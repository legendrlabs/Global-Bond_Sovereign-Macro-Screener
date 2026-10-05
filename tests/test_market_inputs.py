from datetime import date
import unittest

from sovereign_macro.config import load_config
from sovereign_macro.pipeline import demo_bundle, evaluate
from sovereign_macro.summary import build_executive_summary, render_summary_text


def document(series):
    return ('<StructureSpecificData><Header><Prepared>2026-10-05T00:00:00Z</Prepared></Header>'
            '<DataSet>' + series + '</DataSet></StructureSpecificData>').encode()


def series(area='KR', **changes):
    attrs=dict(FREQ='Q',ADJUSTMENT='N',REF_AREA=area,COUNTERPART_AREA='XW',REF_SECTOR='S1311',
        COUNTERPART_SECTOR='S1',CONSOLIDATION='N',ACCOUNTING_ENTRY='L',STO='LE',INSTR_ASSET='F3',
        MATURITY='T',EXPENDITURE='_Z',UNIT_MEASURE='USD',CURRENCY_DENOM='_T',VALUATION='N',
        PRICES='V',TRANSFORMATION='N',CUST_BREAKDOWN='_T',UNIT_MULT='9')
    attrs.update(changes)
    return '<Series ' + ' '.join(f'{k}="{v}"' for k,v in attrs.items()) + '>' + \
        '<Obs TIME_PERIOD="2026-Q1" OBS_VALUE="100" CONF_STATUS="F" />' + \
        '<Obs TIME_PERIOD="2026-Q2" OBS_VALUE="120" CONF_STATUS="F" /></Series>'


class MarketInputTests(unittest.TestCase):
    def test_latest_completed_quarter_preserves_billions_and_excludes_other_scopes(self):
        from sovereign_macro.market_inputs import parse_bis_size
        body=document(series()+series('US',REF_SECTOR='S13')+series('JP',VALUATION='M'))
        rows=parse_bis_size(body,date(2026,10,5))
        self.assertEqual(set(rows),{'KOR'})
        self.assertEqual(rows['KOR']['value'],120)
        self.assertEqual(rows['KOR']['period'],'2026-Q2')
        self.assertEqual(rows['KOR']['unit'],'USD_billion')

    def test_future_quarter_does_not_replace_available_completed_quarter(self):
        from sovereign_macro.market_inputs import parse_bis_size
        row=parse_bis_size(document(series()),date(2026,4,5))['KOR']
        self.assertEqual(row['period'],'2026-Q1')

    def test_truncated_conflicting_or_invalid_values_are_rejected(self):
        from sovereign_macro.market_inputs import parse_bis_size
        from sovereign_macro.models import DataError
        bodies=[document(series())[:-6],document(series()+series()),
                document(series().replace('"120"','"nan"')),
                document(series().replace('"120"','"-1"')),
                document(series(UNIT_MULT='6')),
                document(series().replace('CONF_STATUS="F"','CONF_STATUS="C"'))]
        for body in bodies:
            with self.subTest(body=body[-100:]),self.assertRaises(DataError):
                parse_bis_size(body,date(2026,10,5))

    def test_structural_staleness_is_separate_from_seven_day_yield_rule(self):
        from sovereign_macro.market_inputs import parse_bis_size
        row=parse_bis_size(document(series()),date(2028,1,1))['KOR']
        self.assertEqual(row['status'],'STALE')
        self.assertIsNone(row['value'])

    def test_size_is_reported_without_fabricating_market_score_and_public_values_are_hidden(self):
        config=load_config();day=date(2026,10,5);bundle=demo_bundle(config,day)
        bundle['market_inputs']={'size':{'KOR':dict(value=120,period='2026-Q2',unit='USD_billion',
            status='AVAILABLE',provider='bis',redistribution='pending',url='https://stats.bis.org/api/v1/data/test')},'errors':[]}
        private=evaluate(config,bundle,day)
        row=next(r for r in private['rows'] if r['iso3']=='KOR')
        self.assertEqual(row['market_inputs']['size']['value'],120)
        self.assertIsNone(row['market_quality_norm']);self.assertIsNone(row['adjusted'])
        self.assertIn('Market Quality Inputs',render_summary_text(build_executive_summary(private)))
        public=evaluate(config,bundle,day,public_output=True)
        row=next(r for r in public['rows'] if r['iso3']=='KOR')
        self.assertIsNone(row['market_inputs']['size'].get('value'))
        self.assertEqual(row['market_inputs']['size']['status'],'REDISTRIBUTION_PENDING')

    def test_optional_collection_failure_is_recorded_without_failing_other_inputs(self):
        from sovereign_macro.market_inputs import collect_market_inputs
        class Offline:
            def fetch(self,url): raise TimeoutError('offline')
        result=collect_market_inputs(Offline(),{'enabled':True},date(2026,10,5))
        self.assertEqual(result['size'],{})
        self.assertEqual(result['errors'],['SIZE:TimeoutError:offline'])

    def test_collector_keeps_raw_hash_retrieval_time_and_contract_query(self):
        from sovereign_macro.market_inputs import collect_market_inputs
        from sovereign_macro.http import Payload
        class Client:
            def fetch(self,url):
                self.url=url
                return Payload(document(series()),url,'2026-10-05T01:00:00Z','raw-hash')
        client=Client();result=collect_market_inputs(client,{'enabled':True},date(2026,10,5))
        self.assertIn('.XW.S1311.S1.N.L.LE.F3.T._Z.USD._T.N.V.N._T?',client.url)
        self.assertEqual(result['size']['KOR']['raw_sha256'],'raw-hash')
        self.assertEqual(result['size']['KOR']['retrieved_at'],'2026-10-05T01:00:00Z')

    def test_entire_public_row_gate_also_hides_otherwise_cleared_size(self):
        config=load_config();day=date(2026,10,5);bundle=demo_bundle(config,day)
        bundle['market_inputs']={'size':{'KOR':dict(value=120,period='2026-Q2',status='AVAILABLE',redistribution='allowed')},'errors':[]}
        row=next(r for r in evaluate(config,bundle,day,public_output=True)['rows'] if r['iso3']=='KOR')
        self.assertIsNone(row['market_inputs']['size'].get('value'))
