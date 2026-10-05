"""Catch valid official exclusions and misleading aggregate availability."""
from dataclasses import replace
from datetime import date
import unittest

from sovereign_macro.config import load_config
from sovereign_macro.pipeline import demo_bundle, evaluate
from sovereign_macro.summary import build_executive_summary, render_summary_text


class QualityScopeTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config()
        self.day = date(2026, 10, 5)

    def test_verified_official_major_markets_are_ranked_with_definition_disclosed(self):
        bundle = demo_bundle(self.config, self.day)
        for iso, provider in [('KOR', 'kofia'), ('USA', 'treasury'), ('JPN', 'japan')]:
            bundle['yields'][iso + ':5'] = replace(bundle['yields'][iso + ':5'], provider=provider)
        result = evaluate(self.config, bundle, self.day)
        for iso in ('KOR', 'USA', 'JPN'):
            row = next(r for r in result['rows'] if r['iso3'] == iso)
            self.assertTrue(row['usable_baseline'], iso)
            self.assertIsNotNone(row['baseline_rank'])
            self.assertTrue(row['baseline_definition_note'])
            self.assertIn('BASELINE_DEFINITION_DIFFERENCE', row['warnings'])

    def test_iceland_and_australia_research_proxies_rank_with_original_definitions(self):
        bundle = demo_bundle(self.config, self.day)
        for iso, provider, definition in [('ISL', 'iceland', 'par_constant_maturity'),
                                           ('AUS', 'rba', 'interpolated_constant_maturity')]:
            bundle['yields'][iso + ':5'] = replace(bundle['yields'][iso + ':5'], provider=provider, yield_type=definition)
        result = evaluate(self.config, bundle, self.day)
        for iso, definition in [('ISL', 'par_constant_maturity'), ('AUS', 'interpolated_constant_maturity')]:
            row = next(r for r in result['rows'] if r['iso3'] == iso)
            self.assertTrue(row['usable_baseline'], iso)
            self.assertIsNotNone(row['baseline_rank'])
            self.assertEqual(row['yield_type'], definition)
            self.assertTrue(row['baseline_definition_note'])
            self.assertTrue(row['baseline_definition_source'])
            self.assertIn('BASELINE_DEFINITION_DIFFERENCE', row['warnings'])
            self.assertFalse(row['usable_adjusted'])
        for iso in ('SVK', 'ESP'):
            row = next(r for r in result['rows'] if r['iso3'] == iso)
            self.assertFalse(row['usable_baseline'])
            self.assertIsNone(row['baseline_rank'])

    def test_new_research_proxy_approvals_keep_stale_unit_and_definition_gates(self):
        for iso in ('ISL', 'AUS'):
            for changes in ({'period': '2026-09-27'}, {'yield_type': 'estimated_zero_coupon'}, {'unit': 'bp'}):
                bundle = demo_bundle(self.config, self.day)
                bundle['yields'][iso + ':5'] = replace(bundle['yields'][iso + ':5'], **changes)
                row = next(r for r in evaluate(self.config, bundle, self.day)['rows'] if r['iso3'] == iso)
                self.assertFalse(row['usable_baseline'])
                self.assertIsNone(row['baseline_rank'])

    def test_baseline_remains_available_when_fx_and_market_quality_are_missing(self):
        bundle = demo_bundle(self.config, self.day)
        bundle['fx'] = {}
        result = evaluate(self.config, bundle, self.day)
        summary = build_executive_summary(result)
        scopes = {r['scope']: r for r in summary['quality_scopes']}
        self.assertGreater(scopes['BASELINE']['available'], 0)
        self.assertEqual(scopes['FX_1Y']['available'], 1)  # KRW identity remains valid.
        self.assertEqual(scopes['MARKET_QUALITY']['available'], 0)
        self.assertFalse(result['quality']['safe_to_use'])
        text = render_summary_text(summary)
        self.assertLess(text.index('USAGE MODE'), text.index('GLOBAL STATUS'))

    def test_approved_definition_never_overrides_stale_or_wrong_metric(self):
        bundle = demo_bundle(self.config, self.day)
        for changes in ({'period': '2026-09-27'}, {'yield_type': 'zero_coupon'},
                        {'metric': 'yield_10y'}, {'unit': 'bp'}):
            bundle['yields']['USA:5'] = replace(demo_bundle(self.config, self.day)['yields']['USA:5'], **changes)
            row = next(r for r in evaluate(self.config, bundle, self.day)['rows'] if r['iso3'] == 'USA')
            self.assertFalse(row['usable_baseline'])
            self.assertIsNone(row['baseline_rank'])

    def test_scope_counts_use_redacted_public_rows(self):
        result = evaluate(self.config, demo_bundle(self.config, self.day), self.day, public_output=True)
        scopes = {r['scope']: r for r in build_executive_summary(result)['quality_scopes']}
        self.assertEqual(scopes['BASELINE']['available'], 0)
        self.assertEqual(scopes['REAL_YIELD']['available'], 0)

    def test_fiscal_rollover_is_not_mislabeled_as_definition_failure(self):
        bundle = demo_bundle(self.config, self.day)
        bundle['fiscal']['horizon_start'] = 2025
        for vals in bundle['fiscal']['values']['overall_balance'].values(): vals[2025] = -2
        row = next(r for r in evaluate(self.config, bundle, self.day)['rows'] if r['iso3'] == 'CAN')
        self.assertIn('FISCAL_YEAR_ROLLOVER', row['errors'])
        self.assertNotIn('BASELINE_DEFINITION_UNAPPROVED', row['errors'])

    def test_demo_provenance_strips_values_and_serialized_notes_without_mutating_input(self):
        bundle=demo_bundle(self.config,self.day)
        bundle['yields']['KOR:5']=replace(bundle['yields']['KOR:5'],notes='{"crosscheck":987.654}')
        bundle['provenance']={'fx':{'value':987.654,'notes':'private-source','url':'test'}}
        result=evaluate(self.config,bundle,self.day,demo=True)
        for row in result['rows']:
            for source in row['provenance']:
                self.assertNotIn('value',source);self.assertNotIn('notes',source)
        self.assertEqual(bundle['provenance']['fx']['value'],987.654)
        from sovereign_macro.report import publish
        import tempfile
        with tempfile.TemporaryDirectory() as output:
            path=publish(result,output)
            for name in ('index.html','run_manifest.json','country_details.csv'):
                self.assertNotIn('987.654',(path/name).read_text())

    def test_demo_zero_live_eligibility_is_not_displayed_as_country_missingness(self):
        result=evaluate(self.config,demo_bundle(self.config,self.day),self.day,demo=True)
        for scope in build_executive_summary(result)['quality_scopes']:
            self.assertEqual(scope['available'],0)
            self.assertEqual(scope['unavailable_countries'],[])
            self.assertEqual(scope['status'],'SYNTHETIC DEMO')
