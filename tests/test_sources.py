import unittest
from datetime import date
from sovereign_macro.sources import parse_ecb, parse_canada, parse_treasury, parse_riksbank
from sovereign_macro.fiscal import parse_fiscal, parse_net_debt_pdf, merge_pdf
from sovereign_macro.models import DataError

class SourcesTests(unittest.TestCase):
    def test_ecb_cross_currency_rows(self):
        xml=b'<Envelope><Cube><Cube time="2026-10-01"><Cube currency="KRW" rate="1500"/><Cube currency="USD" rate="1.25"/></Cube></Cube></Envelope>'
        self.assertEqual(parse_ecb(xml)['2026-10-01']['KRW'],1500)
    def test_canada_exact_series_and_latest_nonempty(self):
        j={'seriesDetail':{'BD.CDN.5YR.DQ.YLD':{'label':'5 year'}},'observations':[{'d':'2026-09-30','BD.CDN.5YR.DQ.YLD':{'v':'3.62'}},{'d':'2026-10-01','BD.CDN.5YR.DQ.YLD':{'v':''}}]}
        self.assertEqual(parse_canada(j,'BD.CDN.5YR.DQ.YLD'),[('2026-09-30',3.62)])
        with self.assertRaises(DataError): parse_canada(j,'OTHER')
    def test_treasury_namespaces_and_tenors(self):
        x=b'<feed xmlns:d="urn:d"><entry><d:NEW_DATE>2026-10-02T00:00:00</d:NEW_DATE><d:BC_5YEAR>5.06</d:BC_5YEAR><d:BC_10YEAR>5.2</d:BC_10YEAR></entry></feed>'
        self.assertEqual(parse_treasury(x,5),[('2026-10-02',5.06)])
        self.assertEqual(parse_treasury(x,10),[('2026-10-02',5.2)])
    def test_riksbank_drops_null_not_zero(self):
        self.assertEqual(parse_riksbank([{'date':'2026-10-01','value':0},{'date':'2026-10-02','value':None}]),[('2026-10-01',0.)])
    def test_fiscal_edition_horizon_and_missing(self):
        meta={k:{'source':source,'unit':'Annual percent change' if k=='PCPIPCH' else '% of GDP','projection-year':2026} for k,source in [('GGXWDN_G01_GDP_PT','Fiscal Monitor (April 2026)'),('GGXCNL_G01_GDP_PT','Fiscal Monitor (April 2026)'),('G_XWDG_G01_GDP_PT','Fiscal Monitor (April 2026)'),('PCPIPCH','World Economic Outlook (April 2026)')]}
        payload={k:{'values':{k:{'CAN':{str(y):1 for y in range(2026,2032)}}}} for k in meta}
        data=parse_fiscal(meta,payload,2026)
        self.assertEqual(data['horizon_end'],2031)
        self.assertNotIn('SVK',data['values']['net_debt'])
        meta['PCPIPCH']['source']='World Economic Outlook (October 2026)'
        with self.assertRaises(DataError): parse_fiscal(meta,payload,2026)
    def test_pdf_generic_rows_and_overlap_guard(self):
        text='Table A8. General Government Net Debt\n2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 2031\nCanada2 '+ ' '.join(str(i) for i in range(15))+'\nSlovak Republic '+' '.join(str(i+20) for i in range(15))
        countries=[{'iso3':'CAN','pdf_label':'Canada'},{'iso3':'SVK','pdf_label':'Slovak Republic'}]
        rows=parse_net_debt_pdf(text,countries)
        self.assertEqual(rows['SVK'][2031],34)
        api={'CAN':{2026:9.02}}
        merge_pdf(api,rows)
        self.assertEqual(api['CAN'][2026],9.02)
        self.assertEqual(api['SVK'][2031],34)
        with self.assertRaises(DataError): merge_pdf({'CAN':{2026:11}},rows)

