import unittest
from datetime import date
from unittest.mock import patch
from sovereign_macro import sources
from sovereign_macro.models import DataError

URL='https://www.cnb.cz/export/sites/cnb/en/statistics/.galleries/money_and_banking_stat/mon_bank_stat/2026/menstat_2026-09_EN.pdf'
TABLE='1.3 TABLE 2B – CAPITAL MARKET INTEREST RATES (in %, monthly average) 2 years 5 years 10 years (Maastricht) Bond yields Source: Czech National Bank. Monetary Statistics – 9/2026'
COMMENT='Monetary Statistics – 9/2026 1.4 COMMENTARY ON TABLES 1 – 2 Commentary on key interest rates (Table 1) and financial market interest rates (Table 2): July 2026. 1.4.2 FINANCIAL MARKET INTEREST RATES The yield on the 2Y bond fell to 3.90%. The yield on the 5Y bond increased by 0.10 percentage point to 4.26%. The yield on the 10Y bond rose to 4.79%.'

class CzechTests(unittest.TestCase):
    def test_reference_month_not_publication_month_and_exact_five_year(self):
        self.assertEqual(sources.parse_czech_pages([TABLE,COMMENT],'2026-09'),[('2026-07',4.26)])
        self.assertEqual(sources.parse_czech_pages([TABLE,COMMENT.replace('4.26%','-0.12%')],'2026-09'),[('2026-07',-.12)])

    def test_metadata_drift_and_ambiguous_yield_rejected(self):
        for pages,edition in (([TABLE.replace('monthly average','daily'),COMMENT],'2026-09'),
                              ([TABLE,COMMENT],'2026-08'),
                              ([TABLE,COMMENT.replace('5Y','7Y')],'2026-09'),
                              ([TABLE,COMMENT+ ' The yield on the 5Y bond rose to 4.27%.'],'2026-09'),
                              ([TABLE,COMMENT.replace('July 2026','October 2026')],'2026-09'),
                              ([TABLE,COMMENT.replace('July 2026','July 2025')],'2026-09')):
            with self.assertRaises(DataError):sources.parse_czech_pages(pages,edition)

    def test_unavailable_five_year_cannot_consume_next_tenor_value(self):
        text=COMMENT.replace('The yield on the 5Y bond increased by 0.10 percentage point to 4.26%.',
                             'The yield on the 5Y bond was unavailable.')
        with self.assertRaises(DataError):sources.parse_czech_pages([TABLE,text],'2026-09')

    def test_fifteen_year_table_is_not_five_year_metadata(self):
        with self.assertRaises(DataError):sources.parse_czech_pages([TABLE.replace('5 years','15 years'),COMMENT],'2026-09')

    def test_discovery_official_host_path_edition_and_asof(self):
        html=f'<a href="{URL}">new</a><a href="{URL}">duplicate</a><a href="{URL.replace("2026-09","2026-11")}">future</a><a href="{URL.replace("www.cnb.cz","evil.example")}">foreign</a>'
        self.assertEqual(sources.discover_czech_bulletin(html.encode(),date(2026,10,4)),(URL,'2026-09'))
        with self.assertRaises(DataError):sources.discover_czech_bulletin(b'<a href="https://evil.example/menstat_2026-09_EN.pdf">x</a>',date(2026,10,4))

    def test_collect_pdf_provenance_and_monthly_hold(self):
        from sovereign_macro.config import load_config
        from sovereign_macro.http import Payload
        country=next(c for c in load_config()['countries']['countries'] if c['iso3']=='CZE')
        class Page:
            def __init__(self,text):self.text=text
            def extract_text(self):return self.text
        class Reader:
            pages=[Page(TABLE),Page(COMMENT)]
        class Client:
            def fetch(self,url,**kwargs):
                body=f'<a href="{URL}">pdf</a>'.encode() if url.endswith('index.html') else b'pdf'
                return Payload(body,url,'2026-10-04T00:00:00Z','pdf-sha','2026-10-01')
        with patch('sovereign_macro.sources.PdfReader',return_value=Reader()):
            obs=sources.collect_yield(Client(),country,date(2026,10,4))
        self.assertEqual((obs.period,obs.value,obs.frequency),('2026-07',4.26,'monthly'))
        self.assertEqual(obs.url,URL);self.assertEqual(obs.unit,'percent');self.assertEqual(obs.raw_sha256,'pdf-sha')
        self.assertIn('2026-09',obs.notes)
        self.assertFalse(country['yield']['baseline_compatible'])
        with self.assertRaisesRegex(DataError,'FREQUENCY_OR_DATE'):obs.valid_on(date(2026,10,4))
        with self.assertRaises(DataError):sources.collect_yield(None,country,date(2026,10,4),10)
