"""Fiscal-only reuse must preserve source dates and fail closed on invalid evidence."""
import hashlib
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from sovereign_macro.fiscal import collect_fiscal, METRICS
from sovereign_macro.http import Payload
from sovereign_macro.models import DataError

BASE='https://www.imf.org/external/datamapper/api/v2/'
DAY=date(2026,10,5)
STAMP='2026-10-05T00:41:23+00:00'
COUNTRIES=[{'iso3':'CAN','pdf_label':'Canada'}]

def fixture(edition='April 2026'):
    meta={key:dict(source=('World Economic Outlook' if metric=='inflation' else 'Fiscal Monitor')+' ('+edition+')',
                   unit='Annual percent change' if metric=='inflation' else '% of GDP',
                   **{'projection-year':2026,'last-modified':'2026-04-15 00:00:00'})
          for metric,key in METRICS.items()}
    data={BASE+'indicators':{'indicators':meta}}
    for metric,key in METRICS.items():
        number={'net_debt':42.,'gross_debt':64.,'overall_balance':-2.,'inflation':2.5}[metric]
        data[BASE+key]={'indicators':{key:meta[key]},'values':{key:{'CAN':{str(y):number for y in range(2026,2032)}}}}
    return data

class Client:
    def __init__(self,cache,data=None,error=None):
        self.cache=Path(cache);self.data=fixture() if data is None else data
        self.error=error;self.records=[]
    def fetch(self,url):
        if self.error: raise DataError(self.error)
        raw=json.dumps(self.data[url]).encode()
        return Payload(raw,url,STAMP,hashlib.sha256(raw).hexdigest())

class FiscalSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.config={'api':BASE,'redistribution':'pending','snapshot_enabled':True,'snapshot_max_age_days':210}
    def collect(self,client,day=DAY,config=None):
        return collect_fiscal(client,config or self.config,COUNTRIES,day)
    def prime(self):
        return self.collect(Client(self.tmp.name))
    def offline(self,day=DAY,config=None):
        return self.collect(Client(self.tmp.name,error='HTTP_FAILURE:ReadTimeout'),day,config)
    def test_network_failure_reuses_validated_values_without_refreshing_source_time(self):
        first=self.prime();cached=self.offline()
        self.assertEqual(cached['values']['net_debt']['CAN'][2026],42.)
        self.assertEqual(cached['edition'],'April 2026')
        self.assertTrue(cached['snapshot']['used'])
        self.assertEqual(cached['snapshot']['original_retrieved_at'],STAMP)
        self.assertEqual(cached['provenance']['net_debt']['retrieved_at'],first['provenance']['net_debt']['retrieved_at'])
        self.assertEqual(cached['errors'],[])
        self.assertIn('FISCAL_SNAPSHOT_USED',cached['warnings'])
    def test_valid_live_refresh_takes_precedence_over_saved_snapshot(self):
        self.prime();data=fixture();key=METRICS['net_debt'];data[BASE+key]['values'][key]['CAN']['2026']=43.
        live=self.collect(Client(self.tmp.name,data))
        self.assertEqual(live['values']['net_debt']['CAN'][2026],43.)
        self.assertFalse(live['snapshot']['used'])
        self.assertEqual(self.offline()['values']['net_debt']['CAN'][2026],43.)
    def test_no_snapshot_keeps_network_failure(self):
        with self.assertRaisesRegex(DataError,'HTTP_FAILURE'): self.offline()
    def test_disabled_reuse_does_not_use_saved_values(self):
        self.prime()
        with self.assertRaisesRegex(DataError,'HTTP_FAILURE'):
            self.offline(config={**self.config,'snapshot_enabled':False})
    def test_expired_snapshot_and_forecast_year_rollover_are_rejected(self):
        self.prime()
        for day,settings in [(date(2026,10,7),{'snapshot_max_age_days':1}),(date(2027,1,1),{})]:
            with self.subTest(day=day),self.assertRaisesRegex(DataError,'SNAPSHOT'):
                self.offline(day,config={**self.config,**settings})
    def test_future_retrieval_is_rejected(self):
        self.prime()
        with self.assertRaisesRegex(DataError,'SNAPSHOT'): self.offline(date(2026,10,4))
    def test_corrupt_raw_response_is_not_used(self):
        self.prime()
        paths=list(Path(self.tmp.name).rglob('*.bin'))
        self.assertTrue(paths)
        for p in paths: p.write_bytes(b'tampered')
        with self.assertRaisesRegex(DataError,'SNAPSHOT'): self.offline()
    def test_new_edition_seen_during_partial_refresh_blocks_old_edition(self):
        self.prime()
        class Partial(Client):
            def fetch(self,url):
                if url!=BASE+'indicators': raise DataError('HTTP_FAILURE:ReadTimeout')
                return super().fetch(url)
        with self.assertRaisesRegex(DataError,'EDITION'):
            self.collect(Partial(self.tmp.name,fixture('October 2026')))
    def test_invalid_live_units_are_not_hidden_by_old_snapshot(self):
        self.prime();data=fixture();data[BASE+'indicators']['indicators'][METRICS['net_debt']]['unit']='ratio'
        with self.assertRaises(DataError): self.collect(Client(self.tmp.name,data))
    def test_source_scope_change_cannot_inherit_snapshot(self):
        self.prime()
        with self.assertRaisesRegex(DataError,'SNAPSHOT'):
            self.offline(config={**self.config,'api':'https://other.example/api/'})
    def test_legacy_http_cache_can_be_validated_and_promoted_without_network(self):
        client=Client(self.tmp.name)
        for url in fixture():
            p=client.fetch(url);root=Path(self.tmp.name)
            (root/(p.sha256+'.bin')).write_bytes(p.body)
            (root/(hashlib.sha256(url.encode()).hexdigest()+'.json')).write_text(json.dumps(
                {'url':url,'sha256':p.sha256,'retrieved_at':p.retrieved_at,'last_modified':''}))
        cached=self.offline()
        self.assertTrue(cached['snapshot']['used'])
        self.assertEqual(cached['values']['inflation']['CAN'][2031],2.5)
        self.assertTrue(list(Path(self.tmp.name).glob('fiscal-snapshots/*.json')))
    def test_legacy_mixed_series_editions_cannot_be_promoted(self):
        data=fixture();key=METRICS['inflation'];data[BASE+key]['indicators'][key]['source']='World Economic Outlook (October 2026)'
        client=Client(self.tmp.name,data)
        for url in data:
            p=client.fetch(url);root=Path(self.tmp.name)
            (root/(p.sha256+'.bin')).write_bytes(p.body)
            (root/(hashlib.sha256(url.encode()).hexdigest()+'.json')).write_text(json.dumps(
                {'url':url,'sha256':p.sha256,'retrieved_at':p.retrieved_at}))
        with self.assertRaisesRegex(DataError,'SNAPSHOT'): self.offline()

class FiscalDisclosureTests(unittest.TestCase):
    def test_saved_edition_is_visible_in_report_without_global_failure(self):
        from sovereign_macro.config import load_config
        from sovereign_macro.pipeline import demo_bundle, evaluate
        from sovereign_macro.summary import build_executive_summary, render_summary_markdown
        config=load_config();bundle=demo_bundle(config,DAY)
        bundle['fiscal']['edition']='April 2026'
        bundle['fiscal']['warnings']=['FISCAL_SNAPSHOT_USED']
        bundle['fiscal']['snapshot']=dict(used=True,edition='April 2026',original_retrieved_at=STAMP,
            last_retrieved_at=STAMP,validated_at=STAMP,age_days=0,
            refresh_failure='HTTP_FAILURE:ReadTimeout',latest_release_verified=False)
        result=evaluate(config,bundle,DAY)
        self.assertTrue(result['fiscal_source']['used'])
        self.assertEqual(result['fiscal_source']['original_retrieved_at'],STAMP)
        self.assertIn('FISCAL_SNAPSHOT_USED',result['quality']['warnings'])
        self.assertNotIn('FISCAL_SNAPSHOT_USED',result['quality']['system_errors'])
        self.assertTrue(all('FISCAL_SNAPSHOT_USED' in r['warnings'] for r in result['rows']))
        text=render_summary_markdown(build_executive_summary(result))
        self.assertIn('April 2026',text);self.assertIn(STAMP,text)
        self.assertIn('HTTP_FAILURE:ReadTimeout',text)
    def test_public_mode_still_redacts_cached_fiscal_numbers(self):
        from sovereign_macro.config import load_config
        from sovereign_macro.pipeline import demo_bundle, evaluate
        config=load_config();bundle=demo_bundle(config,DAY)
        bundle['fiscal']['snapshot']={'used':True,'edition':'April 2026','original_retrieved_at':STAMP}
        result=evaluate(config,bundle,DAY,public_output=True)
        self.assertTrue(all(r['net_debt_current'] is None and r['inflation_mean'] is None for r in result['rows']))
        self.assertEqual(result['fiscal_source']['original_retrieved_at'],STAMP)

