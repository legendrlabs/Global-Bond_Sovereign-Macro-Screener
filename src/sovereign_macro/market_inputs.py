"""Source-backed structural inputs; no invented Market Quality composite."""
from calendar import monthrange
from copy import deepcopy
from datetime import date
import json
import re
import xml.etree.ElementTree as ET

from .models import DataError, finite

AREA_TO_ISO3=dict(zip(
    'IS NO AU NZ KR CZ BG CA IE DK LT SE HR NL SI DE SK AT PT IL ES GB FR IT BE US JP'.split(),
    'ISL NOR AUS NZL KOR CZE BGR CAN IRL DNK LTU SWE HRV NLD SVN DEU SVK AUT PRT ISR ESP GBR FRA ITA BEL USA JPN'.split()))
BIS_API='https://stats.bis.org/api/v1/data/WS_NA_SEC_DSS/'
SIZE_CONTRACT=dict(FREQ='Q',ADJUSTMENT='N',COUNTERPART_AREA='XW',REF_SECTOR='S1311',
    COUNTERPART_SECTOR='S1',CONSOLIDATION='N',ACCOUNTING_ENTRY='L',STO='LE',INSTR_ASSET='F3',
    MATURITY='T',EXPENDITURE='_Z',UNIT_MEASURE='USD',CURRENCY_DENOM='_T',VALUATION='N',
    PRICES='V',TRANSFORMATION='N',CUST_BREAKDOWN='_T')


def quarter_end(period):
    match=re.fullmatch(r'(\d{4})-Q([1-4])',period)
    if not match: raise DataError('BIS_QUARTER_SCHEMA')
    year,q=map(int,match.groups());month=q*3
    return date(year,month,monthrange(year,month)[1])


def parse_bis_size(body,as_of,max_age_days=365):
    try: root=ET.fromstring(body)
    except ET.ParseError as exc: raise DataError('BIS_XML_SCHEMA') from exc
    if root.tag.split('}')[-1]!='StructureSpecificData': raise DataError('BIS_XML_SCHEMA')
    points={}
    for series in root.iter():
        if series.tag.split('}')[-1]!='Series': continue
        area=series.get('REF_AREA')
        if area not in AREA_TO_ISO3: continue
        if any(series.get(k)!=v for k,v in SIZE_CONTRACT.items()): continue
        if series.get('UNIT_MULT')!='9': raise DataError('BIS_UNIT_MULTIPLIER')
        for obs in series:
            if obs.tag.split('}')[-1]!='Obs': continue
            period=obs.get('TIME_PERIOD','');observed=quarter_end(period)
            if observed>as_of: continue
            if obs.get('CONF_STATUS')!='F': raise DataError('BIS_CONFIDENTIALITY_UNVERIFIED')
            try: value=float(obs.get('OBS_VALUE',''))
            except ValueError as exc: raise DataError('BIS_VALUE_SCHEMA') from exc
            if not finite(value) or value<0: raise DataError('BIS_VALUE_SCHEMA')
            key=(AREA_TO_ISO3[area],period)
            if key in points: raise DataError('BIS_DUPLICATE_OBSERVATION')
            points[key]=(observed,value)
    result={}
    for (iso,period),(observed,value) in sorted(points.items()):
        if iso in result and result[iso]['observation_date']>=observed.isoformat(): continue
        age=(as_of-observed).days
        result[iso]=dict(provider='bis',metric='central_government_debt_securities_outstanding',
            value=value if age<=max_age_days else None,unit='USD_billion',period=period,
            observation_date=observed.isoformat(),age_days=age,status='AVAILABLE' if age<=max_age_days else 'STALE',
            definition='central government excluding social security; nominal value; all currencies; all original maturities; all markets')
    return result


def collect_market_inputs(client,settings,as_of):
    if not settings.get('enabled',False): return dict(size={},errors=['SOURCE_NOT_CONNECTED'])
    areas='+'.join(AREA_TO_ISO3)
    key=f'Q.N.{areas}.XW.S1311.S1.N.L.LE.F3.T._Z.USD._T.N.V.N._T'
    url=BIS_API+key+f'?startPeriod={as_of.year-1}-Q1&endPeriod={as_of.year}-Q{(as_of.month-1)//3+1}'
    try:
        payload=client.fetch(url)
        if payload.url!=url: raise DataError('BIS_UNEXPECTED_REDIRECT')
        size=parse_bis_size(payload.body,as_of,settings.get('size_max_age_days',365))
        for row in size.values():
            row.update(url=payload.url,raw_sha256=payload.sha256,retrieved_at=payload.retrieved_at,
                       redistribution=settings.get('redistribution','pending'))
        return dict(size=size,errors=[])
    except Exception as exc:
        return dict(size={},errors=['SIZE:'+type(exc).__name__+':'+str(exc)[:180]])


def country_market_inputs(iso,bundle,demo=False,public_output=False):
    inputs=bundle.get('market_inputs',{})
    size=deepcopy(inputs.get('size',{}).get(iso))
    if size is None:
        reason='; '.join(inputs.get('errors',[])) or 'BIS_SERIES_NOT_REPORTED_IN_SELECTED_SCOPE'
        size=dict(value=None,unit='USD_billion',period='',provider='bis',status='UNAVAILABLE',reason=reason)
    if demo:
        size.update(value=None,status='SYNTHETIC_DEMO')
    elif public_output and size.get('value') is not None and size.get('redistribution','pending')!='allowed':
        size.update(value=None,status='REDISTRIBUTION_PENDING')
    credit=dict(value=None,status='SOURCE_NOT_CONNECTED',reason='Same-agency long-term local-currency rating and dated source not verified')
    observation=bundle.get('yields',{}).get(iso+':5')
    if observation is not None and observation.provider=='wgb':
        try:
            reported=json.loads(observation.notes).get('reported_credit')
            if isinstance(reported,dict): credit=deepcopy(reported)
        except (ValueError,TypeError,AttributeError): pass
    if demo:
        credit=dict(value=None,status='SYNTHETIC_DEMO',reason='No real reported rating in synthetic demo')
    elif public_output and credit.get('rating'):
        credit={k:v for k,v in credit.items() if k not in ('rating','outlook','action')}
        credit.update(status='REDISTRIBUTION_PENDING',reason='Reported rating omitted from public output')
    result=dict(size=size,
        liquidity=dict(value=None,status='SOURCE_NOT_CONNECTED',reason='Comparable sovereign liquidity level / turnover not verified'),
        credit=credit,
        accessibility=dict(value=None,status='SOURCE_NOT_CONNECTED',reason='Dated bond-market accessibility input not connected'),
        composite_status='MODEL_NOT_IMPLEMENTED')
    if public_output:
        for component in ('size','liquidity','credit','accessibility'):
            if result[component].get('value') is None: result[component].pop('value',None)
    return result
