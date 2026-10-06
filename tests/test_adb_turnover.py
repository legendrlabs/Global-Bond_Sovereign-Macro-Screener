from datetime import date
import json
import unittest
from urllib.parse import parse_qs, urlsplit

from sovereign_macro import market_inputs
from sovereign_macro import liquidity
from sovereign_macro.config import load_config
from sovereign_macro.http import Payload
from sovereign_macro.models import DataError
from sovereign_macro.pipeline import demo_bundle, evaluate
from sovereign_macro.summary import build_executive_summary, render_summary_text, sections


# Synthetic government and corporate amounts deliberately have different ratios.
HEADER = ('Economy,Date,"Govt Bonds Turnover(LCY billions)",'
          '"Ave Govt Bonds Outstanding(LCY billions)","Govt BondsTurnover Ratio",'
          '"Corp Bonds Turnover(LCY billions)","Ave Corp Bonds Outstanding(LCY billions)",'
          '"Corp BondsTurnover Ratio"\n')
KR = 'KR,2026-06-30,51.00,100.00,0.51,80,100,0.80\n'
JP = 'JP,2026-06-30,25.00,100.00,0.25,90,100,0.90\n'


def csv_body(rows=KR+JP):
    return ('METADATA:\nIndicator: Bonds Turnover Ratio\n'
            'Definition: Quarterly Bond turnover ratio = Value of bonds traded\n'
            'Average amount of bonds outstanding\nFrequency: Quarterly updates\n'
            'DISCLAIMER: Synthetic test data.\n\n'+HEADER+rows).encode()


