"""Dated issuer-reported S&P diagnostics, never a credit score."""
from datetime import date
import re
from bs4 import BeautifulSoup
from .models import DataError

SOURCES = {
    'NZL': ('nzdm', 'https://debtmanagement.treasury.govt.nz/investor-resources/credit-ratings',
            'Credit Ratings', ['Rating Agency', 'Domestic Currency', 'Foreign Currency', 'Latest update'], 'S&P Global Ratings'),
    'DEU': ('finanzagentur', 'https://www.deutsche-finanzagentur.de/en/federal-funding/government-as-issuer/ratings',
            'Ratings of the Federal Republic of Germany', ['Agency', 'long term', 'short term', 'outlook', 'date report'], 'Standard & Poors'),
    'FRA': ('aft', 'https://www.aft.gouv.fr/en/frances-credit-ratings',
            'France’s credit ratings', ['Agency', 'Rating', 'Outlook', 'Latest rating', 'Next rating date'], "Standard & Poor's"),
    'BEL': ('belgian_debt_agency', 'https://www.debtagency.be/en/datafederalstaterating',
            'Federal Government', ['RATING AGENCY', 'CURRENT RATING', 'EXPECTED DATE OF THE NEXT REVIEW'], 'Standard & Poors'),
    'DNK': ('nationalbanken', 'https://www.nationalbanken.dk/en/government-debt/investor-relations/rating',
            'Rating', ['', 'Domestic debt', 'Foreign debt', 'Outlook', 'Most recently confirmed'], 'Standard & Poor’s'),
    'SVK': ('nbs', 'https://nbs.sk/en/about-the-bank/international-relations/international-institutions/rating/',
            'Credit rating', ['Agency', 'Grade', 'Last change'], 'Standard & Poor’s'),
}
BASIS_URL = 'https://debtmanagement.treasury.govt.nz/resource/new-zealand-government-securities-overview-2026-27'
GRADES = {'AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-',
          'BB+', 'BB', 'BB-', 'B+', 'B', 'B-', 'CCC+', 'CCC', 'CCC-', 'CC', 'C', 'SD', 'D'}
OUTLOOKS = {'stable': 'Stable', 'positive': 'Positive', 'negative': 'Negative', 'developing': 'Developing'}
MONTHS = {name: i for i, name in enumerate(
    'January February March April May June July August September October November December'.split(), 1)}


def _norm(value):
    return ' '.join(value.replace('’', "'").split()).casefold()


def _row(body, heading, headers, agency, caption=None, *, section=None, subheaders=None, transposed=False):
    if len(body) > 2_000_000: raise DataError('ISSUER_BODY_LIMIT')
    soup = BeautifulSoup(body, 'html.parser')
    if _norm(heading) not in {_norm(h.get_text(' ', strip=True)) for h in soup.find_all('h1')}:
        raise DataError('ISSUER_HEADING_SCHEMA')
    if section is not None and _norm(section) not in {
            _norm(h.get_text(' ', strip=True)) for h in soup.find_all(['h2', 'h3'])}:
        raise DataError('ISSUER_COUNTRY_SECTION_SCHEMA')
    tables = soup.find_all('table')
    if len(tables) > 64: raise DataError('ISSUER_TABLE_LIMIT')
    matches = []
    for table in tables:
        if caption is not None:
            label = table.find('caption')
            if label is None or _norm(label.get_text(' ', strip=True)) != _norm(caption): continue
        rows = table.find_all('tr')
        if not rows: continue
        if len(rows) > 1000: raise DataError('ISSUER_ROW_LIMIT')
        matrix = [[c.get_text(' ', strip=True) for c in tr.find_all(['th', 'td'], recursive=False)] for tr in rows]
        if transposed:
            if not matrix[0] or any(len(r) != len(matrix[0]) for r in matrix): continue
            matrix = list(map(list, zip(*matrix)))
        names = matrix[0]
        if len(names) < len(headers) or any(names[len(headers):]): continue
        if [_norm(n) for n in names[:len(headers)]] != [_norm(h) for h in headers]: continue
        offset = 1
        if subheaders is not None:
            spans = [c.get('colspan', '1') for c in rows[0].find_all(['th', 'td'], recursive=False)]
            if spans != ['1', '2', '2', '1', '1']: continue
            if len(matrix) < 2 or [_norm(n) for n in matrix[1]] != [_norm(n) for n in subheaders]: continue
            offset = 2
        for cells in matrix[offset:]:
            if cells and _norm(cells[0]) == _norm(agency):
                expected = len(subheaders) if subheaders is not None else len(headers)
                if len(cells) < expected or any(cells[expected:]): raise DataError('ISSUER_ROW_SCHEMA')
                matches.append(cells)
    if len(matches) != 1: raise DataError('ISSUER_UNIQUE_AGENCY_SCHEMA')
    return matches[0]


