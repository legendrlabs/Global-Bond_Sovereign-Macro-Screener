from .models import finite


def regimes(nd_current, nd_future, real_yield, fx_vol, nominal_5y, nominal_10y):
    valid_debt=finite(nd_current) and finite(nd_future)
    trend='UNAVAILABLE'
    if valid_debt:
        delta=nd_future-nd_current
        trend='IMPROVING' if delta <= -5 else 'DETERIORATING' if delta >= 5 else 'STABLE'
    real='UNAVAILABLE' if not finite(real_yield) else 'LOW' if real_yield < 0 else 'NEUTRAL' if real_yield <= 2 else 'HIGH'
    fx='UNAVAILABLE' if not finite(fx_vol) else 'LOW' if fx_vol < .08 else 'MEDIUM' if fx_vol <= .15 else 'HIGH'
    carry='UNAVAILABLE'
    if valid_debt and finite(real_yield) and finite(fx_vol):
        carry='UNATTRACTIVE' if real_yield < 0 else 'ATTRACTIVE' if real_yield > 2 and fx=='LOW' and trend!='DETERIORATING' else 'NEUTRAL'
    discount='UNAVAILABLE'
    if valid_debt and all(finite(x) for x in [real_yield,nominal_5y,nominal_10y]):
        levels=['EASING','NEUTRAL','RESTRICTIVE','HIGHLY_RESTRICTIVE']
        ix=0 if real_yield < 0 else 1 if real_yield <= 1 else 2 if real_yield <= 3 else 3
        if nominal_5y >= 5 and nominal_10y >= 5 and trend=='DETERIORATING': ix=min(3,ix+1)
        discount=levels[ix]
    return dict(fiscal_trend=trend,real_yield_regime=real,fx_risk=fx,carry=carry,discount_rate=discount)