class FileAdapterTests(unittest.TestCase):
    def test_rba_dates_units_column_and_blank_tail(self):
        from sovereign_macro.sources import parse_rba
        text='Units,Per cent per annum\nSeries ID,FCMYGBAG5D\n30-Sep-2026,4.983\n01-Oct-2026,\n'
        self.assertEqual(parse_rba(text.encode(),'FCMYGBAG5D'),[('2026-09-30',4.983)])
    def test_japan_era_and_percent_no_scaling(self):
        from sovereign_macro.sources import parse_japan
        text='国債金利情報 (単位 : %)\n基準日,5年,10年\nH31.4.30,-0.12,0.1\nR8.10.1,2.407,3.092\n'
        self.assertEqual(parse_japan(text.encode('cp932'),5),[('2019-04-30',-.12),('2026-10-01',2.407)])
    def test_kofia_ignores_summary_and_empty_rows(self):
        from sovereign_macro.sources import parse_kofia
        text='<message><BISComDspDatDTO><val1>최고</val1><val2>8</val2></BISComDspDatDTO><BISComDspDatDTO><val1>2026-10-02</val1><val2>4.129</val2></BISComDspDatDTO><BISComDspDatDTO><val1>2026-10-03</val1><val2/></BISComDspDatDTO></message>'
        self.assertEqual(parse_kofia(text.encode()),[('2026-10-02',4.129)])
    def test_latest_sort_and_duplicate_conflict(self):
        from sovereign_macro.sources import select_latest
        self.assertEqual(select_latest([('2026-10-02',4),('2026-10-01',5)],date(2026,10,3)),('2026-10-02',4))
        with self.assertRaises(DataError): select_latest([('2026-10-02',4),('2026-10-02',5)],date(2026,10,3))
    def test_norway_rejects_treasury_bill_and_wrong_tenor(self):
        from sovereign_macro.sources import parse_norway
        text='FREQ;TENOR;INSTRUMENT_TYPE;TIME_PERIOD;OBS_VALUE\nB;5Y;GBON;2026-10-01;4.71\nB;3M;TBIL;2026-10-01;4.4\n'
        self.assertEqual(parse_norway(text.encode(),5),[('2026-10-01',4.71)])

class ContractRegressionTests(unittest.TestCase):
    def test_unsupported_tenors_cannot_relabel_five_year_series(self):
        from sovereign_macro.config import load_config
        from sovereign_macro.sources import collect_yield
        for c in load_config()['countries']['countries']:
            if c['yield']['adapter'] in ('rba','kofia','italy','belgium'):
                with self.assertRaisesRegex(DataError,'TENOR_NOT_IMPLEMENTED'):
                    collect_yield(None,c,date(2026,10,3),tenor=10)
    def test_rba_contradictory_or_missing_units_rejected(self):
        from sovereign_macro.sources import parse_rba
        for units in ('Basis points',''):
            fixture=f'Units,{units}\nSeries ID,FCMYGBAG5D\n30-Sep-2026,498.3\n'
            with self.assertRaisesRegex(DataError,'UNIT'): parse_rba(fixture.encode(),'FCMYGBAG5D')

class MetadataRegressionTests(unittest.TestCase):
    def test_canada_wrong_maturity_rejected(self):
        with self.assertRaisesRegex(DataError,'MATURITY'):
            parse_canada({'seriesDetail':{'s':{'label':'10 year'}},'observations':[]},'s')
    def test_japan_missing_percent_metadata_rejected(self):
        from sovereign_macro.sources import parse_japan
        with self.assertRaisesRegex(DataError,'UNIT'):
            parse_japan('基準日,5年\nR8.10.1,240.7\n'.encode('cp932'),5)
    def test_riksbank_changed_definition_rejected_before_observations(self):
        from sovereign_macro.sources import collect_yield
        from sovereign_macro.config import load_config
        class Client:
            riksbank_series={'SEGVB5YC':{'longDescription':'Government bond, maturity 10 years','seriesClosed':False}}
        c=next(c for c in load_config()['countries']['countries'] if c['iso3']=='SWE')
        with self.assertRaisesRegex(DataError,'SERIES_METADATA'):
            collect_yield(Client(),c,date(2026,10,3))

class PdfEditionTests(unittest.TestCase):
    def test_same_edition_footer_whitespace_and_mismatch(self):
        from sovereign_macro.fiscal import validate_pdf_edition
        validate_pdf_edition('International Monetary Fund | April 2026','April 2026')
        validate_pdf_edition('International Monetary Fund | April    2026','April 2026')
        with self.assertRaisesRegex(DataError,'EDITION'):
            validate_pdf_edition('International Monetary Fund | October 2026','April 2026')
