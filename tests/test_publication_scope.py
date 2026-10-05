"""Prevent a source-specific reuse review from clearing unrelated observations."""
from copy import deepcopy
from dataclasses import replace
from datetime import date
import json
import unittest

from sovereign_macro.config import load_config
from sovereign_macro.pipeline import demo_bundle, evaluate
from sovereign_macro.summary import build_executive_summary, render_summary_text, render_summary_markdown, render_summary_html


class PublicationScopeTests(unittest.TestCase):
    def setUp(self):
        self.config=load_config()
        self.day=date(2026,10,3)
        for axis in ('fiscal','fx'):
            self.config['sources'][axis]['redistribution']='allowed'
        self.country=next(c for c in self.config['countries']['countries'] if c['iso3']=='CAN')
        self.route=self.country['yield']
        self.route.update(redistribution='allowed',redistribution_review={
            'evidence_url':'https://example.org/reuse',
            'scope':[{'url':'https://example.org/data/5y','query':{'series_ids':'five'}}],
            'notice':'Example source; licence https://example.org/reuse; derived calculations disclosed.'})
        self.bundle=demo_bundle(self.config,self.day)
        self.bundle['yields']['CAN:5']=replace(self.bundle['yields']['CAN:5'],
            provider='example',url='https://example.org/data/5y?series_ids=five&lang=EN',
            series=self.route['series'],redistribution='allowed')

    def row(self,bundle=None,public=True):
        return next(r for r in evaluate(self.config,bundle or self.bundle,self.day,
                                       public_output=public)['rows'] if r['iso3']=='CAN')

    def test_matching_observation_is_published_with_attribution_in_all_summaries(self):
        result=evaluate(self.config,self.bundle,self.day,public_output=True)
        row=next(r for r in result['rows'] if r['iso3']=='CAN')
        self.assertTrue(row['usable_baseline'])
        self.assertEqual(row['redistribution_status'],'allowed')
        summary=build_executive_summary(result)
        for renderer in (render_summary_text,render_summary_markdown,render_summary_html):
            self.assertIn('Example source',renderer(summary))

    def test_wrong_url_or_query_cannot_inherit_approval(self):
        for url in ('https://example.org.evil/data/5y?series_ids=five',
                    'https://evil@example.org/data/5y?series_ids=five',
                    'https://example.org/data/other?series_ids=five',
                    'http://example.org/data/5y?series_ids=five',
                    'https://example.org/data/5y?series_ids=other',
                    'https://example.org/data/5y?series_ids=five&series_ids=other'):
            with self.subTest(url=url):
                b=deepcopy(self.bundle);b['yields']['CAN:5']=replace(b['yields']['CAN:5'],url=url)
                row=self.row(b)
                self.assertIsNone(row['baseline'])
                self.assertFalse(row['usable_baseline'])
                self.assertNotIn('"value":',json.dumps(row['provenance']))

    def test_wrong_series_or_pending_observation_is_redacted(self):
        for change in ({'series':'other'},{'series':''},{'redistribution':'pending'}):
            with self.subTest(change=change):
                b=deepcopy(self.bundle);b['yields']['CAN:5']=replace(b['yields']['CAN:5'],**change)
                self.assertIsNone(self.row(b)['yield_5y'])

    def test_any_unapproved_second_tenor_blocks_whole_row(self):
        self.bundle['yields']['CAN:10']=replace(self.bundle['yields']['CAN:5'],
            metric='yield_10y',tenor_years=10,url='https://other.org/ten')
        self.assertIsNone(self.row()['baseline'])

    def test_missing_scope_evidence_or_notice_fails_closed(self):
        for key in ('scope','evidence_url','notice'):
            with self.subTest(key=key):
                review=self.route['redistribution_review'];old=review.pop(key)
                self.assertIsNone(self.row()['baseline'])
                review[key]=old

    def test_private_scores_and_stale_definition_gates_unchanged(self):
        private=self.row(public=False)
        self.route['redistribution_review']['scope']=[]
        self.assertEqual(self.row(public=False)['baseline'],private['baseline'])
        for change in ({'period':'2026-09-01'},{'unit':'unverified'},
                       {'yield_type':'wrong'},{'tenor_years':4}):
            b=deepcopy(self.bundle);b['yields']['CAN:5']=replace(b['yields']['CAN:5'],**change)
            self.assertFalse(self.row(b,public=False)['usable_baseline'])

    def test_required_provider_modification_date_is_enforced_and_displayed(self):
        self.route['redistribution_review']['required_provenance']=['source_date']
        self.assertIsNone(self.row()['baseline'])
        self.bundle['yields']['CAN:5']=replace(self.bundle['yields']['CAN:5'],source_date='2026-10-02')
        result=evaluate(self.config,self.bundle,self.day,public_output=True)
        self.assertIsNotNone(next(r for r in result['rows'] if r['iso3']=='CAN')['baseline'])
        self.assertIn('2026-10-02',render_summary_text(build_executive_summary(result)))

    def test_malformed_scope_fails_closed(self):
        for scope in (None,[None],[{'url':'https://example.org/data/5y','query':[]}],{'url':'https://example.org/data/5y'}):
            with self.subTest(scope=scope):
                self.route['redistribution_review']['scope']=scope
                self.assertIsNone(self.row()['baseline'])

    def test_real_default_scopes_do_not_clear_synthetic_or_missing_inputs(self):
        config=load_config()
        for axis in ('fiscal','fx'):config['sources'][axis]['redistribution']='allowed'
        for iso in ('PRT','HRV'):
            c=next(c for c in config['countries']['countries'] if c['iso3']==iso)
            self.assertEqual(c['yield']['redistribution'],'allowed')
            self.assertFalse(c['yield']['baseline_compatible'])
            self.assertNotIn('2026-09-10',c['yield']['redistribution_review']['notice'])
        result=evaluate(config,demo_bundle(config,self.day),self.day,public_output=True,demo=True)
        for r in result['rows']:
            self.assertIsNone(r['yield_5y'])
            self.assertFalse(r['usable_baseline'])
        self.assertFalse(result['quality']['safe_to_use'])

    def test_default_approval_is_limited_to_scoped_sources(self):
        config=load_config()
        for axis in ('fiscal','fx'):config['sources'][axis]['redistribution']='allowed'
        c=next(c for c in config['countries']['countries'] if c['iso3']=='PRT')
        c['yield']['series']='12099457'
        b=demo_bundle(config,self.day)
        b['yields']['PRT:5']=replace(b['yields']['PRT:5'],provider='bpstat',series='12099457',
            redistribution='allowed',url='https://bpstat.bportugal.pt/data/v1/domains/26/datasets/690b7b36fd36c0dbe249c48cbbc39524/?series_ids=12099457&obs_last_n=5')
        r=next(r for r in evaluate(config,b,self.day,public_output=True)['rows'] if r['iso3']=='PRT')
        self.assertIsNotNone(r['yield_5y'])
        self.assertFalse(r['usable_baseline'])
        c['yield']['series']='other'
        r=next(r for r in evaluate(config,b,self.day,public_output=True)['rows'] if r['iso3']=='PRT')
        self.assertIsNone(r['yield_5y'])
