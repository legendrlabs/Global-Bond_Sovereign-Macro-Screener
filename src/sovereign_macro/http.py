"""Bounded public HTTP transport. A failed refresh never masquerades as current data."""
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import time
import requests
from urllib.parse import urlparse
from .models import DataError

try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None

IMF_HOSTS = {'imf.org', 'www.imf.org'}
LIQUIDITY_HOSTS = {'markets.newyorkfed.org', 'www.jsda.or.jp'}
DEFAULT_TIMEOUT = (5, 15)
IMF_TIMEOUT = (10, 30)
LIQUIDITY_TIMEOUT = 20

@dataclass(frozen=True)
class Payload:
    body: bytes
    url: str
    retrieved_at: str
    sha256: str
    source_date: str = ''
    transport: str = 'requests'
    def json(self):
        return json.loads(self.body)

class HttpClient:
    def __init__(self, cache='data/cache', session=None, budget=80, attempts=2, imf_transport=None, browser_transport=None):
        self.cache=Path(cache)
        self.session=session or requests.Session()
        self.browser_transport=browser_transport
        if self.browser_transport is None and session is None and cffi_requests is not None:
            self.browser_transport=cffi_requests.request
        self.imf_transport=imf_transport if imf_transport is not None else self.browser_transport
        self.budget=budget
        self.attempts=attempts
        self.records=[]

    @staticmethod
    def _is_imf(url):
        return (urlparse(url).hostname or '').lower() in IMF_HOSTS

    def _request(self, method, url, body, headers):
        host=(urlparse(url).hostname or '').lower()
        timeout=IMF_TIMEOUT if self._is_imf(url) else LIQUIDITY_TIMEOUT if host in LIQUIDITY_HOSTS else DEFAULT_TIMEOUT
        transport=self.imf_transport if self._is_imf(url) else self.browser_transport if host in LIQUIDITY_HOSTS else None
        if transport is not None:
            try:
                response=transport(method=method,url=url,data=body,headers=headers,
                                             timeout=timeout,impersonate='chrome')
                if response.status_code < 400 or response.status_code == 304:
                    return response, 'curl_cffi'
                self.records.append({'url':url,'status':response.status_code,'transport':'curl_cffi'})
            except Exception as exc:
                self.records.append({'url':url,'status':None,'transport':'curl_cffi','error':type(exc).__name__})
        return self.session.request(method,url,data=body,headers=headers,timeout=timeout), 'requests'

    def fetch(self, url, method='GET', body=None, headers=None):
        extra_headers=dict(headers or {})
        key=hashlib.sha256((method+url+(body or '')+json.dumps(extra_headers,sort_keys=True)).encode()).hexdigest()
        meta_file=self.cache/(key+'.json')
        old={}
        if meta_file.exists():
            try: old=json.loads(meta_file.read_text())
            except (ValueError,OSError): pass
        headers={'User-Agent':'SovereignMacroScreener/0.1 (public statistics research)'}
        if body is not None: headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
        headers.update(extra_headers)
        if old.get('etag'): headers['If-None-Match']=old['etag']
        if old.get('last_modified'): headers['If-Modified-Since']=old['last_modified']
        for attempt in range(self.attempts):
            if self.budget<=0: raise DataError('REQUEST_BUDGET_EXHAUSTED')
            self.budget-=1
            try:
                response,transport=self._request(method,url,body,headers)
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
                meta={'url':response.url or url,'sha256':sha,'retrieved_at':now,
                      'etag':response.headers.get('ETag',old.get('etag','')),
                      'last_modified':response.headers.get('Last-Modified',old.get('last_modified','')),
                      'transport':transport}
                meta_file.write_text(json.dumps(meta),encoding='utf8')
                self.records.append({**meta,'status':response.status_code})
                return Payload(content,meta['url'],now,sha,meta['last_modified'],transport)
            except requests.RequestException as exc:
                status=getattr(getattr(exc,'response',None),'status_code',None)
                retryable=status is None or status==429 or status>=500
                self.records.append({'url':url,'status':status,'error':type(exc).__name__})
                if not retryable or attempt+1==self.attempts:
                    raise DataError(f'HTTP_FAILURE:{status or type(exc).__name__}') from exc
                time.sleep(min(2**attempt,4))
        raise DataError('HTTP_FAILURE')
