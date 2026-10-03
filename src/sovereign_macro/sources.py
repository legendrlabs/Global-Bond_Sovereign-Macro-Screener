"""Source-specific parsing; series selection and maturity stay explicit."""
import csv
from datetime import timedelta, date, datetime
from io import StringIO, BytesIO
import re
import time
import zipfile
import xml.etree.ElementTree as ET
from .models import DataError, Observation, finite

def local(tag):
    return tag.rsplit('}',1)[-1]

def numeric(value):
    if value is None or value=='': return None
    try: value=float(value)
    except (TypeError,ValueError): return None
    return value if finite(value) else None

def parse_ecb(body):
    result={}
    for node in ET.fromstring(body).iter():
        if 'time' in node.attrib:
            day=node.attrib['time']
            date.fromisoformat(day)
            rates={child.attrib['currency']:float(child.attrib['rate']) for child in node if 'currency' in child.attrib}
            if any(not finite(v) or v<=0 for v in rates.values()): raise DataError('FX_RATE_CONTRACT')
            if day in result: raise DataError('DUPLICATE_FX_DATE')
            result[day]=rates
    if not result: raise DataError('FX_EMPTY')
    return result

def parse_canada(data,series):
    if series not in data.get('seriesDetail',{}): raise DataError('SERIES_METADATA_MISMATCH')
    label=data['seriesDetail'][series].get('label','').lower().replace('-',' ')
    if not re.search(r'\b5\s*year',label): raise DataError('CANADA_MATURITY_METADATA')
    return [(r['d'],v) for r in data['observations'] if (v:=numeric(r.get(series,{}).get('v'))) is not None]

def parse_riksbank(data):
    if not isinstance(data,list): raise DataError('RIKSBANK_SCHEMA')
    return [(r['date'][:10],v) for r in data if (v:=numeric(r.get('value'))) is not None]

def parse_treasury(body,tenor):
    rows=[]
    for node in ET.fromstring(body).iter():
        if local(node.tag)!='entry': continue
        fields={local(c.tag):c.text for c in node.iter()}
        value=numeric(fields.get(f'BC_{tenor}YEAR'))
        if value is not None and fields.get('NEW_DATE'): rows.append((fields['NEW_DATE'][:10],value))
    return rows

def parse_norway(body,tenor):
    reader=csv.DictReader(StringIO(body.decode('utf-8-sig')),delimiter=';')
    return [(r['TIME_PERIOD'],v) for r in reader if r['TENOR']==f'{tenor}Y' and r['INSTRUMENT_TYPE']=='GBON'
            and r['FREQ']=='B' and (v:=numeric(r['OBS_VALUE'])) is not None]

def parse_rba(body,series):
    rows=list(csv.reader(StringIO(body.decode('utf-8-sig'))))
    header=next((i for i,r in enumerate(rows) if series in r),None)
    if header is None: raise DataError('RBA_SERIES_MISSING')
    col=rows[header].index(series)
    units=next((r for r in rows[:header] if r and r[0]=='Units'),[])
    if len(units)<=col or units[col]!='Per cent per annum': raise DataError('RBA_UNIT_UNVERIFIED')
    result=[]
    for row in rows[header+1:]:
        if len(row)<=col: continue
        try: day=datetime.strptime(row[0],'%d-%b-%Y').date().isoformat()
        except ValueError: continue
        value=numeric(row[col])
        if value is not None: result.append((day,value))
    return result

def parse_japan(body,tenor):
    rows=list(csv.reader(StringIO(body.decode('cp932'))))
    if not rows or '%' not in ','.join(rows[0]): raise DataError('JAPAN_UNIT_UNVERIFIED')
    header=next((i for i,r in enumerate(rows) if f'{tenor}年' in r),None)
    if header is None: raise DataError('JAPAN_TENOR_MISSING')
    col=rows[header].index(f'{tenor}年')
    result=[]
    for row in rows[header+1:]:
        if len(row)<=col: continue
        match=re.fullmatch(r'([SHR])(\d+)\.(\d+)\.(\d+)',row[0].strip())
        if not match: continue
        era,y,m,d=match.groups()
        day=date({'S':1925,'H':1988,'R':2018}[era]+int(y),int(m),int(d))
        value=numeric(row[col])
        if value is not None: result.append((day.isoformat(),value))
    return result

def parse_kofia(body):
    rows=[]
    for node in ET.fromstring(body).iter():
        if local(node.tag)!='BISComDspDatDTO': continue
        fields={local(c.tag):c.text for c in node}
        day=fields.get('val1','') or ''
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',day): continue
        value=numeric(fields.get('val2'))
        if value is not None: rows.append((day,value))
    return rows

def parse_italy(body,series):
    rows=[]
    with zipfile.ZipFile(BytesIO(body)) as archive:
        for name in archive.namelist():
            if not name.endswith('_DATA.csv'): continue
            reader=csv.DictReader(StringIO(archive.read(name).decode('utf-8-sig')),delimiter=';')
            if series not in (reader.fieldnames or []): continue
            for row in reader:
                value=numeric(row[series])
                day=row.get('DATA_OSS','').replace('/','-')
                if value is not None: rows.append((day,value))
    return rows

