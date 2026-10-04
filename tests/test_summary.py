import copy
from datetime import date
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from sovereign_macro.config import load_config
from sovereign_macro.pipeline import evaluate, demo_bundle
from sovereign_macro.report import publish
from sovereign_macro import cli
from sovereign_macro import summary


def fixture():
    rows=[]
    for iso,rank,usable in [('BBB',2,True),('AAA',1,True),('CCC',None,True),('DDD',3,False)]:
        rows.append(dict(iso3=iso,name=iso,currency='EUR',baseline_rank=rank,baseline=42.123,
                         usable_baseline=usable,errors=[] if usable else ['YIELD_5Y_UNAVAILABLE'],
                         adjusted=None,adjusted_rank=None,provenance=[],yield_5y=3.5,fx_vol_1y=None,
                         carry='UNAVAILABLE',redistribution_status='allowed'))
    return dict(rows=rows,as_of='2026-10-05',model_version='test-model',quality=dict(
        status='DATA_HOLD',safe_to_use=False,safe_to_use_adjusted=False,baseline_usable=3,
        adjusted_usable=0,country_count=4,demo=False,public_output=False,
        system_errors=['DDD:5:DataError:HTTP_FAILURE:429','FX:DataError:ReadTimeout']))


class SummaryTests(unittest.TestCase):
    def test_partial_filters_unusable_and_missing_rank_and_sorts(self):
        r=fixture();r['quality']['baseline_usable']=6
        before=copy.deepcopy(r);s=summary.build_executive_summary(r)
        self.assertEqual(s['usage_mode'],'PARTIAL BASELINE')
        self.assertEqual([x['iso3'] for x in s['baseline_ranking']],['AAA','BBB'])
        self.assertEqual(r,before)
        self.assertEqual(s['coverage']['baseline_usable'],6)

    def test_zero_and_full_modes_use_quality(self):
        r=fixture();r['quality']['baseline_usable']=0
        self.assertEqual(summary.build_executive_summary(r)['usage_mode'],'DATA HOLD')
        r['quality']['safe_to_use']=True
        self.assertEqual(summary.build_executive_summary(r)['usage_mode'],'FULL COMPARISON')

    def test_demo_cannot_offer_real_ranking_or_available_decision(self):
        r=fixture();r['quality'].update(demo=True,safe_to_use=True,safe_to_use_adjusted=True)
        s=summary.build_executive_summary(r)
        self.assertEqual(s['usage_mode'],'SYNTHETIC DEMO')
        self.assertEqual(s['baseline_ranking'],[])
        self.assertTrue(all(v=='SYNTHETIC DEMO' for v in s['decision'].values()))

    def test_holds_include_raw_country_collection_error_and_global_fx(self):
        s=summary.build_executive_summary(fixture())
        d=next(x for x in s['holds'] if x['iso3']=='DDD')
        self.assertIn('DDD:5:DataError:HTTP_FAILURE:429',d['reasons'])
        self.assertIn('FX:DataError:ReadTimeout',s['system_holds'])

    def test_ranked_country_still_reports_missing_auxiliary_axes(self):
        r=fixture();r['rows'][1]['errors']=['FX_INSUFFICIENT_1Y','CPI_HORIZON_INCOMPLETE','MARKET_QUALITY_UNAVAILABLE']
        r['quality']['system_errors'].append('AAA:10:DataError:HTTP_FAILURE:429')
        s=summary.build_executive_summary(r)
        self.assertEqual(s['baseline_ranking'][0]['iso3'],'AAA')
        held=next((x for x in s['holds'] if x['iso3']=='AAA'),None)
        self.assertIsNotNone(held)
        self.assertIn('FX_INSUFFICIENT_1Y',held['reasons'])
        self.assertIn('AAA:10:DataError:HTTP_FAILURE:429',held['reasons'])

    def test_no_adjusted_score_created_and_missing_values_stay_missing(self):
        s=summary.build_executive_summary(fixture())
        self.assertEqual(s['adjusted_status'],'NOT AVAILABLE')
        self.assertEqual(s['decision']['ADJUSTED MODEL'],'DATA_HOLD')
        self.assertIsNone(s['top_country_metrics'][0]['fx_vol_1y'])
        for renderer in (summary.render_summary_text,summary.render_summary_markdown,summary.render_summary_html):
            text=renderer(s)
            self.assertIn('MARKET_QUALITY_UNAVAILABLE',text)
            self.assertIn('—',text)
            self.assertNotIn('BUY',text)

    def test_unknown_counts_are_not_inferred_from_validated_rows(self):
        s=summary.build_executive_summary(fixture())
        self.assertIsNone(s['coverage']['yield5_routes_registered'])
        self.assertIsNone(s['coverage']['yield5_observations_parsed'])
        self.assertIn('UNKNOWN',summary.render_summary_text(s))

    def test_public_result_never_restores_private_numbers_or_regimes(self):
        c=load_config();day=date(2026,10,5);b=demo_bundle(c,day)
        private=evaluate(c,b,day);public=evaluate(c,b,day,public_output=True)
        self.assertTrue(any(r['baseline'] is not None for r in private['rows']))
        s=summary.build_executive_summary(public)
        self.assertEqual(s['baseline_ranking'],[])
        self.assertEqual(s['top_country_metrics'],[])
        self.assertEqual(s['coverage']['baseline_usable'],0)
        for renderer in (summary.render_summary_text,summary.render_summary_markdown,summary.render_summary_html):
            self.assertNotIn('IMPROVING',renderer(s))
            self.assertIn('REDISTRIBUTION_PENDING_REDACTED',renderer(s))

    def test_cli_markdown_html_share_same_status_and_counts(self):
        r=fixture()
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(cli,'collect',return_value={}),patch.object(cli,'evaluate',return_value=r):
                stdout=io.StringIO()
                with redirect_stdout(stdout):self.assertEqual(cli.main(['run','--output',tmp]),0)
            import json
            p=Path(tmp)/json.loads((Path(tmp)/'current.json').read_text())['path']
            for text in [stdout.getvalue(),(p/'latest.md').read_text(),(p/'index.html').read_text()]:
                self.assertIn('PARTIAL BASELINE',text)
                self.assertIn('DATA_HOLD',text)
                self.assertIn('SAFE_TO_USE',text)
                self.assertIn('3 / 4',text)
            self.assertIn('Full Diagnostic Table',(p/'latest.md').read_text())
            self.assertTrue((p/'executive_summary.json').is_file())

    def test_html_names_and_errors_are_escaped(self):
        r=fixture();r['rows'][0]['name']='<script>alert(1)</script>'
        text=summary.render_summary_html(summary.build_executive_summary(r))
        self.assertNotIn('<script>',text)
        self.assertIn('&lt;script&gt;',text)

    def test_parsed_count_includes_observation_rejected_by_existing_gate(self):
        c=load_config();day=date(2026,10,5);b=demo_bundle(c,day)
        from dataclasses import replace
        b['yields']['CAN:5']=replace(b['yields']['CAN:5'],period='2020-01-01')
        r=evaluate(c,b,day)
        self.assertEqual(r['coverage']['yield5_observations_parsed'],27)
        self.assertFalse(next(x for x in r['rows'] if x['iso3']=='CAN')['usable_baseline'])

    def test_app_decline_displays_saved_summary(self):
        from sovereign_macro.interactive import run_app
        with tempfile.TemporaryDirectory() as tmp:
            r=fixture();publish(r,tmp)
            stdout=io.StringIO()
            with patch('sovereign_macro.updates.latest_release',return_value=None),redirect_stdout(stdout):
                run_app(tmp,date(2026,10,6),False,lambda: self.fail('declined refresh'),
                        interactive=True,input_fn=lambda _: 'n',open_browser=False)
            self.assertIn('PARTIAL BASELINE',stdout.getvalue())
            self.assertIn('GLOBAL STATUS',stdout.getvalue())
