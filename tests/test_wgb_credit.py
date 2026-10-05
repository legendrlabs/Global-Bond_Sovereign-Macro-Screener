from datetime import date
import json
import unittest

from sovereign_macro.config import load_config
from sovereign_macro.pipeline import demo_bundle, evaluate
from sovereign_macro.summary import build_executive_summary, render_summary_text
from test_wgb import FixtureClient, COUNTRY, main_data


def table(rating='AA+', day='5 Oct 2026'):
    return f'''<table><thead><tr><th>Rating Agency</th><th>Rating</th>
    <th>Outlook</th><th>Last Update</th><th>Action</th></tr></thead><tbody>
    <tr><td>Standard &amp; Poor's</td><td>{rating}</td><td>stable</td>
    <td>{day}</td><td>rating affirmation</td></tr>
    <tr><td>Moody's Investors Service</td><td>Aa1</td><td>stable</td>
    <td>1 Jan 2026</td><td>affirmation</td></tr></tbody></table>'''


class WgbCreditTests(unittest.TestCase):
    def observation(self, html=table()):
        from sovereign_macro.wgb import collect_wgb
        data=main_data();data['ratingTable']=html
        return collect_wgb(FixtureClient(country_main=data),COUNTRY,date(2026,10,5))

    def test_same_agency_report_is_preserved_without_asserting_rating_type(self):
        credit=json.loads(self.observation().notes).get('reported_credit',{})
        self.assertEqual(credit.get('rating'),'AA+')
        self.assertEqual(credit['agency'],"Standard & Poor's")
        self.assertEqual(credit['last_action_date'],'2026-10-05')
        self.assertEqual(credit['status'],'REPORTED_TYPE_UNVERIFIED')
        self.assertFalse(credit['usable_for_scoring'])
        self.assertTrue(credit['raw_sha256'])

    def test_malformed_future_duplicate_or_missing_rating_is_isolated_from_valid_yield(self):
        cases=[table(day='6 Oct 2026'),table(day='5 Oct'),table(rating='Aa1'),
               table().replace('</tbody>','<tr><td>Standard &amp; Poor\'s</td><td>AA+</td><td>stable</td><td>5 Oct 2026</td><td>affirmation</td></tr></tbody>'),
               table().replace('Rating Agency','Agency'),table(rating='-')]
        for html in cases:
            with self.subTest(html=html):
                obs=self.observation(html)
                self.assertEqual(obs.value,4.518)
                self.assertEqual(json.loads(obs.notes).get('reported_credit',{}).get('status'),'UNAVAILABLE')

    def test_report_displays_source_rating_but_never_creates_credit_or_adjusted_score(self):
        config=load_config();day=date(2026,10,5);bundle=demo_bundle(config,day)
        bundle['yields']['NZL:5']=self.observation()
        result=evaluate(config,bundle,day)
        row=next(r for r in result['rows'] if r['iso3']=='NZL')
        self.assertEqual(row['market_inputs']['credit'].get('rating'),'AA+')
        self.assertIsNone(row['market_inputs']['credit']['value'])
        self.assertIsNone(row['market_quality_norm']);self.assertIsNone(row['adjusted'])
        text=render_summary_text(build_executive_summary(result))
        self.assertIn('Reported Credit Ratings',text);self.assertIn('AA+',text)

    def test_public_and_demo_output_do_not_leak_reported_rating(self):
        config=load_config();day=date(2026,10,5);bundle=demo_bundle(config,day)
        bundle['yields']['NZL:5']=self.observation()
        for kwargs in ({'public_output':True},{'demo':True}):
            result=evaluate(config,bundle,day,**kwargs)
            row=next(r for r in result['rows'] if r['iso3']=='NZL')
            self.assertNotIn('rating',row['market_inputs']['credit'])
            self.assertNotIn('AA+',render_summary_text(build_executive_summary(result)))

    def test_official_yield_does_not_claim_a_wgb_rating_from_unrelated_notes(self):
        from dataclasses import replace
        config=load_config();day=date(2026,10,5);bundle=demo_bundle(config,day)
        bundle['yields']['NZL:5']=replace(self.observation(),provider='official')
        row=next(r for r in evaluate(config,bundle,day)['rows'] if r['iso3']=='NZL')
        self.assertNotIn('rating',row['market_inputs']['credit'])
        self.assertEqual(row['market_inputs']['credit']['status'],'SOURCE_NOT_CONNECTED')
