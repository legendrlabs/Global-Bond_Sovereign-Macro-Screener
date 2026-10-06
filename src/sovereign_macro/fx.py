from datetime import date, timedelta
import math
import statistics
from urllib.parse import urlparse
from .models import DataError, finite


def cross_rate(rates, currency):
    denom = 1 if currency == 'EUR' else rates.get(currency)
    krw = rates.get('KRW')
    if not finite(denom) or not finite(krw) or denom <= 0 or krw <= 0:
        raise DataError('FX_MISSING_OR_INVALID')
    return krw/denom


def _anniversary(as_of, years):
    try:
        return as_of.replace(year=as_of.year-years)
    except ValueError:
        return as_of.replace(year=as_of.year-years, day=28)


def _weekday_gap(a,b):
    days=(b-a).days-1
    weeks,tail=divmod(max(days,0),7)
    return weeks*5+sum((a+timedelta(days=7*weeks+i)).weekday()<5 for i in range(1,tail+1))


def _transition_contract(transition, currency, as_of):
    """A reviewed fixed-peg contract is separate from current currency assignment."""
    try:
        old=transition['old_currency'];new=transition['new_currency']
        start=date.fromisoformat(transition['history_from'])
        effective=date.fromisoformat(transition['effective_date'])
        ratio=transition['old_units_per_new'];decimals=transition['reference_decimals']
        urls=transition['evidence_urls']
        valid=(transition['kind']=='fixed_peg_redenomination' and transition['verified'] is True
               and isinstance(old,str) and len(old)==3 and old.isupper() and old!=new
               and new==currency and new=='EUR' and start<effective<=as_of
               and finite(ratio) and not isinstance(ratio,bool) and ratio>0
               and type(decimals) is int and 0<=decimals<=8
               and isinstance(urls,list) and bool(urls)
               and all(isinstance(u,str) and urlparse(u).scheme=='https' and urlparse(u).hostname for u in urls))
    except (KeyError,TypeError,ValueError,AttributeError):
        valid=False
    if not valid: raise DataError('CURRENCY_TRANSITION_CONTRACT_INVALID')
    return start,effective,old,ratio,0.5*10**(-decimals)+1e-12


def fx_metrics(points, currency, as_of, continuity=True, min_1y=200, min_3y=600, transition=None):
    out = dict(vol_1y=None,vol_3y=None,max_drawdown=None,count_1y=0,count_3y=0,
               latest_date=None,errors=[])
    if currency == 'KRW':
        out.update(vol_1y=0.,vol_3y=0.,max_drawdown=0.,identity=True)
        return out
    if not continuity:
        out['errors'].append('CURRENCY_TRANSITION_UNVERIFIED')
        return out
    contract=_transition_contract(transition,currency,as_of) if transition is not None else None
    if contract:
        start,effective,old,ratio,tolerance=contract
        out['transition']={k:transition[k] for k in ('kind','old_currency','new_currency','history_from',
                            'effective_date','old_units_per_new','reference_decimals','evidence_urls')}
        out['transition'].update(status='VERIFIED_CONTINUITY',rebased_count=0)
    peg_breaks=[]
    dated = sorted(d for d in points if d <= as_of)
    valid = []
    for i,d in enumerate(dated):
        try:
            if contract and d<effective:
                if d<start or d<_anniversary(as_of,3): continue
                observed=points[d].get(old)
                if not finite(observed) or observed<=0: raise DataError('FX_MISSING_OR_INVALID')
                if abs(observed-ratio)>tolerance:
                    peg_breaks.append(d)
                    continue
                value=cross_rate(points[d],old)*ratio
                out['transition']['rebased_count']+=1
            else:
                value=cross_rate(points[d],currency)
            valid.append((d,value,i))
        except DataError:
            pass
    for years,minimum in [(1,min_1y),(3,min_3y)]:
        boundary=_anniversary(as_of,years)
        subset = [(d,v,i) for d,v,i in valid if d >= boundary]
        out[f'count_{years}y']=len(subset)
        if any(d>=boundary for d in peg_breaks):
            out['errors'].append(f'FX_PEG_MISMATCH_{years}Y')
            continue
        # Enough recent EUR points cannot stand in for missing pre-transition BGN.
        if contract and boundary<effective and (boundary<start or not subset
                or (subset[0][0]-boundary).days>7 or subset[0][0]>=effective):
            out['errors'].append(f'FX_TRANSITION_COVERAGE_{years}Y')
            continue
        if len(subset) < minimum:
            out['errors'].append(f'FX_INSUFFICIENT_{years}Y')
            continue
        if any(b[2]-a[2]-1 > 5 or _weekday_gap(a[0],b[0]) > 5 for a,b in zip(subset,subset[1:])):
            out['errors'].append('FX_GAP')
            continue
        returns=[math.log(b[1]/a[1]) for a,b in zip(subset,subset[1:])]
        if len(returns) >= 2:
            out[f'vol_{years}y']=statistics.stdev(returns)*math.sqrt(252)
        if years == 1:
            high=subset[0][1]
            dd=0.
            for _,value,_ in subset:
                high=max(high,value)
                dd=min(dd,value/high-1)
            out['max_drawdown']=dd
    if valid:
        latest=valid[-1][0]
        out['latest_date']=latest.isoformat()
        if (as_of-latest).days > 7:
            out.update(vol_1y=None,vol_3y=None,max_drawdown=None)
            out['errors'].append('FX_STALE')
    if contract and out['errors']:
        out['transition']['status']='INCOMPLETE_OR_INVALID_HISTORY'
    return out
