"""Conditional nominal research comparison, without inventing a par conversion."""
from dataclasses import replace
from datetime import date
import unittest
from sovereign_macro.config import load_config
from sovereign_macro.models import Observation
from sovereign_macro.pipeline import demo_bundle, evaluate

DAY=date(2026,10,6)


class SlovakResearchComparisonTests(unittest.TestCase):
    def setUp(self):
        self.config=load_config()
        self.country=next(c for c in self.config['countries']['countries'] if c['iso3']=='SVK')

    def row(self, changes=None):
        bundle=demo_bundle(self.config,DAY)
        obs=replace(bundle['yields']['SVK:5'],provider='slovakia',value=3.87,series='ZCY5Y')
        bundle['yields']['SVK:5']=replace(obs,**(changes or {}))
        return next(r for r in evaluate(self.config,bundle,DAY)['rows'] if r['iso3']=='SVK')

    def test_raw_zero_rate_is_ranked_only_as_a_disclosed_research_proxy(self):
        row=self.row()
        self.assertTrue(row['usable_baseline'])
        self.assertIsNotNone(row['baseline_rank'])
        self.assertEqual(row['yield_5y'],3.87)
        self.assertEqual(row['yield_type'],'estimated_zero_coupon')
        self.assertIn('BASELINE_DEFINITION_DIFFERENCE',row['warnings'])
        self.assertIn('복리',row['baseline_definition_note'])
        self.assertIn('par',row['baseline_definition_note'])
        self.assertEqual(row['redistribution_status'],'pending')
        self.assertIsNone(row['adjusted'])

    def test_explicit_opt_out_restores_definition_hold(self):
        self.country['yield']['baseline_compatible']=False
        row=self.row()
        self.assertEqual(row['yield_5y'],3.87)
        self.assertFalse(row['usable_baseline'])
        self.assertIsNone(row['baseline_rank'])
        self.assertIn('BASELINE_DEFINITION_UNAPPROVED',row['errors'])

    def test_approval_does_not_override_date_unit_country_currency_or_definition(self):
        for changes in ({'period':'2026-09-28'},{'period':'2026-10-07'},
                        {'metric':'yield_10y'},{'tenor_years':10},{'unit':'bp'},
                        {'currency':'USD'},{'iso3':'CZE'},{'yield_type':'par_constant_maturity'}):
            with self.subTest(changes=changes):
                row=self.row(changes)
                self.assertIsNone(row['yield_5y'])
                self.assertFalse(row['usable_baseline'])
                self.assertIsNone(row['baseline_rank'])

    def test_complete_fixture_opens_only_baseline_and_missing_inputs_still_hold(self):
        # Synthetic fixtures exercise the readiness gate; not a source-data replay.
        bundle=demo_bundle(self.config,DAY)
        for c in self.config['countries']['countries']:
            if not c['yield']['baseline_compatible'] and c['iso3']!='SVK':
                iso=c['iso3'];slug=c['wgb_slug']
                bundle['yields'][iso+':5']=Observation(iso,'yield_5y',4,DAY.isoformat(),c['currency'],
                    provider='wgb',series=slug+':5Y',tenor_years=5,yield_type='annualized_government_yield',
                    url='https://www.worldgovernmentbonds.com/bond-historical-data/'+slug+'/5-years/')
        bundle['yields']['USA:10']=Observation('USA','yield_10y',5,DAY.isoformat(),'USD',
                    provider='treasury',tenor_years=10,yield_type='par_constant_maturity')
        for d,rates in bundle['fx'].items():
            if d<date(2026,1,1): rates['BGN']=1.9558
        good=evaluate(self.config,bundle,DAY)
        self.assertEqual(good['quality']['baseline_usable'],27)
        self.assertTrue(good['quality']['safe_to_use'])
        self.assertEqual(good['quality']['status'],'READY')
        self.assertFalse(good['quality']['safe_to_use_adjusted'])
        self.assertTrue(all(r['adjusted'] is None for r in good['rows']))
        for missing in ('BGN','USA10','fiscal','demo','system_error'):
            from copy import deepcopy
            b=deepcopy(bundle)
            if missing=='BGN':
                for rates in b['fx'].values(): rates.pop('BGN',None)
            elif missing=='USA10': del b['yields']['USA:10']
            elif missing=='fiscal': del b['fiscal']['values']['overall_balance']['SVK'][2028]
            elif missing=='system_error': b['errors']=['FX_FETCH_FAILED']
            r=evaluate(self.config,b,DAY,demo=missing=='demo')
            self.assertFalse(r['quality']['safe_to_use'],missing)

if __name__=='__main__':unittest.main()
