import unittest
import tempfile
from unittest.mock import patch
import requests
from sovereign_macro.http import HttpClient
from sovereign_macro.models import DataError

class Session:
    def __init__(self,items): self.items=iter(items);self.calls=[]
    def request(self,*args,**kwargs):
        self.calls.append((args,kwargs));item=next(self.items)
        if isinstance(item,Exception): raise item
        return item

def response(code,content=b'{}',headers=None):
    r=requests.Response();r.status_code=code;r._content=content;r.headers.update(headers or {});return r

class HttpTests(unittest.TestCase):
    def test_json_post_can_supply_origin_referer_without_changing_existing_form_posts(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=Session([response(200)])
            client=HttpClient(tmp,s)
            client.fetch('https://example.org/data',method='POST',body='{}',
                         headers={'Origin':'https://example.org','Content-Type':'application/json'})
            self.assertEqual(s.calls[0][1]['headers']['Origin'],'https://example.org')
            self.assertEqual(s.calls[0][1]['headers']['Content-Type'],'application/json')
            self.assertEqual(s.calls[0][1]['data'],'{}')
    def test_retry_and_conditional_hash_revalidation(self):
        with tempfile.TemporaryDirectory() as tmp,patch('sovereign_macro.http.time.sleep'):
            s=Session([response(429),response(200,b'payload',{'ETag':'version'}),response(304)])
            client=HttpClient(tmp,s)
            first=client.fetch('https://example.org/data')
            second=client.fetch('https://example.org/data')
            self.assertEqual(first.sha256,second.sha256)
            self.assertEqual(s.calls[-1][1]['headers']['If-None-Match'],'version')
            self.assertEqual(s.calls[0][1]['timeout'],(5,15))
    def test_timeout_does_not_reuse_cached_success(self):
        with tempfile.TemporaryDirectory() as tmp,patch('sovereign_macro.http.time.sleep'):
            client=HttpClient(tmp,Session([response(200),requests.Timeout(),requests.Timeout()]))
            client.fetch('https://example.org/data')
            with self.assertRaises(DataError): client.fetch('https://example.org/data')
    def test_404_no_retry_and_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=Session([response(404)]);client=HttpClient(tmp,s,budget=1)
            with self.assertRaises(DataError): client.fetch('https://example.org/data')
            self.assertEqual(len(s.calls),1)
            with self.assertRaisesRegex(DataError,'BUDGET'): client.fetch('https://example.org/data')
