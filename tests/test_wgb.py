import copy
from datetime import date
import hashlib
import json
import unittest

from sovereign_macro.http import Payload
from sovereign_macro.models import DataError


BASE = 'https://www.worldgovernmentbonds.com'


def page(slug='new-zealand', tenor=None):
    gv = dict(FUNCTION='Country' if tenor is None else 'Bond', DOMESTIC=True,
              COUNTRY1={'URL_PAGE': slug}, COUNTRY2=None, OBJ2=None,
              OBJ=None if tenor is None else {'UNIT': '%'},
              OBJ1=None if tenor is None else {'DURATA': tenor * 12},
              ENDPOINT=BASE + '/wp-json/common/v1/historical')
    return ('<script>var jsGlobalVars = ' + json.dumps(gv) + ';</script>').encode()


def curve(day='05 Oct', value='4.518%', tenor=5, discontinued=False):
    cls = 'discontinued-row' if discontinued else ''
    return f'''<table id="table-curve"><thead><tr><th></th><th>Residual Maturity</th>
      <th>Annualized Yield</th><th>Last Update</th></tr></thead><tbody>
      <tr class="{cls}"><td></td><td><a href="{BASE}/bond-historical-data/new-zealand/{tenor}-years/">{tenor} years</a></td>
      <td>{value}</td><td>{day}</td></tr></tbody></table>'''


def main_data(**kw):
    return {'success': True, 'mainTable': curve(**kw), 'bondPrices': '''
      <table><thead><tr><th></th><th>Residual Maturity</th><th>Yield</th><th>Bond Price</th></tr></thead>
      <tbody><tr><td></td><td>5 years</td><td>4.518%</td><td>80.18</td></tr></tbody></table>'''}


def history(day='2026-10-05', value=4.518):
    return {'success': True, 'result': {'quote': {
        '1': {'DATA_VAL': '2026-10-02', 'CLOSE_VAL': value},
        '2': {'DATA_VAL': day, 'CLOSE_VAL': value, 'TIME_VAL': day + ' 08:15:15'}},
        'ultimoValore': value, 'ultimoTimestamp': day + ' 08:15:15'}}


class FixtureClient:
    def __init__(self, country_main=None, historical=None, hist_page=None):
        self.calls = []
        self.records = []
        self.bodies = [page(), json.dumps(country_main or main_data()).encode(),
                       hist_page or page(tenor=5), json.dumps(historical or history()).encode()]

    def fetch(self, url, method='GET', body=None, headers=None):
        self.calls.append((url, method, body, headers))
        content = self.bodies[len(self.calls)-1]
        return Payload(content, url, '2026-10-05T09:00:00Z', hashlib.sha256(content).hexdigest())


COUNTRY = {'iso3': 'NZL', 'currency': 'NZD', 'wgb_slug': 'new-zealand'}


