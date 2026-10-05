from datetime import date, timedelta
import math
import statistics
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


def fx_metrics(points, currency, as_of, continuity=True, min_1y=200, min_3y=600):
    out = dict(vol_1y=None,vol_3y=None,max_drawdown=None,count_1y=0,count_3y=0,
               latest_date=None,errors=[])
    if currency == 'KRW':
        out.update(vol_1y=0.,vol_3y=0.,max_drawdown=0.,identity=True)
        return out
    if not continuity:
        out['errors'].append('CURRENCY_TRANSITION_UNVERIFIED')
        return out
    dated = sorted(d for d in points if d <= as_of)
    valid = []
    for i,d in enumerate(dated):
        try:
            valid.append((d,cross_rate(points[d],currency),i))
        except DataError:
            pass
    for years,minimum in [(1,min_1y),(3,min_3y)]:
        subset = [(d,v,i) for d,v,i in valid if d >= _anniversary(as_of,years)]
        out[f'count_{years}y']=len(subset)
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
    return out
