import math
from .models import DataError, finite


def logistic(x):
    if x >= 0:
        return 1 / (1 + math.exp(-x))
    ex = math.exp(x)
    return ex / (1 + ex)


def baseline(nd_current, nd_future, balances, yield_pct):
    if not balances or not all(finite(v) for v in [nd_current, nd_future, yield_pct, *balances]):
        raise DataError("MISSING_OR_NONFINITE")
    if yield_pct < 0:
        raise DataError("BASELINE_DOMAIN_ERROR")
    current = 15 * logistic((70-nd_current)/15)
    future = 25 * logistic((70-nd_future)/15)
    balance = min(10, max(0, 10+sum(balances)/len(balances)))
    fiscal = current + future + balance
    ry = 25 * (math.sqrt(1+yield_pct)-1)
    return dict(fiscal=fiscal, current_debt_score=current, future_debt_score=future,
                balance_score=balance, yield_component=ry, baseline=2*math.sqrt(fiscal*ry))


def adjusted(fiscal, real_yield, fx_vol, market_quality, settings=None):
    s = settings or {}
    fn = fiscal/50 if finite(fiscal) and 0 <= fiscal <= 50 else None
    rn = logistic((real_yield-s.get('real_center',1))/s.get('real_scale',1.5)) if finite(real_yield) else None
    xn = math.exp(-(fx_vol/s.get('fx_scale',.15))**2) if finite(fx_vol) and fx_vol >= 0 else None
    qn = market_quality if finite(market_quality) and 0 <= market_quality <= 1 else None
    axes = [fn,rn,xn,qn]
    score = None
    if all(v is not None for v in axes):
        score = 100 * math.prod(v**w for v,w in zip(axes,[.4,.3,.2,.1]))
    return dict(fiscal_norm=fn, real_yield_norm=rn, fx_norm=xn, market_quality_norm=qn, adjusted=score)


def rank_rows(rows, model):
    key = model+'_rank'
    for row in rows:
        row[key] = None
    valid = sorted((r for r in rows if r.get('usable_'+model) and finite(r.get(model))),
                   key=lambda r:(-r[model],r['iso3']))
    last = None
    rank = 0
    for pos,row in enumerate(valid,1):
        if row[model] != last:
            rank = pos
        row[key] = rank
        last = row[model]