class WgbTests(unittest.TestCase):
    def collect(self, client=None, as_of=date(2026, 10, 5)):
        from sovereign_macro.wgb import collect_wgb
        return collect_wgb(client or FixtureClient(), COUNTRY, as_of)

    def test_real_shaped_responses_preserve_percent_date_identity_and_evidence(self):
        c = FixtureClient(); obs = self.collect(c)
        self.assertEqual((obs.iso3, obs.currency, obs.tenor_years), ('NZL', 'NZD', 5))
        self.assertEqual((obs.value, obs.period, obs.unit), (4.518, '2026-10-05', 'percent'))
        self.assertEqual(obs.provider, 'wgb')
        self.assertEqual(obs.yield_type, 'annualized_government_yield')
        self.assertEqual(obs.redistribution, 'pending')
        self.assertEqual(obs.raw_sha256, hashlib.sha256(c.bodies[-1]).hexdigest())
        self.assertEqual(len(json.loads(obs.notes)['raw_evidence']), 4)
        headers = c.calls[1][3]
        self.assertEqual(headers['Origin'], BASE)
        self.assertEqual(headers['Content-Type'], 'application/json; charset=UTF-8')

    def test_matching_value_with_different_dates_uses_older_date(self):
        obs = self.collect(FixtureClient(country_main=main_data(day='02 Oct')))
        self.assertEqual(obs.period, '2026-10-02')
        self.assertIn('WGB_DATE_DISCREPANCY', json.loads(obs.notes)['warnings'])

    def test_newer_curve_date_and_older_history_also_use_older_date(self):
        obs = self.collect(FixtureClient(historical=history(day='2026-10-02')))
        self.assertEqual(obs.period, '2026-10-02')
        self.assertIn('WGB_DATE_DISCREPANCY', json.loads(obs.notes)['warnings'])

    def test_added_trailing_column_cannot_replace_actual_observation_date(self):
        d = main_data(day='01 Sep')
        d['mainTable'] = d['mainTable'].replace('<th>Last Update</th>', '<th>Last Update</th><th>Retrieved</th>')
        d['mainTable'] = d['mainTable'].replace('<td>01 Sep</td>', '<td>01 Sep</td><td>05 Oct</td>')
        with self.assertRaisesRegex(DataError, 'SCHEMA'):
            self.collect(FixtureClient(country_main=d))

    def test_future_curve_date_is_rejected_instead_of_rolling_back_a_year(self):
        with self.assertRaisesRegex(DataError, 'FUTURE'):
            self.collect(FixtureClient(country_main=main_data(day='06 Oct')))

    def test_seven_calendar_days_boundary(self):
        obs = self.collect(FixtureClient(country_main=main_data(day='28 Sep')))
        self.assertEqual(obs.period, '2026-09-28')
        with self.assertRaisesRegex(DataError, 'STALE'):
            self.collect(FixtureClient(country_main=main_data(day='27 Sep')))

    def test_new_year_uses_history_year_and_preserves_december_observation(self):
        h = history(day='2027-01-02'); h['result']['quote'] = {'1': h['result']['quote']['2']}
        obs = self.collect(FixtureClient(country_main=main_data(day='31 Dec'), historical=h), date(2027,1,2))
        self.assertEqual(obs.period, '2026-12-31')

    def test_future_and_nonfinite_history_are_rejected(self):
        for h in [history(day='2099-10-05'), history(value='NaN'), history(value='Infinity')]:
            with self.subTest(h=h), self.assertRaises(DataError): self.collect(FixtureClient(historical=h))

    def test_conflicting_duplicate_dates_are_rejected(self):
        h = history(); h['result']['quote']['3'] = {'DATA_VAL':'2026-10-05','CLOSE_VAL':9}
        with self.assertRaisesRegex(DataError, 'DUPLICATE'): self.collect(FixtureClient(historical=h))

    def test_wrong_country_tenor_unit_or_non_domestic_context_rejected(self):
        for change in [{'COUNTRY1': {'URL_PAGE':'austria'}}, {'OBJ1':{'DURATA':120}},
                       {'OBJ':{'UNIT':'bp'}}, {'COUNTRY2':{'URL_PAGE':'austria'}},
                       {'DOMESTIC':False}, {'FUNCTION':'Spread'},
                       {'ENDPOINT':'https://example.org/data'}]:
            gv = json.loads(page(tenor=5).decode().split(' = ')[1].split(';</script>')[0]); gv.update(change)
            p = ('<script>var jsGlobalVars = '+json.dumps(gv)+';</script>').encode()
            with self.subTest(change=change), self.assertRaises(DataError): self.collect(FixtureClient(hist_page=p))

    def test_discontinued_value_mismatch_and_header_changes_are_rejected(self):
        for d in [main_data(discontinued=True), main_data(value='4.600%'), main_data(value='NaN%')]:
            with self.subTest(d=d), self.assertRaises(DataError): self.collect(FixtureClient(country_main=d))
        d = main_data(); d['mainTable'] = d['mainTable'].replace('Annualized Yield', 'Bond Price')
        with self.assertRaisesRegex(DataError, 'SCHEMA'): self.collect(FixtureClient(country_main=d))

    def test_duplicate_tenor_rows_and_wrong_history_link_rejected(self):
        d = main_data(); d['mainTable'] = d['mainTable'].replace('</tbody>', d['mainTable'].split('<tbody>')[1].split('</tbody>')[0]+'</tbody>')
        with self.assertRaises(DataError): self.collect(FixtureClient(country_main=d))
        d = main_data(); d['mainTable'] = d['mainTable'].replace('/5-years/', '/10-years/')
        with self.assertRaises(DataError): self.collect(FixtureClient(country_main=d))
