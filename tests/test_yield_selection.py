from copy import deepcopy
from dataclasses import replace
from datetime import date
import json
import unittest
from unittest.mock import patch

from sovereign_macro.config import load_config
from sovereign_macro.http import Payload
from sovereign_macro.models import DataError, Observation
from sovereign_macro.pipeline import demo_bundle, evaluate
from sovereign_macro.report import build_html
from sovereign_macro.summary import build_executive_summary, render_summary_text


class YieldSelectionTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(); self.day = date(2026,10,5)
        self.c = next(c for c in self.config['countries']['countries'] if c['iso3']=='CAN')
        self.official = Observation('CAN','yield_5y',3.1,'2026-10-02','CAD',
            provider='canada', tenor_years=5, yield_type=self.c['yield']['yield_type'])
        self.fallback = replace(self.official, provider='wgb', value=3.2,
            yield_type='annualized_government_yield', series='canada:5Y',
            url='https://www.worldgovernmentbonds.com/bond-historical-data/canada/5-years/',
            notes=json.dumps({'warnings':['WGB_DATE_DISCREPANCY'],'curve_yield':3.2}))

    def selected(self, official=None, fallback=None, official_error=None, tenor=5):
        from sovereign_macro.yield_selection import collect_preferred_yield
        with patch('sovereign_macro.yield_selection.collect_yield',
                   return_value=official or self.official, side_effect=official_error), \
             patch('sovereign_macro.yield_selection.collect_wgb', return_value=fallback or self.fallback) as wgb:
            result = collect_preferred_yield(None,self.c,self.config,self.day,tenor)
            return result, wgb

    def test_valid_official_wins_even_when_fallback_is_newer(self):
        obs, wgb = self.selected(fallback=replace(self.fallback,period='2026-10-05'))
        self.assertEqual(obs.provider, 'canada'); self.assertEqual(obs.period,'2026-10-02')
        wgb.assert_not_called()

    def test_failed_stale_monthly_or_invalid_official_uses_fallback(self):
        invalid = [replace(self.official, period='2026-09-27'),
                   replace(self.official, period='2026-09', frequency='monthly'),
                   replace(self.official, unit='unverified'),
                   replace(self.official, iso3='USA'), replace(self.official, tenor_years=10)]
        for official in invalid:
            with self.subTest(official=official):
                obs, _ = self.selected(official=official)
                self.assertEqual(obs.provider, 'wgb'); self.assertTrue(obs.selection_reason)
        obs, _ = self.selected(official_error=DataError('HTTP_FAILURE:403'))
        self.assertIn('HTTP_FAILURE:403', obs.selection_reason)

    def test_invalid_fallback_is_not_accepted(self):
        for changes in [{'period':'2026-09-27'}, {'iso3':'USA'}, {'unit':'bp'},
                        {'series':'canada:10Y'}, {'url':'https://example.org/data'},
                        {'value':float('nan')}, {'tenor_years':10}]:
            with self.subTest(changes=changes), self.assertRaises(DataError):
                self.selected(official_error=DataError('MISSING'), fallback=replace(self.fallback,**changes))

    def test_seven_day_old_official_is_used_and_eighth_day_falls_back(self):
        obs, wgb = self.selected(official=replace(self.official,period='2026-09-28'))
        self.assertEqual(obs.provider, 'canada'); wgb.assert_not_called()
        obs, _ = self.selected(official=replace(self.official,period='2026-09-27'))
        self.assertEqual(obs.provider,'wgb')

    def test_disabled_fallback_keeps_the_official_failure(self):
        self.config['sources']['yield_fallback']['enabled'] = False
        with self.assertRaisesRegex(DataError,'MISSING'):
            self.selected(official_error=DataError('MISSING'))

    def test_all_twenty_seven_countries_have_explicit_unique_wgb_routes(self):
        slugs=[c['wgb_slug'] for c in self.config['countries']['countries']]
        self.assertEqual(len(set(slugs)),27)
        self.assertEqual(self.c['wgb_slug'],'canada')
        self.assertEqual(self.config,load_config('config'))

    def test_ten_year_watch_fallback_preserves_tenor(self):
        f=replace(self.fallback, metric='yield_10y', tenor_years=10, series='canada:10Y',
                  url=self.fallback.url.replace('/5-years/','/10-years/'))
        obs, wgb=self.selected(official_error=DataError('HTTP_FAILURE'),fallback=f,tenor=10)
        self.assertEqual(obs.tenor_years,10)
        self.assertEqual(wgb.call_args.kwargs['tenor'],10)

    def test_pipeline_shows_selected_provider_age_and_date_warning_without_claiming_definition_approval(self):
        b=demo_bundle(self.config,self.day); b['yields']['CAN:5']=self.fallback
        result=evaluate(self.config,b,self.day); row=next(r for r in result['rows'] if r['iso3']=='CAN')
        self.assertEqual(row['yield_5y'],3.2)
        self.assertEqual(row['yield_5y_provider'],'wgb')
        self.assertEqual(row['yield_5y_age_days'],3)
        self.assertTrue(row['yield_5y_fallback'])
        self.assertIn('WGB_DATE_DISCREPANCY',row['warnings'])
        self.assertFalse(row['usable_baseline'])
        self.assertIn('wgb',build_html(result,'test'))
        self.assertIn('WGB_DATE_DISCREPANCY',render_summary_text(build_executive_summary(result)))

    def test_fallback_cannot_inherit_official_publication_approval_or_leak_values_in_notes(self):
        for axis in ('fiscal','fx'): self.config['sources'][axis]['redistribution']='allowed'
        self.c['yield']['redistribution']='allowed'; self.c['yield'].pop('redistribution_review',None)
        b=demo_bundle(self.config,self.day); b['yields']['CAN:5']=self.fallback
        row=next(r for r in evaluate(self.config,b,self.day,public_output=True)['rows'] if r['iso3']=='CAN')
        self.assertIsNone(row['yield_5y']); self.assertFalse(row['usable_baseline'])
        self.assertNotIn('curve_yield',json.dumps(row['provenance']))

    def test_successful_fallback_is_warning_not_system_failure(self):
        from sovereign_macro.collect import collect
        config=deepcopy(self.config); config['countries']['countries']=[self.c]
        class Client:
            records=[]
            def fetch(self,url): return Payload(b'<Cube><Cube time="2026-10-02"><Cube currency="KRW" rate="1500"/></Cube></Cube>',url,'','')
        with patch('sovereign_macro.collect.collect_fiscal',return_value={'errors':[]}), \
             patch('sovereign_macro.yield_selection.collect_yield',side_effect=DataError('HTTP_FAILURE')), \
             patch('sovereign_macro.yield_selection.collect_wgb',return_value=self.fallback):
            bundle=collect(config,Client(),self.day)
        self.assertEqual(bundle['errors'],[])
        self.assertEqual(bundle['yields']['CAN:5'].provider,'wgb')

