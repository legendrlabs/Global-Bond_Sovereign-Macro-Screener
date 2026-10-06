"""Synthetic examples catch date and scope errors in new official sources."""
from datetime import date
import unittest

from sovereign_macro.issuer_credit import parse_issuer_credit
from sovereign_macro.models import DataError
from test_issuer_credit import table

DAY = date(2026, 10, 7)


def belgium(day='12.09.2026', next_day='23.10.2026'):
    return ('<h1>Federal Government</h1><h3>Belgium\'s Rating</h3>' + table(
        ['RATING AGENCY', 'CURRENT RATING', 'EXPECTED DATE OF THE NEXT REVIEW'],
        [['Standard & Poors', f'BBB+ confirmed, outlook negative ({day})', next_day]]) +
        '<h3>Main rating agencies comparison</h3>' + table(
        ['Standard & Poors', "Moody's", 'Fitch Ratings'], [['AAA', 'Aaa', 'AAA']])).encode()


def denmark(day='12-Sep-2026'):
    return ('<h1>Rating</h1><p>The Kingdom of Denmark\'s credit rating</p>'
        '<table><tr><td></td><td colspan="2">Domestic debt</td>'
        '<td colspan="2">Foreign debt</td><td>Outlook</td><td>Most recently confirmed</td></tr>'
        '<tr><td></td><td>Long</td><td>Short</td><td>Long</td><td>Short</td><td></td><td></td></tr>'
        f'<tr><td>Standard &amp; Poor’s</td><td>AA</td><td>A-1+</td><td>AA-</td>'
        f'<td>A-1</td><td>Stable</td><td>{day}</td></tr></table>').encode()


def slovakia(day='September 12, 2026'):
    return ('<h1>Credit rating</h1><h3>Current Credit Rating of the Slovak Republic</h3>' + table(
        ['Agency', 'Standard & Poor’s', 'Moody’s', 'Fitch Ratings'],
        [['Grade', 'BBB+ stable outlook', 'A2 positive outlook', 'A- negative outlook'],
         ['Last change', day, 'January 1, 2020', 'January 1, 2021']])).encode()


class CreditExpansionTests(unittest.TestCase):
    def test_belgium_confirmation_ignores_next_review_and_scale_comparison(self):
        row = parse_issuer_credit('BEL', belgium(), DAY)
        self.assertEqual(row['rating'], 'BBB+')
        self.assertEqual(row['outlook'], 'Negative')
        self.assertEqual(row['assessment_date'], '2026-09-12')
        self.assertEqual(row['assessment_date_type'], 'issuer_confirmation_date')
        self.assertEqual(row['rating_kind'], 'currency_and_term_unverified')
        self.assertIsNone(row['currency'])
        self.assertFalse(row['usable_for_scoring'])

    def test_denmark_keeps_long_domestic_and_foreign_debt_separate_without_currency_inference(self):
        row = parse_issuer_credit('DNK', denmark(), DAY)
        self.assertEqual(row['rating'], 'AA')
        self.assertEqual(row['foreign_rating'], 'AA-')
        self.assertEqual(row['assessment_date'], '2026-09-12')
        self.assertEqual(row['assessment_date_type'], 'issuer_most_recently_confirmed')
        self.assertEqual(row['rating_kind'], 'long_term_domestic_debt_currency_unverified')
        self.assertEqual(row['status'], 'REPORTED_TYPE_UNVERIFIED')
        self.assertIsNone(row['currency']); self.assertIsNone(row['value'])

    def test_slovakia_last_change_never_masquerades_as_latest_assessment(self):
        row = parse_issuer_credit('SVK', slovakia(), DAY)
        self.assertEqual(row['rating'], 'BBB+')
        self.assertEqual(row['last_action_date'], '2026-09-12')
        self.assertEqual(row['date_type'], 'issuer_last_change')
        self.assertNotIn('assessment_date', row)
        self.assertEqual(row['rating_kind'], 'currency_and_term_unverified')
        self.assertFalse(row['usable_for_scoring'])

    def test_new_sources_reject_future_or_ambiguous_dates_and_wrong_country_or_headers(self):
        cases = [
            ('BEL', belgium('08.10.2026')), ('BEL', belgium('09.2026')),
            ('BEL', belgium().replace(b"Belgium's Rating", b"Another state's Rating")),
            ('DNK', denmark('08-Oct-2026')),
            ('DNK', denmark().replace(b'Domestic debt', b'Foreign debt')),
            ('DNK', denmark().replace(b'<td>Long</td>', b'<td>Short</td>', 1)),
            ('DNK', denmark().replace(b'colspan="2"', b'colspan="1"', 1)),
            ('SVK', slovakia('October 8, 2026')),
            ('SVK', slovakia().replace(b'Last change', b'Next review')),
            ('SVK', slovakia().replace(b'Slovak Republic', b'Unrelated Republic')),
        ]
        for iso, body in cases:
            with self.subTest(iso=iso, body=body[:70]), self.assertRaises(DataError):
                parse_issuer_credit(iso, body, DAY)

    def test_all_configured_countries_get_secondary_candidates_without_observations(self):
        from sovereign_macro.config import load_config
        from sovereign_macro.market_inputs import country_market_inputs
        for country in load_config()['countries']['countries']:
            iso = country['iso3']
            links = country_market_inputs(iso, {})['credit']['candidate_sources']
            with self.subTest(iso=iso):
                self.assertTrue(any(x['provider'] == 'Trading Economics' for x in links))
                self.assertTrue(any(x['provider'] != 'Trading Economics' for x in links))
                for link in links:
                    self.assertFalse(link['usable_for_scoring'])
                    self.assertNotIn('rating', link); self.assertNotIn('value', link)

    def test_report_explains_confirmation_and_change_date_semantics(self):
        from sovereign_macro.config import load_config
        from sovereign_macro.pipeline import demo_bundle, evaluate
        from sovereign_macro.summary import build_executive_summary, render_summary_text
        config = load_config()
        bundle = demo_bundle(config, DAY)
        bundle['market_inputs'] = {'credit': {
            iso: parse_issuer_credit(iso, body, DAY)
            for iso, body in [('BEL', belgium()), ('DNK', denmark()), ('SVK', slovakia())]}}
        text = render_summary_text(build_executive_summary(evaluate(config, bundle, DAY)))
        self.assertIn('issuer_confirmation_date', text)
        self.assertIn('issuer_most_recently_confirmed', text)
        self.assertIn('issuer_last_change', text)


if __name__ == '__main__':
    unittest.main()