class PdfSnapshotTests(unittest.TestCase):
    def test_pdf_timeout_reuses_complete_edition_and_keeps_saved_pdf(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        pdf_url='https://www.imf.org/fiscal-monitor/april2026.pdf'
        cfg=dict(api=BASE,redistribution='pending',snapshot_enabled=True,
                 pdf_editions={'April 2026':dict(url=pdf_url,page=1,table='Table A8.')})
        countries=COUNTRIES+[{'iso3':'NZL','pdf_label':'New Zealand'}]
        text='April 2026\nTable A8. General Government Net Debt\n'+' '.join(str(y) for y in range(2017,2032))+'\nCanada '+ ' '.join(['42']*15)+'\nNew Zealand '+ ' '.join(['43']*15)
        reader=SimpleNamespace(pages=[SimpleNamespace(extract_text=lambda **kw:text)])
        class PdfClient(Client):
            fail_pdf=False
            def fetch(self,url):
                if url==pdf_url:
                    if self.fail_pdf: raise DataError('HTTP_FAILURE:ReadTimeout')
                    raw=b'PDF fixture bytes'
                    return Payload(raw,url,STAMP,hashlib.sha256(raw).hexdigest())
                return super().fetch(url)
        with tempfile.TemporaryDirectory() as root,patch('sovereign_macro.fiscal.PdfReader',return_value=reader):
            first=collect_fiscal(PdfClient(root),cfg,countries,DAY)
            self.assertEqual(first['values']['net_debt']['NZL'][2026],43.)
            client=PdfClient(root);client.fail_pdf=True
            recovered=collect_fiscal(client,cfg,countries,DAY)
            self.assertEqual(recovered['values']['net_debt']['NZL'][2026],43.)
            self.assertTrue(recovered['snapshot']['used'])
            self.assertEqual(recovered['errors'],[])
            offline=collect_fiscal(Client(root,error='HTTP_FAILURE:ReadTimeout'),cfg,countries,DAY)
            self.assertEqual(offline['values']['net_debt']['NZL'][2031],43.)
    def test_first_pdf_timeout_retains_valid_partial_api_data(self):
        from unittest.mock import patch
        cfg=dict(api=BASE,redistribution='pending',snapshot_enabled=True,
            pdf_editions={'April 2026':dict(url=BASE+'pdf',page=1,table='Table A8.')})
        class PdfFail(Client):
            def fetch(self,url):
                if url==BASE+'pdf': raise DataError('HTTP_FAILURE:ReadTimeout')
                return super().fetch(url)
        with tempfile.TemporaryDirectory() as root:
            result=collect_fiscal(PdfFail(root),cfg,COUNTRIES+[{'iso3':'NZL','pdf_label':'New Zealand'}],DAY)
            self.assertEqual(result['values']['net_debt']['CAN'][2026],42.)
            self.assertFalse(result['snapshot']['used'])
            self.assertIn('PDF_FALLBACK_FAILED:HTTP_FAILURE:ReadTimeout',result['errors'])

class LegacyOptionalPdfTests(unittest.TestCase):
    def test_unneeded_old_pdf_does_not_block_same_edition_api_recovery(self):
        pdf='https://www.imf.org/fiscal-monitor/april2026.pdf'
        config=dict(api=BASE,redistribution='pending',snapshot_enabled=True,
            pdf_editions={'April 2026':dict(url=pdf,page=1,table='Table A8.')})
        with tempfile.TemporaryDirectory() as root:
            client=Client(root)
            for url in fixture():
                p=client.fetch(url)
                (Path(root)/(p.sha256+'.bin')).write_bytes(p.body)
                (Path(root)/(hashlib.sha256(url.encode()).hexdigest()+'.json')).write_text(json.dumps(
                    {'url':url,'sha256':p.sha256,'retrieved_at':p.retrieved_at}))
            raw=b'Unneeded PDF';sha=hashlib.sha256(raw).hexdigest()
            (Path(root)/(sha+'.bin')).write_bytes(raw)
            (Path(root)/'old-pdf.json').write_text(json.dumps(
                {'url':pdf,'sha256':sha,'retrieved_at':'2026-10-01T00:00:00+00:00'}))
            result=collect_fiscal(Client(root,error='HTTP_FAILURE:ReadTimeout'),config,COUNTRIES,DAY)
            self.assertEqual(result['values']['net_debt']['CAN'][2026],42.)
            self.assertTrue(result['snapshot']['used'])
            self.assertEqual(result['snapshot']['original_retrieved_at'],STAMP)

    def test_unneeded_corrupt_pdf_is_not_a_required_source(self):
        config=dict(api=BASE,redistribution='pending',snapshot_enabled=True,
            pdf_editions={'April 2026':dict(url=BASE+'unused-pdf',page=1,table='Table A8.')})
        with tempfile.TemporaryDirectory() as root:
            client=Client(root)
            for url in fixture():
                p=client.fetch(url)
                (Path(root)/(p.sha256+'.bin')).write_bytes(p.body)
                (Path(root)/(hashlib.sha256(url.encode()).hexdigest()+'.json')).write_text(json.dumps(
                    {'url':url,'sha256':p.sha256,'retrieved_at':p.retrieved_at}))
            (Path(root)/'unneeded-pdf.json').write_text(json.dumps(
                {'url':BASE+'unused-pdf','sha256':'a'*64,'retrieved_at':STAMP}))
            result=collect_fiscal(Client(root,error='HTTP_FAILURE:ReadTimeout'),config,COUNTRIES,DAY)
            self.assertEqual(result['values']['net_debt']['CAN'][2026],42.)

class EditionContinuityTests(unittest.TestCase):
    def test_new_edition_observation_survives_next_run_network_outage(self):
        cfg=dict(api=BASE,redistribution='pending',snapshot_enabled=True)
        class Partial(Client):
            def fetch(self,url):
                if url!=BASE+'indicators': raise DataError('HTTP_FAILURE:ReadTimeout')
                return super().fetch(url)
        with tempfile.TemporaryDirectory() as root:
            collect_fiscal(Client(root),cfg,COUNTRIES,DAY)
            with self.assertRaisesRegex(DataError,'EDITION'):
                collect_fiscal(Partial(root,fixture('October 2026')),cfg,COUNTRIES,DAY)
            with self.assertRaisesRegex(DataError,'EDITION'):
                collect_fiscal(Client(root,error='HTTP_FAILURE:ReadTimeout'),cfg,COUNTRIES,DAY)
    def test_same_edition_revision_observation_survives_next_run_outage(self):
        cfg=dict(api=BASE,redistribution='pending',snapshot_enabled=True)
        data=fixture();data[BASE+'indicators']['indicators'][METRICS['net_debt']]['last-modified']='2026-10-05 01:00:00'
        class Partial(Client):
            def fetch(self,url):
                if url!=BASE+'indicators': raise DataError('HTTP_FAILURE:ReadTimeout')
                return super().fetch(url)
        with tempfile.TemporaryDirectory() as root:
            collect_fiscal(Client(root),cfg,COUNTRIES,DAY)
            with self.assertRaises(DataError): collect_fiscal(Partial(root,data),cfg,COUNTRIES,DAY)
            with self.assertRaisesRegex(DataError,'REVISION'):
                collect_fiscal(Client(root,error='HTTP_FAILURE:ReadTimeout'),cfg,COUNTRIES,DAY)
