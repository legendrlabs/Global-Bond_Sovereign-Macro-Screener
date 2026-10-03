import unittest
import tempfile
import json
from pathlib import Path
from datetime import date
from sovereign_macro.config import load_config
from sovereign_macro.pipeline import evaluate, demo_bundle
from sovereign_macro.report import publish

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.config=load_config()
        self.day=date(2026,10,3)
    def test_all_rows_and_no_quality_reweight(self):
        result=evaluate(self.config,demo_bundle(self.config,self.day),self.day,demo=True)
        self.assertEqual(len(result['rows']),27)
        self.assertFalse(result['quality']['safe_to_use'])
        self.assertTrue(any(r['baseline'] is not None for r in result['rows']))
        self.assertTrue(all(r['adjusted'] is None for r in result['rows']))
        self.assertTrue(all(r['baseline_rank'] is None for r in result['rows']))
    def test_public_numbers_and_regimes_redacted(self):
        result=evaluate(self.config,demo_bundle(self.config,self.day),self.day,public_output=True)
        self.assertTrue(all(r['baseline'] is None and r['yield_5y'] is None and r['net_debt_current'] is None for r in result['rows']))
        self.assertTrue(all(r['fiscal_trend']=='UNAVAILABLE' for r in result['rows']))
        text=json.dumps(result)
        self.assertNotIn('"value":',text)
    def test_failed_refresh_replaces_current_and_retains_last_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            first=evaluate(self.config,demo_bundle(self.config,self.day),self.day,demo=True)
            # Publisher receives the evaluated completeness flag, not inferred ranks.
            first['quality']['safe_to_use']=True
            first['quality']['status']='READY'
            publish(first,tmp)
            previous=json.loads((Path(tmp)/'last_success.json').read_text())
            failed=evaluate(self.config,{'fiscal':None,'fx':{},'yields':{},'errors':['HTTP_FAILURE']},self.day)
            publish(failed,tmp)
            current=json.loads((Path(tmp)/'current.json').read_text())
            self.assertNotEqual(previous['run_id'],current['run_id'])
            self.assertEqual(previous,json.loads((Path(tmp)/'last_success.json').read_text()))
            quality=json.loads((Path(tmp)/current['path']/'quality.json').read_text())
            self.assertEqual(quality['status'],'DATA_HOLD')
            self.assertEqual(quality['run_id'],current['run_id'])
            self.assertTrue((Path(tmp)/current['path']/'index.html').exists())
    def test_missing_balance_year_blocks_fiscal_score(self):
        bundle=demo_bundle(self.config,self.day)
        del bundle['fiscal']['values']['overall_balance']['CAN'][2028]
        result=evaluate(self.config,bundle,self.day)
        row=next(r for r in result['rows'] if r['iso3']=='CAN')
        self.assertIsNone(row['baseline'])
        self.assertIn('FISCAL_HORIZON_INCOMPLETE',row['errors'])

class ReviewRegressionTests(unittest.TestCase):
    def setUp(self):
        self.config=load_config();self.day=date(2026,10,3)
        for c in self.config['countries']['countries']:
            c['yield']['baseline_compatible']=True
            c['fx_continuity']=True;c['currency_from']='2000-01-01'
    def test_missing_cpi_fx_or_watch_tenor_blocks_global_readiness(self):
        for missing in ('inflation','fx','watch'):
            bundle=demo_bundle(self.config,self.day)
            from sovereign_macro.models import Observation
            bundle['yields']['USA:10']=Observation('USA','yield_10y',5,self.day.isoformat(),'USD',tenor_years=10,yield_type='par_constant_maturity')
            if missing=='inflation': bundle['fiscal']['values']['inflation']={}
            elif missing=='fx': bundle['fx']={}
            else: del bundle['yields']['USA:10']
            result=evaluate(self.config,bundle,self.day)
            self.assertFalse(result['quality']['safe_to_use'],missing)
    def test_mismatched_yield_definition_and_metric_are_unavailable(self):
        from dataclasses import replace
        for changes in ({'yield_type':'zero_coupon'},{'metric':'yield_10y'}):
            bundle=demo_bundle(self.config,self.day)
            bundle['yields']['CAN:5']=replace(bundle['yields']['CAN:5'],**changes)
            row=next(r for r in evaluate(self.config,bundle,self.day)['rows'] if r['iso3']=='CAN')
            self.assertFalse(row['usable_baseline'])
            self.assertIsNone(row['yield_5y'])
    def test_leap_day_preserves_krw_identity(self):
        day=date(2028,2,29)
        row=next(r for r in evaluate(self.config,demo_bundle(self.config,day),day)['rows'] if r['iso3']=='KOR')
        self.assertEqual(row['fx_vol_1y'],0)
    def test_currency_start_blocks_one_year_and_future_currency_assignment(self):
        c=next(c for c in self.config['countries']['countries'] if c['iso3']=='HRV');c['currency_from']='2023-01-01'
        for day in (date(2023,7,1),date(2022,7,1)):
            row=next(r for r in evaluate(self.config,demo_bundle(self.config,day),day)['rows'] if r['iso3']=='HRV')
            self.assertIsNone(row['fx_vol_1y'])
