"""Synthetic issuer tables test classification, dates and privacy, not live grades."""
from datetime import date
from html import escape
import json
import unittest

from sovereign_macro.models import DataError
from sovereign_macro.http import Payload


DAY=date(2026,10,7)
NZ='https://debtmanagement.treasury.govt.nz/investor-resources/credit-ratings'
BASIS='https://debtmanagement.treasury.govt.nz/resource/new-zealand-government-securities-overview-2026-27'
DE='https://www.deutsche-finanzagentur.de/en/federal-funding/government-as-issuer/ratings'
FR='https://www.aft.gouv.fr/en/frances-credit-ratings'


def table(heads,rows,caption=''):
    cells=lambda row,tag: ''.join(f'<{tag}>{escape(str(x))}</{tag}>' for x in row)
    return '<table><caption>'+caption+'</caption><tr>'+cells(heads,'th')+'</tr>'+''.join(
        '<tr>'+cells(row,'td')+'</tr>' for row in rows)+'</table>'


def nz(rating='AA', foreign='AA-', day='11 September 2026', duplicate=False, basis=False):
    row=['S&P Global Ratings',f'{rating} (stable outlook)',f'{foreign} (stable outlook)',day]
    heads=['Rating Agency','Local Currency' if basis else 'Domestic Currency','Foreign Currency','Latest update']
    return ('<h1>'+('New Zealand Government Securities Overview 2026/27' if basis else 'Credit Ratings')+'</h1>'+
        table(heads,[['Fitch Ratings','AAA (negative outlook)','AAA (negative outlook)','1 August 2026'],row]+([row] if duplicate else []),
              'Table 2: New Zealand Long-term Credit Ratings' if basis else "New Zealand's current credit ratings")+
        '<p>Last updated: 1 January 2020</p>').encode()


def de(day='2026-09-12'):
    return ('<h1>Ratings of the Federal Republic of Germany</h1>'+table(
        ['Agency','long term','short term','outlook','date report','',''],
        [['Standard & Poors','AA','A-1+','stable',day,'','']])).encode()


def fr(day='13 September 2026',next_day='11 December 2026'):
    return ("<h1>France’s credit ratings</h1>"+table(
        ['Agency','Rating','Outlook','Latest rating','Next rating date'],
        [["Standard & Poor's",'BBB+','Negative',day,next_day]])).encode()


