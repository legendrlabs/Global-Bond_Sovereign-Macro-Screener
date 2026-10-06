"""ADB government-bond turnover diagnostics; never a comparable 5Y score."""
from calendar import monthrange
import csv
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from io import StringIO
from urllib.parse import urlencode

from .models import DataError, finite

ADB_CSV='https://asianbondsonline.adb.org/downloads/bond_turn_ratio_csv.php'
ADB_DEFINITION='https://asianbondsonline.adb.org/xml/get-indicator.php?code=Bond_turn_ratio'
ADB_NOTES='https://asianbondsonline.adb.org/charts/bond_turn_ratio.php'
ECONOMIES={'KR':'KOR','JP':'JPN'}
NUMERIC_FIELDS=('value','traded_value','average_outstanding')
HEADER=('Economy','Date','Govt Bonds Turnover(LCY billions)',
        'Ave Govt Bonds Outstanding(LCY billions)','Govt BondsTurnover Ratio',
        'Corp Bonds Turnover(LCY billions)','Ave Corp Bonds Outstanding(LCY billions)',
        'Corp BondsTurnover Ratio')


def redact_turnover(row, status):
    """Also remove the amounts from which a hidden ratio could be recovered."""
    had_value=any(row.get(k) is not None for k in NUMERIC_FIELDS)
    for key in NUMERIC_FIELDS: row.pop(key,None)
    if had_value: row['status']=status


def metadata(economy):
    scope=('OTC only; government category includes municipal, government-guaranteed, FILP-agency '
           'and transportation/NHK bonds; all maturities' if economy=='JP' else
           'OTC only; precise government-category composition remains unverified; all maturities')
    return dict(provider='adb',metric='government_bond_turnover_ratio',frequency='quarterly',
        unit='turns_per_quarter',amount_unit='LCY_billion',currency='JPY' if economy=='JP' else 'KRW',
        upstream_provider='JSDA' if economy=='JP' else 'KG Zeroin',
        definition='Quarterly government-bond traded value / average outstanding at previous and current '
                   'quarter ends; local currency; repo excluded; published ratio rounded to two decimals. '
                   'ADB already halves reported sales plus purchases; no further division applied. '+scope,
        definition_url=ADB_DEFINITION,country_notes_url=ADB_NOTES,
        usable_for_scoring=False,
        reason='Source-specific government categories and OTC coverage are not harmonized; not a single-5Y measure')


def decimal_value(value):
    try: result=Decimal(value)
    except (InvalidOperation,TypeError,ValueError) as exc: raise DataError('ADB_VALUE_SCHEMA') from exc
    if not result.is_finite() or result<0 or not finite(float(result)):
        raise DataError('ADB_VALUE_SCHEMA')
    return result


def parse_adb_turnover(body,as_of,max_age_days=185):
    try:
        text=body.decode('utf-8-sig');lines=text.splitlines()
        start=next(i for i,line in enumerate(lines) if line.startswith('Economy,Date,'))
        prefix='\n'.join(lines[:start])
        if ('Indicator: Bonds Turnover Ratio' not in prefix or
            'Definition: Quarterly Bond turnover ratio = Value of bonds traded' not in prefix or
            'Average amount of bonds outstanding' not in prefix or
            'Frequency: Quarterly updates' not in prefix):
            raise DataError('ADB_DEFINITION_UNVERIFIED')
        reader=csv.DictReader(StringIO('\n'.join(lines[start:])),strict=True)
        if tuple(reader.fieldnames or ())!=HEADER: raise DataError('ADB_CSV_HEADER_SCHEMA')
        grouped={key:[] for key in ECONOMIES}
        for row in reader:
            economy=row.get('Economy')
            if economy in grouped: grouped[economy].append(row)
    except (UnicodeError,StopIteration,csv.Error) as exc:
        raise DataError('ADB_CSV_SCHEMA') from exc
    result={}
    for economy,rows in grouped.items():
        item=dict(metadata(economy),value=None,status='UNAVAILABLE')
        try:
            points={}
            for row in rows:
                if None in row or any(row.get(k) is None for k in HEADER):
                    raise DataError('ADB_ROW_SCHEMA')
                try: observed=date.fromisoformat(row['Date'])
                except (TypeError,ValueError) as exc: raise DataError('ADB_DATE_SCHEMA') from exc
                if observed.month not in (3,6,9,12) or observed.day!=monthrange(observed.year,observed.month)[1]:
                    raise DataError('ADB_QUARTER_SCHEMA')
                if observed>as_of: continue
                if observed in points: raise DataError('ADB_DUPLICATE_OBSERVATION')
                traded=decimal_value(row[HEADER[2]]);outstanding=decimal_value(row[HEADER[3]])
                ratio=decimal_value(row[HEADER[4]])
                if outstanding<=0: raise DataError('ADB_DENOMINATOR_SCHEMA')
                if (traded/outstanding).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)!=ratio:
                    raise DataError('ADB_RATIO_MISMATCH')
                points[observed]=(float(ratio),float(traded),float(outstanding))
            if points:
                observed=max(points);ratio,traded,outstanding=points[observed]
                age=(as_of-observed).days
                current=age<=max_age_days
                item.update(value=ratio if current else None,traded_value=traded if current else None,
                    average_outstanding=outstanding if current else None,
                    period=f'{observed.year}-Q{observed.month//3}',observation_date=observed.isoformat(),
                    age_days=age,status='AVAILABLE_DIAGNOSTIC' if current else 'STALE')
            else: item['reason']='ADB_NO_COMPLETED_COUNTRY_OBSERVATION'
        except (DataError,InvalidOperation) as exc:
            item.update(status='INVALID_DATA',reason=str(exc))
        result[ECONOMIES[economy]]=item
    return result


def collect_adb_turnover(client,settings,as_of):
    # Keep the prior year for January runs and publication lags; filter rows ourselves.
    query=urlencode(dict(economies='KR^JP',years=f'{as_of.year-1}^{as_of.year}',frequency='Quarterly'))
    url=ADB_CSV+'?'+query
    try:
        payload=client.fetch(url)
        if payload.url!=url: raise DataError('ADB_UNEXPECTED_REDIRECT')
        result=parse_adb_turnover(payload.body,as_of,settings.get('turnover_max_age_days',185))
        for row in result.values():
            row.update(url=payload.url,raw_sha256=payload.sha256,retrieved_at=payload.retrieved_at,
                transport=payload.transport,redistribution=settings.get('redistribution','pending'),
                country_notes_url=ADB_NOTES+'?module=data-portal&'+query)
        return result
    except Exception as exc:
        return {iso:dict(metadata(economy),value=None,status='UNAVAILABLE',url=url,
            reason=type(exc).__name__+':'+str(exc)[:180]) for economy,iso in ECONOMIES.items()}