def _dated(text, as_of, style=None):
    try:
        if style == 'dot':
            match = re.fullmatch(r'(\d{2})\.(\d{2})\.(\d{4})', text)
            if not match: raise ValueError('date format')
            day, month, year = map(int, match.groups())
            result = date(year, month, day)
        elif style == 'short_month':
            match = re.fullmatch(r'(\d{2})-([A-Za-z]{3})-(\d{4})', text)
            if not match: raise ValueError('date format')
            day, month, year = match.groups()
            number = {m[:3]: n for m, n in MONTHS.items()}[month]
            result = date(int(year), number, int(day))
        elif style == 'month_first':
            match = re.fullmatch(r'([A-Za-z]+) (\d{1,2}), (\d{4})', text)
            if not match: raise ValueError('date format')
            month, day, year = match.groups()
            result = date(int(year), MONTHS[month], int(day))
        elif re.fullmatch(r'\d{4}-\d{2}-\d{2}', text):
            result = date.fromisoformat(text)
        else:
            match = re.fullmatch(r'(\d{1,2}) ([A-Za-z]+) (\d{4})', text)
            if not match: raise ValueError('date format')
            day, month, year = match.groups()
            result = date(int(year), MONTHS[month], int(day))
    except (ValueError, KeyError) as exc:
        raise DataError('ISSUER_DATE_SCHEMA') from exc
    if result > as_of: raise DataError('ISSUER_FUTURE_ASSESSMENT')
    return result.isoformat()


def _grade(value):
    if value not in GRADES: raise DataError('ISSUER_GRADE_SCHEMA')
    return value


def _outlook(value):
    if _norm(value) not in OUTLOOKS: raise DataError('ISSUER_OUTLOOK_SCHEMA')
    return OUTLOOKS[_norm(value)]


def _nz_values(cells, as_of):
    values = []
    for text in cells[1:3]:
        match = re.fullmatch(r'([A-Z]+[+-]?)\s*\(([^()]+) outlook\)', text)
        if not match: raise DataError('ISSUER_RATING_OUTLOOK_SCHEMA')
        values.extend((_grade(match[1]), _outlook(match[2])))
    return values, _dated(cells[3], as_of)


