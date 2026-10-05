"""Explicit IMF edition reuse, separate from generic HTTP freshness semantics."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import uuid
from .fiscal import METRICS
from .http import Payload
from .models import DataError


class Capture:
    def __init__(self,client):
        self.client=client
        self.payloads={}

    def fetch(self,url):
        p=self.client.fetch(url)
        if p.url!=url: raise DataError('FISCAL_SOURCE_URL_MISMATCH')
        self.payloads[url]=p
        return p


class Replay:
    def __init__(self,payloads):
        self.payloads=payloads
        self.used={}

    def fetch(self,url):
        if url not in self.payloads: raise DataError('FISCAL_SNAPSHOT_RESPONSE_MISSING')
        self.used[url]=self.payloads[url]
        return self.payloads[url]


def scope(config,countries):
    return {'api':config['api'],'pdf_editions':config.get('pdf_editions',{}),
            'countries':sorted((c['iso3'],c['pdf_label']) for c in countries)}


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()


def timestamp(value):
    t=datetime.fromisoformat(value)
    if t.tzinfo is None: raise DataError('FISCAL_SNAPSHOT_TIMESTAMP')
    return t.astimezone(timezone.utc)


def validate_times(payloads,config,as_of):
    times=[timestamp(p.retrieved_at) for p in payloads.values()]
    if not times or any(t.date()>as_of for t in times): raise DataError('FISCAL_SNAPSHOT_FUTURE')
    if (as_of-min(times).date()).days>config.get('snapshot_max_age_days',210):
        raise DataError('FISCAL_SNAPSHOT_EXPIRED')
    # A legacy cache may contain individually valid responses from different
    # refreshes. Require one collection cohort as well as per-series metadata.
    if (max(times)-min(times)).total_seconds()>86400:
        raise DataError('FISCAL_SNAPSHOT_MIXED_RETRIEVALS')


def payload_from_record(record,root):
    sha=record['sha256']
    if not re.fullmatch('[0-9a-f]{64}',sha): raise DataError('FISCAL_SNAPSHOT_HASH')
    raw=(root/(sha+'.bin')).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha: raise DataError('FISCAL_SNAPSHOT_HASH')
    return Payload(raw,record['url'],record['retrieved_at'],sha,record.get('source_date',record.get('last_modified','')))


def save(root,config,countries,data,payloads):
    raw=root/'raw';raw.mkdir(parents=True,exist_ok=True)
    entries=[]
    for url,p in payloads.items():
        if p.url!=url or hashlib.sha256(p.body).hexdigest()!=p.sha256:
            raise DataError('FISCAL_SNAPSHOT_HASH')
        (raw/(p.sha256+'.bin')).write_bytes(p.body)
        entries.append(dict(url=url,sha256=p.sha256,retrieved_at=p.retrieved_at,source_date=p.source_date))
    doc=dict(schema=1,scope=scope(config,countries),edition=data['edition'],
             validated_at=datetime.now(timezone.utc).isoformat(),responses=entries)
    wrapper=dict(document=doc,sha256=hashlib.sha256(canonical(doc)).hexdigest())
    path=root/'latest.json';temp=root/('latest.tmp-'+uuid.uuid4().hex)
    try:
        temp.write_bytes(canonical(wrapper))
        os.replace(temp,path)
    finally: temp.unlink(missing_ok=True)
    return doc['validated_at']


def load(root,config,countries):
    wrapper=json.loads((root/'latest.json').read_bytes());doc=wrapper['document']
    if hashlib.sha256(canonical(doc)).hexdigest()!=wrapper['sha256']:
        raise DataError('FISCAL_SNAPSHOT_MANIFEST_HASH')
    if doc['schema']!=1 or canonical(doc['scope'])!=canonical(scope(config,countries)):
        raise DataError('FISCAL_SNAPSHOT_SCOPE_MISMATCH')
    payloads={}
    for record in doc['responses']:
        if record['url'] in payloads: raise DataError('FISCAL_SNAPSHOT_DUPLICATE_URL')
        payloads[record['url']]=payload_from_record(record,root/'raw')
    return payloads,doc


def legacy(cache,config,countries):
    urls={config['api']+'indicators',*(config['api']+k for k in METRICS.values())}
    pdf_urls={p['url'] for p in config.get('pdf_editions',{}).values()}
    records={}
    optional=[]
    for path in cache.glob('*.json'):
        try: record=json.loads(path.read_bytes())
        except (ValueError,OSError): continue
        url=record.get('url')
        if url in pdf_urls:
            optional.append(record)
            continue
        if url not in urls: continue
        if url not in records or timestamp(record['retrieved_at'])>timestamp(records[url]['retrieved_at']):
            records[url]=record
    if not records: raise DataError('FISCAL_SNAPSHOT_NOT_FOUND')
    payloads={url:payload_from_record(record,cache) for url,record in records.items()}
    net_key=METRICS['net_debt']
    net=payloads[config['api']+net_key].json().get('values',{}).get(net_key,{})
    if any(not net.get(c['iso3']) for c in countries):
        source=payloads[config['api']+'indicators'].json()['indicators'][net_key]['source']
        match=re.search(r'\((April|October) (\d{4})\)',source)
        pdf=config.get('pdf_editions',{}).get(' '.join(match.groups()) if match else '')
        candidates=[r for r in optional if pdf and r['url']==pdf['url']]
        if candidates:
            record=max(candidates,key=lambda r:timestamp(r['retrieved_at']))
            payloads[record['url']]=payload_from_record(record,cache)
    return payloads


def validate_seen_metadata(seen,saved,base):
    url=base+'indicators'
    if url not in seen: return
    new=seen[url].json()['indicators'];old=saved[url].json()['indicators']
    for key in METRICS.values():
        for field in ('source','unit','projection-year','last-modified'):
            if new.get(key,{}).get(field)!=old.get(key,{}).get(field):
                raise DataError('FISCAL_SNAPSHOT_EDITION_OR_REVISION_CHANGED')


def observed_metadata(root,seen,base):
    """Keep catalogue evidence even when the remaining API calls fail."""
    url=base+'indicators';path=root/'observed-indicators.json'
    if url in seen:
        p=seen[url]
        if p.url!=url or hashlib.sha256(p.body).hexdigest()!=p.sha256:
            raise DataError('FISCAL_SNAPSHOT_HASH')
        raw=root/'raw';raw.mkdir(parents=True,exist_ok=True)
        (raw/(p.sha256+'.bin')).write_bytes(p.body)
        record=dict(url=url,sha256=p.sha256,retrieved_at=p.retrieved_at,source_date=p.source_date)
        temp=root/('observed.tmp-'+uuid.uuid4().hex)
        try:
            temp.write_bytes(canonical(record))
            os.replace(temp,path)
        finally: temp.unlink(missing_ok=True)
        return {url:p}
    if not path.exists(): return {}
    record=json.loads(path.read_bytes())
    if record['url']!=url: raise DataError('FISCAL_SNAPSHOT_SCOPE_MISMATCH')
    return {url:payload_from_record(record,root/'raw')}


def disclosure(data,payloads,used,validated_at,reason='',as_of=None):
    first=min(timestamp(p.retrieved_at) for p in payloads.values()).isoformat()
    last=max(timestamp(p.retrieved_at) for p in payloads.values()).isoformat()
    data['snapshot']=dict(used=used,edition=data['edition'],original_retrieved_at=first,
                          last_retrieved_at=last,validated_at=validated_at,
                          age_days=(as_of-datetime.fromisoformat(first).date()).days,
                          refresh_failure=reason,latest_release_verified=not used)
    data['warnings']=list(data.get('warnings',[]))
    if used: data['warnings'].append('FISCAL_SNAPSHOT_USED')
    for p in data.get('provenance',{}).values():
        p['snapshot_used']=used
    if data.get('pdf_provenance'): data['pdf_provenance']['snapshot_used']=used
    return data


def collect_with_snapshot(client,config,countries,as_of,collector):
    enabled=config.get('snapshot_enabled',True) and hasattr(client,'cache')
    root=Path(client.cache)/'fiscal-snapshots' if enabled else None
    capture=Capture(client)
    partial=None
    try:
        data=collector(capture,config,countries,as_of)
        pdf_failure=next((e for e in data.get('errors',[]) if e.startswith('PDF_FALLBACK_FAILED:HTTP_FAILURE:')),None)
        if pdf_failure and enabled:
            partial=data
            raise DataError(pdf_failure.removeprefix('PDF_FALLBACK_FAILED:'))
    except DataError as exc:
        # Data/edition validation failures are not transient connection failures.
        if not enabled or not str(exc).startswith('HTTP_FAILURE:'): raise
        try:
            known=observed_metadata(root,capture.payloads,config['api'])
            doc=None
            if (root/'latest.json').exists(): payloads,doc=load(root,config,countries)
            else: payloads=legacy(Path(client.cache),config,countries)
            validate_seen_metadata(known,payloads,config['api'])
            replay=Replay(payloads)
            data=collector(replay,config,countries,as_of)
            payloads=replay.used
            validate_times(payloads,config,as_of)
            if partial and data.get('errors'):
                raise DataError('FISCAL_SNAPSHOT_PDF_RECOVERY_INCOMPLETE')
            if data['horizon_start']!=as_of.year: raise DataError('FISCAL_SNAPSHOT_YEAR_ROLLOVER')
            if doc and doc['edition']!=data['edition']: raise DataError('FISCAL_SNAPSHOT_EDITION_MISMATCH')
            validated_at=doc['validated_at'] if doc else save(root,config,countries,data,payloads)
        except (DataError,ValueError,KeyError,TypeError,OSError) as cached_exc:
            if partial is not None:
                # Keep validated API cells if PDF recovery is unavailable. A
                # failed PDF refresh must not replace a complete saved edition.
                partial.setdefault('warnings',[]).append('FISCAL_SNAPSHOT_UNAVAILABLE:'+str(cached_exc))
                # `observed_metadata` already persists a newer catalogue. Do
                # not replace the complete snapshot with these partial cells.
                return disclosure(partial,capture.payloads,False,
                                  datetime.now(timezone.utc).isoformat(),as_of=as_of)
            raise DataError(str(exc)+';FISCAL_SNAPSHOT_UNAVAILABLE:'+str(cached_exc)) from cached_exc
        return disclosure(data,payloads,True,validated_at,str(exc),as_of)
    validated_at=datetime.now(timezone.utc).isoformat()
    if enabled:
        try:
            validate_times(capture.payloads,config,as_of)
            validated_at=save(root,config,countries,data,capture.payloads)
            observed_metadata(root,capture.payloads,config['api'])
        except (DataError,OSError,ValueError) as exc:
            data.setdefault('warnings',[]).append('FISCAL_SNAPSHOT_SAVE_FAILED:'+str(exc))
    return disclosure(data,capture.payloads,False,validated_at,as_of=as_of)