class IssuerCreditTests(unittest.TestCase):
    def api(self,name):
        try:
            from sovereign_macro import issuer_credit
        except ImportError:self.fail('Missing issuer credit adapter')
        fn=getattr(issuer_credit,name,None)
        self.assertTrue(callable(fn),'Missing issuer credit function: '+name)
        return fn

    def parse(self,*args,**kwargs):
        return self.api('parse_issuer_credit')(*args,**kwargs)

    def test_nz_uses_local_column_and_current_row_date_not_overview_or_footer(self):
        row=self.parse('NZL',nz(),DAY,basis_body=nz(day='1 September 2026',basis=True))
        self.assertEqual(row['rating'],'AA');self.assertEqual(row['foreign_rating'],'AA-')
        self.assertEqual(row['assessment_date'],'2026-09-11')
        self.assertEqual(row['rating_kind'],'long_term_local_currency')
        self.assertEqual(row['basis_assessment_date'],'2026-09-01')
        self.assertEqual(row['status'],'AVAILABLE_DIAGNOSTIC')
        self.assertIsNone(row['value']);self.assertFalse(row['usable_for_scoring'])

    def test_nz_missing_or_conflicting_basis_never_claims_long_term_verification(self):
        for basis in (None,nz(rating='AAA',basis=True),nz(basis=True).replace(b'Long-term',b'Current')):
            row=self.parse('NZL',nz(),DAY,basis_body=basis)
            self.assertEqual(row['rating'],'AA')
            self.assertEqual(row['rating_kind'],'domestic_currency_term_unverified')
            self.assertEqual(row['status'],'REPORTED_TYPE_UNVERIFIED')

    def test_nz_foreign_outlook_and_basis_date_conflicts_keep_current_diagnostic(self):
        cases=[
            ('foreign grade',nz(foreign='A+',basis=True),'ISSUER_BASIS_RATING_MISMATCH'),
            ('local outlook',nz(basis=True).replace(b'AA (stable outlook)',b'AA (positive outlook)'),
             'ISSUER_BASIS_RATING_MISMATCH'),
            ('foreign outlook',nz(basis=True).replace(b'AA- (stable outlook)',b'AA- (negative outlook)'),
             'ISSUER_BASIS_RATING_MISMATCH'),
            ('newer basis date',nz(day='15 September 2026',basis=True),'ISSUER_BASIS_NEWER_THAN_CURRENT'),
        ]
        for label,basis,error in cases:
            with self.subTest(conflict=label):
                row=self.parse('NZL',nz(),DAY,basis_body=basis)
                self.assertEqual(row['rating_kind'],'domestic_currency_term_unverified')
                self.assertEqual(row['status'],'REPORTED_TYPE_UNVERIFIED')
                self.assertEqual(row['basis_verification_error'],error)
                self.assertEqual(row['rating'],'AA');self.assertEqual(row['foreign_rating'],'AA-')
                self.assertEqual(row['outlook'],'Stable');self.assertEqual(row['foreign_outlook'],'Stable')
                self.assertEqual(row['assessment_date'],'2026-09-11')
                self.assertNotIn('basis_assessment_date',row)
                self.assertIsNone(row['value']);self.assertFalse(row['usable_for_scoring'])

    def test_france_next_review_is_not_an_observation_and_types_remain_unspecified(self):
        row=self.parse('FRA',fr(),DAY)
        self.assertEqual(row['assessment_date'],'2026-09-13')
        self.assertEqual(row['rating'],'BBB+')
        self.assertEqual(row['rating_kind'],'currency_and_term_unverified')
        self.assertEqual(row['status'],'REPORTED_TYPE_UNVERIFIED')

    def test_germany_long_term_grade_does_not_claim_currency_from_summary(self):
        row=self.parse('DEU',de(),DAY)
        self.assertEqual(row['rating'],'AA');self.assertEqual(row['assessment_date'],'2026-09-12')
        self.assertEqual(row['rating_kind'],'long_term_currency_unverified')

    def test_future_impossible_duplicate_missing_or_drifted_rows_fail_closed(self):
        cases=[nz(day='8 October 2026'),nz(day='31 February 2026'),nz(duplicate=True),
               nz().replace(b'S&amp;P Global Ratings',b'Other Agency'),
               nz().replace(b'Domestic Currency',b'Foreign Currency'),nz(rating='Aaa'),
               nz().replace(b'stable outlook',b'unknown outlook'),b'<h1>Credit Ratings</h1>',
               nz().replace(b'Credit Ratings',b'Unrelated Issuer')]
        for body in cases:
            with self.subTest(body=body[:70]),self.assertRaises(DataError):self.parse('NZL',body,DAY)

    def test_collector_isolates_failure_and_records_source_and_basis_hashes(self):
        collect_issuer_credit=self.api('collect_issuer_credit')
        class Client:
            def fetch(self,url):
                if url==FR:raise TimeoutError('offline')
                bodies={NZ:nz(),BASIS:nz(day='1 September 2026',basis=True),DE:de()}
                return Payload(bodies[url],url,'2026-10-06T19:00:00Z','basis-hash' if url==BASIS else 'source-hash','', 'curl_cffi')
        rows=collect_issuer_credit(Client(),{},DAY)
        self.assertEqual(rows['FRA']['status'],'UNAVAILABLE')
        self.assertEqual(rows['NZL']['rating_kind'],'long_term_local_currency')
        self.assertEqual(rows['NZL']['raw_sha256'],'source-hash')
        self.assertEqual(rows['NZL']['basis_sha256'],'basis-hash')
        self.assertEqual(rows['DEU']['status'],'REPORTED_TYPE_UNVERIFIED')

    def test_basis_failure_keeps_reported_local_grade_and_redirects_are_rejected(self):
        collect_issuer_credit=self.api('collect_issuer_credit')
        class Client:
            def fetch(self,url):
                if url==BASIS:raise TimeoutError('basis offline')
                return Payload(nz() if url==NZ else de(),'https://unrelated.example/' if url==DE else url,'2026-10-06T19:00:00Z','hash')
        rows=collect_issuer_credit(Client(),{},DAY)
        self.assertEqual(rows['NZL']['rating'],'AA')
        self.assertEqual(rows['NZL']['status'],'REPORTED_TYPE_UNVERIFIED')
        self.assertIn('basis offline',rows['NZL']['basis_verification_error'])
        self.assertEqual(rows['DEU']['status'],'UNAVAILABLE')

    def test_redaction_removes_local_foreign_outlook_and_action_values(self):
        redact_credit=self.api('redact_credit')
        row=self.parse('NZL',nz(),DAY,basis_body=nz(basis=True));row['action']='affirmation'
        redact_credit(row)
        for key in ('rating','foreign_rating','outlook','foreign_outlook','action'):self.assertNotIn(key,row)
        self.assertEqual(row['status'],'REDISTRIBUTION_PENDING')