def parse_issuer_credit(iso, body, as_of, basis_body=None):
    if iso not in SOURCES: raise DataError('ISSUER_UNSUPPORTED_COUNTRY')
    provider, url, heading, headers, agency = SOURCES[iso]
    options = {}
    if iso == 'BEL': options['section'] = "Belgium's Rating"
    if iso == 'DNK': options['subheaders'] = ['', 'Long', 'Short', 'Long', 'Short', '', '']
    if iso == 'SVK': options.update(transposed=True, section='Current Credit Rating of the Slovak Republic')
    cells = _row(body, heading, headers, agency, **options)
    row = dict(provider=provider, url=url, agency="Standard & Poor's", value=None,
               usable_for_scoring=False, redistribution='pending', status='REPORTED_TYPE_UNVERIFIED')
    if iso == 'BEL':
        match = re.fullmatch(r'([A-Z]+[+-]?) confirmed, outlook ([A-Za-z]+) \(([^()]+)\)', cells[1])
        if not match: raise DataError('ISSUER_RATING_OUTLOOK_SCHEMA')
        row.update(rating=_grade(match[1]), outlook=_outlook(match[2]), currency=None,
                   rating_kind='currency_and_term_unverified', assessment_date_type='issuer_confirmation_date')
        assessed = _dated(match[3], as_of, 'dot')
    elif iso == 'DNK':
        row.update(rating=_grade(cells[1]), foreign_rating=_grade(cells[3]), outlook=_outlook(cells[5]),
                   currency=None, rating_kind='long_term_domestic_debt_currency_unverified',
                   assessment_date_type='issuer_most_recently_confirmed')
        assessed = _dated(cells[6], as_of, 'short_month')
    elif iso == 'SVK':
        match = re.fullmatch(r'([A-Z]+[+-]?) ([A-Za-z]+) outlook', cells[1])
        if not match: raise DataError('ISSUER_RATING_OUTLOOK_SCHEMA')
        row.update(rating=_grade(match[1]), outlook=_outlook(match[2]), currency=None,
                   rating_kind='currency_and_term_unverified',
                   last_action_date=_dated(cells[2], as_of, 'month_first'), date_type='issuer_last_change',
                   reason='Official current rating summary; date is last change, not latest assessment; no credit score')
        return row
    elif iso == 'NZL':
        values, assessed = _nz_values(cells, as_of)
        row.update(rating=values[0], outlook=values[1], foreign_rating=values[2], foreign_outlook=values[3],
                   currency='NZD', rating_kind='domestic_currency_term_unverified',
                   assessment_date_type='issuer_latest_update')
        if basis_body is not None:
            try:
                basis = _row(basis_body, 'New Zealand Government Securities Overview 2026/27',
                             ['Rating Agency', 'Local Currency', 'Foreign Currency', 'Latest Update'],
                             agency, 'Table 2: New Zealand Long-term Credit Ratings')
                basis_values, basis_date = _nz_values(basis, as_of)
                if basis_values != values: raise DataError('ISSUER_BASIS_RATING_MISMATCH')
                if basis_date > assessed: raise DataError('ISSUER_BASIS_NEWER_THAN_CURRENT')
                row.update(rating_kind='long_term_local_currency', status='AVAILABLE_DIAGNOSTIC',
                           basis_assessment_date=basis_date)
            except DataError as exc:
                row['basis_verification_error'] = str(exc)
    else:
        row.update(rating=_grade(cells[1]), outlook=_outlook(cells[3 if iso == 'DEU' else 2]),
                   currency=None, rating_kind='long_term_currency_unverified' if iso == 'DEU' else 'currency_and_term_unverified',
                   assessment_date_type='issuer_report_date' if iso == 'DEU' else 'issuer_latest_rating')
        assessed = _dated(cells[4 if iso == 'DEU' else 3], as_of)
    row.update(assessment_date=assessed, assessment_age_days=(as_of-date.fromisoformat(assessed)).days,
               reason='Issuer-reported diagnostic; rating basis is explicit in rating_kind; no credit score implemented')
    return row


def _fetch(client, url):
    payload = client.fetch(url)
    if payload.url != url: raise DataError('ISSUER_UNEXPECTED_REDIRECT')
    return payload


def collect_issuer_credit(client, settings, as_of):
    result = {}
    for iso, (provider, url, *_rest) in SOURCES.items():
        try:
            payload = _fetch(client, url)
            basis = None
            basis_error = None
            if iso == 'NZL':
                try: basis = _fetch(client, BASIS_URL)
                except Exception as exc: basis_error = type(exc).__name__ + ':' + str(exc)[:120]
            row = parse_issuer_credit(iso, payload.body, as_of, basis.body if basis else None)
            row.update(raw_sha256=payload.sha256, retrieved_at=payload.retrieved_at, transport=payload.transport)
            if basis is not None:
                row.update(basis_url=BASIS_URL, basis_sha256=basis.sha256,
                           basis_retrieved_at=basis.retrieved_at, basis_transport=basis.transport)
            if basis_error: row['basis_verification_error'] = basis_error
            result[iso] = row
        except Exception as exc:
            result[iso] = dict(provider=provider, url=url, value=None, status='UNAVAILABLE',
                               usable_for_scoring=False, reason=type(exc).__name__ + ':' + str(exc)[:120])
    return result


def redact_credit(row):
    has_grade = bool(row.get('rating') or row.get('foreign_rating'))
    for key in ('rating', 'foreign_rating', 'outlook', 'foreign_outlook', 'action'):
        row.pop(key, None)
    if has_grade:
        row.update(status='REDISTRIBUTION_PENDING', reason='Reported rating omitted from public output')
