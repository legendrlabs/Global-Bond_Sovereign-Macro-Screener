"""Bounded public HTTP transport. A failed refresh never masquerades as current data."""
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import time
import requests
from .models import DataError

@dataclass(frozen=True)
class Payload:
    body: bytes
    url: str
    retrieved_at: str
    sha256: str
    source_date: str = ''
    def json(self):
        return json.loads(self.body)

class HttpClient:
    def __init__(self, cache='data/cache', session=None, budget=80, attempts=2):
        self.cache=Path(cache)
        self.session=session or requests.Session()
        self.budget=budget
        self.attempts=attempts
        self.records=[]

    def fetch(self, url, method='GET', body=None):
        key=hashlib.sha256((method+url+(body or '')).encode()).hexdigest()
        meta_file=self.cache/(key+'.json')
        old={}
        if meta_file.exists():
            try: old=json.loads(meta_file.read_text())
            except (ValueError,OSError): pass
        headers={'User-Agent':'SovereignMacroScreener/0.1 (public statistics research)'}
        if body is not None: headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
        if old.get('etag'): headers['If-None-Match']=old['etag']
        if old.get('last_modified'): headers['If-Modified-Since']=old['last_modified']
        for attempt in range(self.attempts):
            if self.budget<=0: raise DataError('REQUEST_BUDGET_EXHAUSTED')
            self.budget-=1
            try:
                response=self.session.request(method,url,data=body,headers=headers,timeout=(5,15))
                if response.status_code==304:
                    raw=self.cache/(old.get('sha256','')+'.bin')
                    content=raw.read_bytes()
                    if hashlib.sha256(content).hexdigest()!=old.get('sha256'):
                        raise DataError('CACHE_HASH_MISMATCH')
                else:
                    response.raise_for_status()
                    content=response.content
                now=datetime.now(timezone.utc).isoformat()
                sha=hashlib.sha256(content).hexdigest()
                self.cache.mkdir(parents=True,exist_ok=True)
                (self.cache/(sha+'.bin')).write_bytes(content)
                meta={'url':url,'sha256':sha,'retrieved_at':now,
                      'etag':response.headers.get('ETag',old.get('etag','')),
                      'last_modified':response.headers.get('Last-Modified',old.get('last_modified',''))}
                meta_file.write_text(json.dumps(meta),encoding='utf8')
                self.records.append({**meta,'status':response.status_code})
                return Payload(content,url,now,sha,meta['last_modified'])
            except requests.RequestException as exc:
                status=getattr(getattr(exc,'response',None),'status_code',None)
                retryable=status is None or status==429 or status>=500
                self.records.append({'url':url,'status':status,'error':type(exc).__name__})
                if not retryable or attempt+1==self.attempts:
                    raise DataError(f'HTTP_FAILURE:{status or type(exc).__name__}') from exc
                time.sleep(min(2**attempt,4))
        raise DataError('HTTP_FAILURE')