class IssuerIntegrationTests(unittest.TestCase):
    def credit(self):
        from sovereign_macro.issuer_credit import parse_issuer_credit
        row=parse_issuer_credit('NZL',nz(),DAY,basis_body=nz(day='1 September 2026',basis=True))
        return dict(row,raw_sha256='issuer-hash',retrieved_at='2026-10-06T19:00:00Z')

    def test_credit_collects_with_size_and_liquidity_disabled_and_global_switch_gates_it(self):
        from sovereign_macro.market_inputs import collect_market_inputs
        class Client:
            def __init__(self):self.calls=[]
            def fetch(self,url):
                self.calls.append(url)
                bodies={NZ:nz(),BASIS:nz(day='1 September 2026',basis=True),DE:de(),FR:fr()}
                return Payload(bodies[url],url,'2026-10-06T19:00:00Z','hash')
        client=Client();settings=dict(enabled=True,size_enabled=False,liquidity_enabled=False,credit_enabled=True)
        self.assertEqual(collect_market_inputs(client,settings,DAY)['credit']['NZL']['rating'],'AA')
        self.assertEqual(set(client.calls),{NZ,BASIS,DE,FR})
        for changes in ({'credit_enabled':False},{'enabled':False}):
            client=Client();collect_market_inputs(client,dict(settings,**changes),DAY)
            self.assertEqual(client.calls,[])

    def test_issuer_rating_is_independent_of_yield_provider_and_wins_over_wgb(self):
        from sovereign_macro.market_inputs import country_market_inputs
        from sovereign_macro.models import Observation
        wgb=dict(rating='B+',agency="Standard & Poor's",status='REPORTED_TYPE_UNVERIFIED',value=None)
        for provider in ('official','wgb'):
            obs=Observation('NZL','yield_5y',3,DAY.isoformat(),provider=provider,notes=json.dumps({'reported_credit':wgb}))
            bundle=dict(market_inputs={'credit':{'NZL':self.credit()}},yields={'NZL:5':obs})
            credit=country_market_inputs('NZL',bundle)['credit']
            self.assertEqual(credit['provider'],'nzdm');self.assertEqual(credit['rating'],'AA')

    def test_issuer_failure_retains_wgb_with_failure_disclosed(self):
        from sovereign_macro.market_inputs import country_market_inputs
        from sovereign_macro.models import Observation
        wgb=dict(rating='B+',provider='wgb',status='REPORTED_TYPE_UNVERIFIED',value=None)
        failure=dict(status='UNAVAILABLE',provider='nzdm',reason='HTTP_FAILURE:502',url=NZ)
        obs=Observation('NZL','yield_5y',3,DAY.isoformat(),provider='wgb',notes=json.dumps({'reported_credit':wgb}))
        credit=country_market_inputs('NZL',dict(market_inputs={'credit':{'NZL':failure}},yields={'NZL:5':obs}))['credit']
        self.assertEqual(credit['rating'],'B+')
        self.assertEqual(credit['issuer_failure']['reason'],'HTTP_FAILURE:502')

    def test_report_and_provenance_preserve_kind_date_and_hide_all_grade_copies(self):
        from sovereign_macro.config import load_config
        from sovereign_macro.pipeline import demo_bundle,evaluate
        from sovereign_macro.summary import build_executive_summary,render_summary_text
        config=load_config();bundle=demo_bundle(config,DAY)
        bundle['market_inputs']={'credit':{'NZL':self.credit()}}
        private=evaluate(config,bundle,DAY)
        row=next(r for r in private['rows'] if r['iso3']=='NZL')
        self.assertTrue(any(p.get('raw_sha256')=='issuer-hash' for p in row['provenance']))
        self.assertIsNone(row['adjusted']);self.assertIsNone(row['market_quality_norm'])
        text=render_summary_text(build_executive_summary(private))
        self.assertIn('long_term_local_currency',text);self.assertIn('2026-09-11',text)
        for options in ({'public_output':True},{'demo':True}):
            result=evaluate(config,bundle,DAY,**options)
            row=next(r for r in result['rows'] if r['iso3']=='NZL')
            for item in [row['market_inputs']['credit']]+row['provenance']:
                for key in ('rating','foreign_rating','outlook','foreign_outlook','action'):
                    self.assertNotIn(key,item)
            if options.get('public_output'):
                self.assertTrue(any(p.get('raw_sha256')=='issuer-hash' for p in row['provenance']))
            if options.get('demo'):
                self.assertNotIn('raw_sha256',row['market_inputs']['credit'])
                self.assertFalse(any(p.get('raw_sha256')=='issuer-hash' for p in row['provenance']))
        self.assertEqual(bundle['market_inputs']['credit']['NZL']['rating'],'AA')

    def test_issuer_hosts_only_use_compatible_transport(self):
        import tempfile
        from sovereign_macro.http import HttpClient
        from test_http import Browser,Session,response
        for url in (NZ,DE,FR):
            with self.subTest(url=url),tempfile.TemporaryDirectory() as tmp:
                browser=Browser([response(200,b'issuer')]);session=Session([])
                payload=HttpClient(tmp,session,browser_transport=browser.request).fetch(url)
                self.assertEqual(payload.transport,'curl_cffi')
                self.assertEqual(browser.calls[0][1]['timeout'],20)
        with tempfile.TemporaryDirectory() as tmp:
            browser=Browser([]);session=Session([response(200,b'plain')])
            client=HttpClient(tmp,session,browser_transport=browser.request)
            self.assertEqual(client.fetch('https://www.aft.gouv.fr.example.org/data').transport,'requests')


if __name__=='__main__':unittest.main()
