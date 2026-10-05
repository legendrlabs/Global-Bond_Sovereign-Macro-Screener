"""WGB sovereign yields, with explicit identity, dates and raw response evidence."""
from datetime import date
import json
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .models import DataError, Observation, finite

BASE = 'https://www.worldgovernmentbonds.com'
COUNTRY_API = BASE + '/wp-json/country/v1/main'
HISTORY_API = BASE + '/wp-json/common/v1/historical'
TOLERANCE = 0.0005
MONTHS = {m.lower(): n for n, m in enumerate(
    ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'), 1)}


def norm(text):
    return ' '.join(text.split()).lower()


def number(value):
    if isinstance(value, bool): raise DataError('WGB_NONFINITE')
    try: value = float(value)
    except (ValueError, TypeError) as exc: raise DataError('WGB_VALUE_SCHEMA') from exc
    if not finite(value): raise DataError('WGB_NONFINITE')
    return value


def percent(text):
    m = re.fullmatch(r'(-?\d+(?:\.\d+)?)\s*%', text.strip())
    if not m: raise DataError('WGB_PERCENT_SCHEMA')
    return number(m.group(1))


def context(payload, slug, tenor=None):
    m = re.search(r'var\s+jsGlobalVars\s*=\s*(\{.*?\});', payload.body.decode('utf-8'), re.S)
    if not m: raise DataError('WGB_CONTEXT_SCHEMA')
    try: gv = json.loads(m.group(1))
    except ValueError as exc: raise DataError('WGB_CONTEXT_SCHEMA') from exc
    if (not isinstance(gv, dict) or not isinstance(gv.get('COUNTRY1'), dict)
            or gv['COUNTRY1'].get('URL_PAGE') != slug
            or gv.get('COUNTRY2') is not None or gv.get('OBJ2') is not None
            or gv.get('DOMESTIC') is not True
            or gv.get('FUNCTION') != ('Country' if tenor is None else 'Bond')):
        raise DataError('WGB_COUNTRY_CONTEXT')
    if tenor is not None:
        if (not isinstance(gv.get('OBJ1'), dict) or gv['OBJ1'].get('DURATA') != tenor * 12
                or not isinstance(gv.get('OBJ'), dict) or gv['OBJ'].get('UNIT') != '%'
                or gv.get('ENDPOINT') != HISTORY_API):
            raise DataError('WGB_TENOR_UNIT_ENDPOINT')
    return gv


def matched_row(table, tenor):
    rows = []
    for tr in table.find_all('tr'):
        cells = tr.find_all('td', recursive=False)
        if len(cells) >= 3 and norm(cells[1].get_text(' ')) == f'{tenor} years':
            rows.append((tr, cells))
    if len(rows) != 1: raise DataError('WGB_MATURITY_MISSING_OR_DUPLICATE')
    tr, cells = rows[0]
    if 'discontinued-row' in tr.get('class', []): raise DataError('WGB_DISCONTINUED')
    return cells


def curve_row(html, tenor):
    if not isinstance(html, str): raise DataError('WGB_CURVE_SCHEMA')
    table = BeautifulSoup(html, 'html.parser').find('table', id='table-curve')
    if table is None: raise DataError('WGB_CURVE_SCHEMA')
    first = table.find('thead')
    first = first.find('tr') if first else None
    header_cells = first.find_all('th', recursive=False) if first else []
    heads = [norm(th.get_text(' ')) for th in header_cells]
    if (heads[:3] != ['', 'residual maturity', 'annualized yield']
            or heads[-1:] != ['last update'] or heads.count('last update') != 1):
        raise DataError('WGB_CURVE_SCHEMA')
    cells = matched_row(table, tenor)
    try:
        spans = [int(th.get('colspan', 1)) for th in header_cells]
    except (TypeError, ValueError) as exc: raise DataError('WGB_CURVE_SCHEMA') from exc
    if any(s < 1 or s > 30 for s in spans) or len(cells) != sum(spans):
        raise DataError('WGB_CURVE_SCHEMA')
    link = cells[1].find('a', href=True)
    if link is None: raise DataError('WGB_HISTORY_LINK')
    return percent(cells[2].get_text(' ')), norm(cells[-1].get_text(' ')), link['href']


def price_yield(html, tenor):
    if not isinstance(html, str) or not html.strip(): return None
    matches = []
    for table in BeautifulSoup(html, 'html.parser').find_all('table'):
        heads = [norm(th.get_text(' ')) for th in table.find_all('th')]
        if heads[:3] == ['', 'residual maturity', 'yield'] and any('bond price' in h for h in heads):
            matches.append(table)
    if not matches: return None
    if len(matches) != 1: raise DataError('WGB_PRICES_SCHEMA')
    return percent(matched_row(matches[0], tenor)[2].get_text(' '))


def history_point(data, as_of):
    if not isinstance(data, dict) or data.get('success') is not True:
        raise DataError('WGB_HISTORY_SCHEMA')
    result = data.get('result')
    if not isinstance(result, dict) or not isinstance(result.get('quote'), dict) or not result['quote']:
        raise DataError('WGB_HISTORY_SCHEMA')
    points = {}
    for item in result['quote'].values():
        try:
            day = date.fromisoformat(item['DATA_VAL'])
            value = number(item['CLOSE_VAL'])
        except (KeyError, TypeError, ValueError) as exc:
            raise DataError('WGB_HISTORY_POINT_SCHEMA') from exc
        if day in points and points[day] != value: raise DataError('WGB_CONFLICTING_DUPLICATE')
        points[day] = value
    last = max(points)
    if last > as_of: raise DataError('FUTURE_OBSERVATION')
    current = number(result.get('ultimoValore'))
    if abs(current - points[last]) > TOLERANCE + 1e-12: raise DataError('WGB_VALUE_MISMATCH')
    return last, points[last], result.get('ultimoTimestamp', '')


def row_date(text, history_date):
    match = re.fullmatch(r'(\d{1,2}) ([a-z]{3})(?: (\d{4}))?', text)
    if not match or match[2] not in MONTHS: raise DataError('WGB_ROW_DATE_SCHEMA')
    day, month = int(match[1]), MONTHS[match[2]]
    try:
        if match[3]: return date(int(match[3]), month, day)
        candidates = []
        for year in (history_date.year - 1, history_date.year, history_date.year + 1):
            try: candidates.append(date(year, month, day))
            except ValueError: pass
        if not candidates: raise DataError('WGB_ROW_DATE_SCHEMA')
        # A curve row may be either newer or older than the last history point.
        # Infer the nearby year; the caller independently rejects future dates.
        return min(candidates, key=lambda d: (abs((d-history_date).days), d))
    except ValueError as exc: raise DataError('WGB_ROW_DATE_SCHEMA') from exc


def collect_wgb(client, country, as_of, tenor=5, stale_days=7):
    if tenor not in (5, 10): raise DataError('TENOR_NOT_IMPLEMENTED')
    slug = country.get('wgb_slug', '')
    if not re.fullmatch(r'[a-z]+(?:-[a-z]+)*', slug): raise DataError('WGB_COUNTRY_ROUTE')
    page_url = f'{BASE}/country/{slug}/'
    hist_url = f'{BASE}/bond-historical-data/{slug}/{tenor}-years/'
    evidence = []

    def fetch(url, referer=None, gv=None):
        headers = {'Origin': BASE, 'Referer': referer or BASE + '/'}
        if gv is not None:
            headers.update({'Content-Type':'application/json; charset=UTF-8', 'Accept':'application/json'})
        payload = client.fetch(url, method='POST' if gv is not None else 'GET',
                               body=json.dumps({'GLOBALVAR': gv}) if gv is not None else None,
                               headers=headers)
        if payload.url != url: raise DataError('WGB_UNEXPECTED_REDIRECT')
        evidence.append({'url':payload.url,'raw_sha256':payload.sha256,'retrieved_at':payload.retrieved_at})
        return payload

    gv = context(fetch(page_url), slug)
    main = fetch(COUNTRY_API, page_url, gv).json()
    if not isinstance(main, dict) or main.get('success') is not True: raise DataError('WGB_MAIN_SCHEMA')
    screen_value, screen_date, href = curve_row(main.get('mainTable'), tenor)
    if urljoin(page_url, href) != hist_url: raise DataError('WGB_HISTORY_LINK')
    prices = price_yield(main.get('bondPrices'), tenor)
    hgv = context(fetch(hist_url, page_url), slug, tenor)
    payload = fetch(HISTORY_API, hist_url, hgv)
    hist_date, value, source_timestamp = history_point(payload.json(), as_of)
    if abs(screen_value - value) > TOLERANCE + 1e-12:
        raise DataError('WGB_VALUE_MISMATCH')
    if prices is not None and abs(prices - value) > TOLERANCE + 1e-12:
        raise DataError('WGB_VALUE_MISMATCH')
    observed = row_date(screen_date, hist_date)
    if observed > as_of: raise DataError('FUTURE_OBSERVATION')
    warnings = []
    if observed != hist_date: warnings.append('WGB_DATE_DISCREPANCY')
    if prices is None: warnings.append('WGB_PRICE_CROSSCHECK_UNAVAILABLE')
    observed = min(observed, hist_date)
    notes = {'warnings':warnings, 'curve_row_date':screen_date, 'history_date':hist_date.isoformat(),
             'curve_yield':screen_value, 'price_yield':prices, 'raw_evidence':evidence}
    obs = Observation(country['iso3'], f'yield_{tenor}y', value, observed.isoformat(), country['currency'],
                      provider='wgb', dataset='worldgovernmentbonds', series=f'{slug}:{tenor}Y',
                      source_date=source_timestamp, retrieved_at=payload.retrieved_at, url=hist_url,
                      raw_sha256=payload.sha256, tenor_years=tenor, yield_type='annualized_government_yield',
                      redistribution='pending', notes=json.dumps(notes, ensure_ascii=False))
    obs.valid_on(as_of, stale_days)
    return obs