class AdbTurnoverTests(unittest.TestCase):
    def parse(self, body, day=date(2026,10,6), **options):
        parser=getattr(liquidity, 'parse_adb_turnover', None)
        self.assertTrue(callable(parser), 'ADB turnover diagnostics are not connected')
        return parser(body, day, **options)

    def test_filters_country_rows_and_uses_government_not_corporate_ratio(self):
        rows=self.parse(csv_body(KR+JP+'HK,2026-06-30,bad,bad,bad,,,\n'))
        self.assertEqual(set(rows), {'KOR','JPN'})
        self.assertEqual(rows['KOR']['value'], 0.51)
        self.assertEqual(rows['JPN']['value'], 0.25)
        self.assertEqual(rows['KOR']['traded_value'], 51)
        self.assertEqual(rows['KOR']['average_outstanding'], 100)
        self.assertEqual(rows['KOR']['period'], '2026-Q2')
        self.assertEqual(rows['KOR']['unit'], 'turns_per_quarter')
        self.assertFalse(rows['KOR']['usable_for_scoring'])

    def test_missing_country_is_unavailable_and_never_zero(self):
        rows=self.parse(csv_body(KR))
        self.assertIsNone(rows['JPN']['value'])
        self.assertEqual(rows['JPN']['status'], 'UNAVAILABLE')

    def test_invalid_country_does_not_erase_valid_country(self):
        for bad in ('', 'NaN', '-1', '0', 'Infinity'):
            with self.subTest(denominator=bad):
                rows=self.parse(csv_body(KR+JP.replace('25.00,100.00','25.00,'+bad)))
                self.assertEqual(rows['KOR']['value'], 0.51)
                self.assertIsNone(rows['JPN']['value'])
                self.assertEqual(rows['JPN']['status'], 'INVALID_DATA')

    def test_ratio_formula_mismatch_and_duplicate_period_are_rejected(self):
        for rows in (KR.replace('0.51','0.80')+JP, KR+KR+JP):
            with self.subTest(rows=rows):
                result=self.parse(csv_body(rows))
                self.assertIsNone(result['KOR']['value'])
                self.assertEqual(result['JPN']['value'], 0.25)

    def test_published_rounding_is_preserved_without_dividing_sales_again(self):
        row=self.parse(csv_body(KR.replace('51.00','50.60')+JP))['KOR']
        self.assertEqual(row['value'], 0.51)
        self.assertEqual(row['traded_value'], 50.6)

    def test_quarter_end_schema_future_and_staleness(self):
        future=KR.replace('2026-06-30','2026-12-31').replace('0.51','0.52').replace('51.00','52.00')
        self.assertEqual(self.parse(csv_body(KR+future+JP))['KOR']['value'], 0.51)
        self.assertEqual(self.parse(csv_body(KR.replace('06-30','06-29')+JP))['KOR']['status'], 'INVALID_DATA')
        old=self.parse(csv_body(), date(2027,2,1))['KOR']
        self.assertEqual(old['status'], 'STALE')
        for field in ('value','traded_value','average_outstanding'):
            self.assertIsNone(old.get(field))

    def test_missing_header_units_and_frequency_fail_closed(self):
        for body in (b'<html>Error</html>', csv_body().replace(b'LCY billions',b'USD millions'),
                     csv_body().replace(b'Quarterly updates',b'Annual updates')):
            with self.subTest(body=body[:80]), self.assertRaises(DataError): self.parse(body)

    def test_collection_uses_bounded_years_and_preserves_existing_japan_diagnostic(self):
        class Client:
            def fetch(self,url):
                if 'bond_turn_ratio_csv.php' in url:
                    q=parse_qs(urlsplit(url).query)
                    if q != {'economies':['KR^JP'],'years':['2025^2026'],'frequency':['Quarterly']}:
                        raise AssertionError(q)
                    return Payload(csv_body(),url,'2026-10-06T12:00:00Z','adb-hash')
                raise TimeoutError('other providers offline')
        result=market_inputs.collect_market_inputs(Client(),dict(enabled=True,size_enabled=False,
            liquidity_enabled=True),date(2026,10,6))
        self.assertEqual(result.get('turnover',{}).get('KOR',{}).get('value'), 0.51)
        self.assertEqual(result['turnover']['JPN']['raw_sha256'], 'adb-hash')
        self.assertEqual(result['liquidity']['JPN']['provider'], 'jsda')

    def test_failed_refresh_has_no_current_value(self):
        class Offline:
            def fetch(self,url): raise TimeoutError('offline')
        result=market_inputs.collect_market_inputs(Offline(),dict(enabled=True,size_enabled=False,
            liquidity_enabled=True),date(2026,10,6))
        for iso in ('KOR','JPN'):
            self.assertEqual(result.get('turnover',{}).get(iso,{}).get('status'), 'UNAVAILABLE')
            self.assertIsNone(result['turnover'][iso]['value'])

    def test_private_display_and_public_demo_and_whole_row_redaction(self):
        config=load_config();day=date(2026,10,6);bundle=demo_bundle(config,day)
        turnover=self.parse(csv_body())
        for row in turnover.values(): row.update(redistribution='pending',raw_sha256='adb-hash')
        bundle['market_inputs']={'turnover':turnover}
        result=evaluate(config,bundle,day)
        row=next(r for r in result['rows'] if r['iso3']=='KOR')
        self.assertEqual(row['market_inputs'].get('turnover',{}).get('value'), 0.51)
        self.assertIsNone(row['adjusted']);self.assertIsNone(row['market_quality_norm'])
        text=render_summary_text(build_executive_summary(result))
        self.assertIn('ADB Government Bond Turnover',text)
        table=next(rows for title,headers,rows in sections(build_executive_summary(result))
                   if title.startswith('ADB Government Bond Turnover'))
        self.assertEqual(next(r for r in table if r[0]=='KOR')[1], '0.51')
        for options in ({'public_output':True},{'demo':True}):
            hidden=evaluate(config,bundle,day,**options)
            for r in hidden['rows']:
                for item in [r['market_inputs'].get('turnover',{})]+[p for p in r['provenance'] if p.get('provider')=='adb']:
                    for field in ('value','traded_value','average_outstanding'):
                        self.assertIsNone(item.get(field))
            if options.get('demo'): self.assertNotIn('adb-hash',json.dumps(hidden))
        for item in turnover.values(): item['redistribution']='allowed'
        public=evaluate(config,bundle,day,public_output=True)
        row=next(r for r in public['rows'] if r['iso3']=='KOR')
        self.assertIsNone(row['market_inputs']['turnover'].get('value'))
        for p in row['provenance']:
            if p.get('provider')=='adb': self.assertIsNone(p.get('traded_value'))
        self.assertEqual(bundle['market_inputs']['turnover']['KOR']['traded_value'],51)
