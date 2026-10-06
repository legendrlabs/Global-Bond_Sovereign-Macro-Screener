"""Regressions for observed fixed-peg history across a currency redenomination."""
from copy import deepcopy
from datetime import date, timedelta
import unittest

from sovereign_macro.config import load_config
from sovereign_macro.fx import fx_metrics
from sovereign_macro.pipeline import evaluate, demo_bundle
from sovereign_macro.summary import build_executive_summary, render_summary_markdown

DAY = date(2026, 10, 6)
CUT = date(2026, 1, 1)


def history(as_of=DAY, peg=1.95583):
    points = {}
    day = date(as_of.year-3, as_of.month, as_of.day)
    i = 0
    while day <= as_of:
        if day.weekday() < 5:
            rates = {'KRW': 1500 + (i % 17) * 2}
            if day < CUT:
                rates['BGN'] = peg
            points[day] = rates
            i += 1
        day += timedelta(days=1)
    return points


def contract():
    return dict(kind='fixed_peg_redenomination', verified=True, old_currency='BGN',
                new_currency='EUR', effective_date='2026-01-01', history_from='2020-07-10',
                old_units_per_new=1.95583, reference_decimals=4,
                evidence_urls=['https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260101~c830245e42.en.html'])


class CurrencyTransitionTests(unittest.TestCase):
    def metrics(self, points=None, transition=None, day=DAY):
        return fx_metrics(history(day) if points is None else points, 'EUR', day,
                          transition=contract() if transition is None else transition)

    def test_bgr_pipeline_uses_observed_old_currency_history(self):
        config=load_config()
        bundle=demo_bundle(config, DAY)
        bundle['fx']=history()
        result=evaluate(config, bundle, DAY)
        bgr=next(r for r in result['rows'] if r['iso3']=='BGR')
        self.assertIsNotNone(bgr['fx_vol_1y'])
        self.assertIsNotNone(bgr['fx_vol_3y'])
        self.assertFalse(any('CURRENCY_' in e for e in bgr['errors']))
        self.assertEqual(bgr['fx_history']['status'], 'VERIFIED_CONTINUITY')
        self.assertIn('FX_HISTORY_REBASED', bgr['warnings'])
        text=render_summary_markdown(build_executive_summary(result))
        self.assertIn('FX Currency History',text)
        self.assertIn('BGN → EUR',text)
        self.assertIn('2026-01-01',text)
        self.assertIsNone(bgr['adjusted'])
        self.assertFalse(result['quality']['safe_to_use'])
        self.assertIn('BASELINE_DEFINITION_UNAPPROVED', next(r for r in result['rows'] if r['iso3']=='SVK')['errors'])

    def test_exact_peg_has_no_artificial_jump_or_input_mutation(self):
        points=history();before=deepcopy(points)
        actual=self.metrics(points)
        expected=fx_metrics({d:{'KRW':v['KRW']} for d,v in points.items()}, 'EUR', DAY)
        for key in ('vol_1y','vol_3y','max_drawdown'):
            self.assertAlmostEqual(actual[key], expected[key], places=12)
        self.assertEqual(points, before)
        self.assertGreater(actual['transition']['rebased_count'], 0)

    def test_published_four_decimal_peg_preserves_rounding_difference(self):
        actual=self.metrics(history(peg=1.9558))
        expected=fx_metrics(history(), 'EUR', DAY)
        self.assertIsNotNone(actual['vol_1y'])
        self.assertLess(abs(actual['vol_1y']-expected['vol_1y']), 0.00001)
        self.assertNotEqual(actual['vol_1y'], expected['vol_1y'])

    def test_peg_break_is_rejected_only_in_affected_window(self):
        for bad_day, one_year_valid in ((date(2025,12,31),False),(date(2024,6,3),True)):
            with self.subTest(bad_day=bad_day):
                points=history();points[bad_day]['BGN']=1.956
                actual=self.metrics(points)
                self.assertIsNone(actual['vol_3y'])
                self.assertEqual(actual['vol_1y'] is not None,one_year_valid)
                self.assertIn('FX_PEG_MISMATCH_3Y',actual['errors'])

    def test_absent_old_history_cannot_pass_with_enough_post_transition_samples(self):
        day=date(2026,12,1)
        points=history(day)
        for rates in points.values(): rates.pop('BGN',None)
        actual=self.metrics(points,day=day)
        self.assertGreater(actual['count_1y'],200)
        self.assertIsNone(actual['vol_1y'])
        self.assertIsNone(actual['vol_3y'])
        self.assertIn('FX_TRANSITION_COVERAGE_1Y',actual['errors'])

    def test_missing_boundary_observations_and_stale_data_hold(self):
        points=history()
        for day in list(points):
            if date(2025,12,19)<=day<=date(2026,1,12): del points[day]
        self.assertIsNone(self.metrics(points)['vol_1y'])
        self.assertIn('FX_GAP',self.metrics(points)['errors'])
        stale={d:r for d,r in history().items() if d<=date(2026,9,24)}
        self.assertIn('FX_STALE',self.metrics(stale)['errors'])
        self.assertIsNone(self.metrics(stale)['vol_3y'])

    def test_unverified_or_malformed_contract_keeps_currency_gate(self):
        for changes in ({'verified':False},{'old_units_per_new':0},{'old_units_per_new':True},
                        {'new_currency':'USD'},{'reference_decimals':20},{'evidence_urls':[]},
                        {'effective_date':'2027-01-01'},{'history_from':'2026-02-01'}):
            with self.subTest(changes=changes):
                config=load_config();c=next(c for c in config['countries']['countries'] if c['iso3']=='BGR')
                c['fx_transition']=contract();c['fx_transition'].update(changes)
                bundle=demo_bundle(config,DAY);bundle['fx']=history()
                bgr=next(r for r in evaluate(config,bundle,DAY)['rows'] if r['iso3']=='BGR')
                self.assertIsNone(bgr['fx_vol_1y'])
                self.assertTrue(bgr['errors'])

    def test_effective_date_must_match_configured_currency_assignment(self):
        config=load_config();c=next(c for c in config['countries']['countries'] if c['iso3']=='BGR')
        c['currency_from']='2025-01-01'
        bundle=demo_bundle(config,DAY);bundle['fx']=history()
        bgr=next(r for r in evaluate(config,bundle,DAY)['rows'] if r['iso3']=='BGR')
        self.assertIsNone(bgr['fx_vol_1y'])
        self.assertIn('FX:CURRENCY_TRANSITION_DATE_MISMATCH',bgr['errors'])

    def test_removed_contract_cannot_bypass_history_gate(self):
        config=load_config();c=next(c for c in config['countries']['countries'] if c['iso3']=='BGR')
        c.pop('fx_transition')
        bundle=demo_bundle(config,DAY);bundle['fx']=history()
        bgr=next(r for r in evaluate(config,bundle,DAY)['rows'] if r['iso3']=='BGR')
        self.assertIsNone(bgr['fx_vol_1y'])
        self.assertIn('CURRENCY_1Y_HISTORY_UNAVAILABLE',bgr['errors'])

    def test_unverified_continuity_and_future_assignment_remain_unavailable(self):
        self.assertIsNone(fx_metrics(history(),'EUR',DAY,continuity=False)['vol_1y'])
        config=load_config();bundle=demo_bundle(config,date(2025,12,1));bundle['fx']=history(date(2025,12,1))
        bgr=next(r for r in evaluate(config,bundle,date(2025,12,1))['rows'] if r['iso3']=='BGR')
        self.assertIsNone(bgr['fx_vol_1y'])
        self.assertIsNone(bgr['yield_5y'])

    def test_old_history_not_required_after_full_three_year_euro_window(self):
        day=date(2029,1,3)
        actual=self.metrics(history(day),day=day)
        self.assertIsNotNone(actual['vol_1y'])
        self.assertIsNotNone(actual['vol_3y'])

    def test_public_report_preserves_contract_but_redacts_derived_numbers(self):
        config=load_config();bundle=demo_bundle(config,DAY);bundle['fx']=history()
        bgr=next(r for r in evaluate(config,bundle,DAY,public_output=True)['rows'] if r['iso3']=='BGR')
        self.assertIsNone(bgr['fx_vol_1y'])
        self.assertEqual(bgr['fx_history']['old_units_per_new'],1.95583)
        self.assertTrue(any(p.get('metric')=='fx_currency_transition' for p in bgr['provenance']))


if __name__=='__main__': unittest.main()