def parse_belgium(body):
    rows=[]
    for node in ET.fromstring(body).iter():
        if local(node.tag)!='Obs': continue
        fields={local(c.tag):c.attrib for c in node}
        day=fields.get('ObsDimension',{}).get('value') or fields.get('Time',{}).get('value')
        val=fields.get('ObsValue',{}).get('value')
        # Generic SDMX uses Time text, compact SDMX uses attributes.
        if not day:
            day=next((c.text for c in node if local(c.tag)=='Time'),None)
        value=numeric(val)
        if day and value is not None: rows.append((day,value))
    return rows

def select_latest(rows,as_of):
    parsed={}
    for period,value in rows:
        observed=date.fromisoformat(period)
        if observed>as_of: continue
        if period in parsed and parsed[period]!=value: raise DataError('CONFLICTING_DUPLICATE_YIELD')
        parsed[period]=value
    if not parsed: raise DataError('YIELD_EMPTY_AS_OF')
    period=max(parsed)
    return period,parsed[period]

def collect_yield(client,country,as_of,tenor=5):
    route=country['yield']; adapter=route['adapter']; series=route['series']
    if tenor not in (5,10): raise DataError('TENOR_NOT_IMPLEMENTED')
    if tenor!=5 and adapter not in ('norway','treasury','japan'):
        raise DataError('TENOR_NOT_IMPLEMENTED')
    start=(as_of-timedelta(days=21)).isoformat()
    body=None
    if adapter=='canada':
        if tenor!=5: raise DataError('TENOR_NOT_IMPLEMENTED')
        url=f'https://www.bankofcanada.ca/valet/observations/{series}/json?start_date={start}&end_date={as_of}'
        parser=lambda p:parse_canada(p.json(),series)
    elif adapter=='norway':
        url=f'https://data.norges-bank.no/api/data/GOVT_GENERIC_RATES/?startPeriod={start}&format=csv'
        parser=lambda p:parse_norway(p.body,tenor)
    elif adapter=='riksbank':
        if not hasattr(client,'riksbank_series'):
            meta=client.fetch('https://api.riksbank.se/swea/v1/Series').json()
            client.riksbank_series={r['seriesId']:r for r in meta}
        metadata=client.riksbank_series.get(series,{})
        if 'maturity 5 years' not in metadata.get('longDescription','') or metadata.get('seriesClosed') is not False:
            raise DataError('RIKSBANK_SERIES_METADATA')
        if tenor!=5: raise DataError('TENOR_NOT_IMPLEMENTED')
        elapsed=time.monotonic()-getattr(client,'riksbank_last_request',0)
        if elapsed<1: time.sleep(1-elapsed)
        client.riksbank_last_request=time.monotonic()
        url=f'https://api.riksbank.se/swea/v1/Observations/{series}/{start}/{as_of}'
        parser=lambda p:parse_riksbank(p.json())
    elif adapter=='rba':
        url='https://www.rba.gov.au/statistics/tables/csv/f2-data.csv'
        parser=lambda p:parse_rba(p.body,series)
    elif adapter=='treasury':
        url=f'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value={as_of.year}'
        series=f'BC_{tenor}YEAR'
        parser=lambda p:parse_treasury(p.body,tenor)
    elif adapter=='japan':
        url='https://www.mof.go.jp/jgbs/reference/interest_rate/jgbcm.csv'
        series=f'{tenor}年'
        parser=lambda p:parse_japan(p.body,tenor)
    elif adapter=='kofia':
        url='https://www.kofiabond.or.kr/proframeWeb/XMLSERVICES/'
        body=f'<message><proframeHeader><pfmAppName>BIS-KOFIABOND</pfmAppName><pfmSvcName>BISLastAskPrcROPSrchSO</pfmSvcName><pfmFnName>listTrm</pfmFnName></proframeHeader><systemHeader/><BISComDspDatDTO><val1>DD</val1><val2>{start.replace("-","")}</val2><val3>{as_of.isoformat().replace("-","")}</val3><val4>1530</val4><val5>{series}</val5></BISComDspDatDTO></message>'
        parser=lambda p:parse_kofia(p.body)
    elif adapter=='italy':
        url='https://a2a.bancaditalia.it/infostat/dataservices/export/EN/CSV/ALL/CUBE/BANKITALIA/DIFF/BMK0200'
        parser=lambda p:parse_italy(p.body,series)
    elif adapter=='belgium':
        url=f'https://nsidisseminate-stat.nbb.be/rest/data/BE2,DF_IROLOBE2,1.0/D.5Y.F?startPeriod={start}'
        parser=lambda p:parse_belgium(p.body)
    else: raise DataError(route.get('reason','ADAPTER_UNAVAILABLE'))
    p=client.fetch(url,method='POST' if body else 'GET',body=body)
    period,value=select_latest(parser(p),as_of)
    return Observation(country['iso3'],f'yield_{tenor}y',value,period,country['currency'],
                       unit='unverified' if adapter=='belgium' else 'percent',
                       provider=adapter,dataset=adapter,series=series,source_date=p.source_date,
                       retrieved_at=p.retrieved_at,url=p.url,raw_sha256=p.sha256,
                       tenor_years=tenor,yield_type=route['yield_type'],redistribution=route['redistribution'])
