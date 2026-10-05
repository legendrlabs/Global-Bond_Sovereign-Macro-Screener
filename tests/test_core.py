import math
import unittest
from datetime import date, timedelta

from sovereign_macro.scoring import baseline, adjusted, logistic, rank_rows
from sovereign_macro.fx import cross_rate, fx_metrics
from sovereign_macro.models import DataError
from sovereign_macro.regimes import regimes


class CoreTests(unittest.TestCase):
    def test_original_formula_percentage_points(self):
        r = baseline(70, 70, [-3, -2], 3)
        self.assertAlmostEqual(r['fiscal'], 27.5)
        self.assertAlmostEqual(r['yield_component'], 25)
        self.assertAlmostEqual(r['baseline'], 52.4404424085)

    def test_negative_yield_is_domain_error(self):
        for value in [-2, -1, -.01]:
            with self.assertRaisesRegex(DataError, 'BASELINE_DOMAIN_ERROR'):
                baseline(70, 70, [0], value)

    def test_zero_yield_and_no_top_clipping(self):
        self.assertEqual(baseline(70, 70, [0], 0)['baseline'], 0)
        self.assertGreater(baseline(-100, -100, [100], 20)['baseline'], 100)

    def test_missing_and_nonfinite_are_not_scores(self):
        for value in [None, float('nan'), float('inf')]:
            with self.assertRaises(DataError):
                baseline(value, 70, [0], 3)
        with self.assertRaises(DataError):
            baseline(70, 70, [], 3)

    def test_logistic_tails_do_not_overflow(self):
        self.assertEqual(logistic(-10000), 0)
        self.assertEqual(logistic(10000), 1)

    def test_adjusted_missing_quality_does_not_reweight(self):
        r = adjusted(25, 1, 0, None)
        self.assertIsNone(r['adjusted'])
        self.assertEqual(r['fiscal_norm'], .5)
        self.assertEqual(r['real_yield_norm'], .5)
        self.assertEqual(r['fx_norm'], 1)

    def test_adjusted_weighted_geometric_and_zero(self):
        self.assertAlmostEqual(adjusted(25, 1, 0, .5)['adjusted'], 57.4349177499)
        self.assertEqual(adjusted(25, 1, 0, 0)['adjusted'], 0)
        self.assertIsNone(adjusted(25, 1, -1, .5)['adjusted'])

    def test_ties_are_competition_ranks_and_unavailable_unranked(self):
        rows = [{'iso3':'USA','baseline':5,'usable_baseline':True},
                {'iso3':'CAN','baseline':5,'usable_baseline':True},
                {'iso3':'AUS','baseline':3,'usable_baseline':True},
                {'iso3':'JPN','baseline':9,'usable_baseline':False}]
        rank_rows(rows, 'baseline')
        self.assertEqual([r['baseline_rank'] for r in rows], [1,1,3,None])

    def test_cross_rate_direction_and_eur_identity(self):
        self.assertEqual(cross_rate({'KRW':1500,'USD':1.25}, 'USD'), 1200)
        self.assertEqual(cross_rate({'KRW':1500}, 'EUR'), 1500)

    def test_krw_identity_does_not_require_foreign_observations(self):
        r=fx_metrics({}, 'KRW', date(2026,10,4))
        self.assertEqual(r['vol_1y'],0)
        self.assertEqual(r['max_drawdown'],0)

    def test_sample_counts_and_no_missing_date_fill(self):
        start=date(2025,10,4)
        points={start+timedelta(days=i):{'KRW':1500,'USD':1.25} for i in range(365)}
        points={d:v for d,v in points.items() if d.weekday()<5}
        r=fx_metrics(points,'USD',date(2026,10,4))
        self.assertEqual(r['vol_1y'],0)
        self.assertIsNone(r['vol_3y'])
        self.assertEqual(r['count_1y'],260)
        few=dict(list(points.items())[:20])
        self.assertIsNone(fx_metrics(few,'USD',date(2026,10,4))['vol_1y'])

    def test_currency_transition_requires_continuity(self):
        self.assertIsNone(fx_metrics({},'EUR',date(2026,10,4),continuity=False)['vol_1y'])

    def test_provider_gap_not_hidden_by_minimum_samples(self):
        dates=[date(2026,9,1)+timedelta(days=i) for i in range(12)]
        points={d:{'KRW':1500,'USD':1.25} for d in dates}
        for d in dates[2:9]: del points[d]['USD']
        r=fx_metrics(points,'USD',date(2026,9,12),min_1y=2,min_3y=2)
        self.assertIsNone(r['vol_1y'])
        self.assertIn('FX_GAP',r['errors'])

    def test_drawdown_uses_krw_per_currency_value_path(self):
        points={date(2026,9,i):{'KRW':v} for i,v in enumerate([100,80,90],1)}
        r=fx_metrics(points,'EUR',date(2026,9,3),min_1y=2,min_3y=2)
        self.assertAlmostEqual(r['max_drawdown'],-.2)

    def test_regime_boundaries_and_required_inputs(self):
        self.assertEqual(regimes(70,75,2,.08,5,5)['fiscal_trend'],'DETERIORATING')
        self.assertEqual(regimes(70,75,2,.08,5,5)['discount_rate'],'HIGHLY_RESTRICTIVE')
        self.assertEqual(regimes(70,70,0,.15,4,4)['fx_risk'],'MEDIUM')
        self.assertEqual(regimes(70,70,-1,0,4,4)['carry'],'UNATTRACTIVE')
        self.assertEqual(regimes(None,70,3,0,5,5)['carry'],'UNAVAILABLE')


if __name__ == '__main__': unittest.main()

class ProviderGapTests(unittest.TestCase):
    def test_global_provider_gap_not_treated_as_daily_return(self):
        from datetime import timedelta
        day=date(2026,10,3)
        points={}
        for n in range(365):
            d=day-timedelta(days=n)
            if d.weekday()<5 and not 100<n<140: points[d]={'KRW':1500,'USD':1}
        result=fx_metrics(points,'USD',day)
        self.assertIsNone(result['vol_1y'])
        self.assertIn('FX_GAP',result['errors'])
