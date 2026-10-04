"""Evaluate one immutable source bundle; incomplete axes are never reweighted."""
from datetime import date, timedelta
from .models import DataError, Observation, finite
from .scoring import baseline, adjusted, rank_rows
from .fx import fx_metrics, _anniversary
from .regimes import regimes

NUMERIC_FIELDS=('yield_5y','yield_10y','net_debt_current','net_debt_future','gross_debt_current',
                'balance_mean','balance_trajectory','inflation_mean','real_yield','fiscal','baseline','adjusted',
                'fiscal_norm','real_yield_norm','fx_norm','market_quality_norm','fx_vol_1y','fx_vol_3y','fx_drawdown')

def evaluate(config,bundle,as_of,public_output=False,demo=False):
    fiscal=bundle.get('fiscal')
    values=fiscal['values'] if fiscal else {}
    rows=[]
    source_config=config['sources']
    system_errors=list(bundle.get('errors',[]))
    for c in config['countries']['countries']:
        iso=c['iso3']
        row=dict(iso3=iso,name=c['name'],currency=c['currency'],errors=[],usable_baseline=False,
                 usable_adjusted=False,market_quality_status='UNAVAILABLE',provenance=[],
                 yield_type=c['yield']['yield_type'],edition=fiscal['edition'] if fiscal else '',
                 redistribution_status='pending')
        row.update({k:None for k in NUMERIC_FIELDS})
        y5=bundle.get('yields',{}).get(iso+':5')
        y10=bundle.get('yields',{}).get(iso+':10')
        if y5: row['yield_type']=y5.yield_type
        currency_start=date.fromisoformat(c['currency_from'])
        for tenor,obs in [(5,y5),(10,y10)]:
            if obs:
                row['provenance'].append(obs.to_dict())
                row[f'yield_{tenor}y_date']=obs.period
                try:
                    obs.valid_on(as_of,config['scoring']['stale_days'])
                    if obs.metric!=f'yield_{tenor}y' or obs.yield_type!=c['yield']['yield_type']:
                        raise DataError('YIELD_DEFINITION_MISMATCH')
                    if currency_start>as_of: raise DataError('CURRENCY_ASSIGNMENT_UNAVAILABLE')
                    if obs.iso3!=iso or obs.currency!=c['currency'] or obs.tenor_years!=tenor:
                        raise DataError('COUNTRY_CURRENCY_TENOR_MISMATCH')
                    row[f'yield_{tenor}y']=obs.value
                except DataError as exc: row['errors'].append(f'YIELD_{tenor}Y:'+str(exc))
            elif tenor==5 or iso in config['scoring']['watch_markets']:
                row['errors'].append(f'YIELD_{tenor}Y_UNAVAILABLE')
        net=values.get('net_debt',{}).get(iso,{})
        bal=values.get('overall_balance',{}).get(iso,{})
        cpi=values.get('inflation',{}).get(iso,{})
        row['net_debt_current']=net.get(as_of.year)
        row['gross_debt_current']=values.get('gross_debt',{}).get(iso,{}).get(as_of.year)
        fscore=None
        if fiscal:
            end=fiscal['horizon_end'];start=fiscal['horizon_start']
            row.update(forecast_start=start,forecast_end=end,cpi_years=fiscal['cpi_years'],
                       current_fiscal_classification='forecast' if as_of.year>=start else 'historical',
                       future_fiscal_classification='forecast')
            row['net_debt_future']=net.get(end)
            balances=[bal.get(y) for y in range(start,end+1)]
            row['provenance'].extend(fiscal.get('provenance',{}).values())
            pdf_cells=[p['year'] for p in fiscal.get('pdf_fills',[]) if p['iso3']==iso]
            if pdf_cells:
                row['provenance'].append(dict(fiscal['pdf_provenance'],filled_years=pdf_cells))
            if finite(row['net_debt_current']) and finite(row['net_debt_future']) and all(finite(v) for v in balances):
                fscore=baseline(row['net_debt_current'],row['net_debt_future'],balances,0)['fiscal']
                row.update(fiscal=fscore,balance_mean=sum(balances)/len(balances),balance_trajectory=balances[-1]-balances[0])
            else: row['errors'].append('FISCAL_HORIZON_INCOMPLETE')
            if as_of.year!=start: row['errors'].append('FISCAL_YEAR_ROLLOVER')
            inflation=[cpi.get(y) for y in fiscal['cpi_years']]
            if all(finite(v) for v in inflation):
                row['inflation_mean']=sum(inflation)/5
                if row['yield_5y'] is not None: row['real_yield']=row['yield_5y']-row['inflation_mean']
            else: row['errors'].append('CPI_HORIZON_INCOMPLETE')
        else: row['errors'].append('FISCAL_UNAVAILABLE')
        if fscore is not None and row['yield_5y'] is not None:
            try:
                row['baseline']=baseline(row['net_debt_current'],row['net_debt_future'],balances,row['yield_5y'])['baseline']
                if c['yield']['baseline_compatible'] and 'FISCAL_YEAR_ROLLOVER' not in row['errors']:
                    row['usable_baseline']=True
                else: row['errors'].append('BASELINE_DEFINITION_UNAPPROVED')
            except DataError as exc: row['errors'].append(str(exc))
        try:
            fx=fx_metrics(bundle.get('fx',{}),c['currency'],as_of,continuity=c['fx_continuity'])
            for years in (1,3):
                if currency_start>_anniversary(as_of,years):
                    fx[f'vol_{years}y']=None
                    if years==1: fx['max_drawdown']=None
                    fx['errors'].append(f'CURRENCY_{years}Y_HISTORY_UNAVAILABLE')
        except (DataError,ValueError) as exc:
            fx={'vol_1y':None,'vol_3y':None,'max_drawdown':None,'errors':['FX:'+str(exc)],'count_1y':0,'count_3y':0,'latest_date':None}
        row.update(fx_vol_1y=fx['vol_1y'],fx_vol_3y=fx['vol_3y'],fx_drawdown=fx['max_drawdown'],
                   fx_count_1y=fx['count_1y'],fx_count_3y=fx['count_3y'],fx_date=fx.get('latest_date'))
        row['errors'].extend(fx['errors'])
        if bundle.get('provenance',{}).get('fx'): row['provenance'].append(bundle['provenance']['fx'])
        row.update(adjusted(fscore,row['real_yield'],row['fx_vol_1y'],None,config['scoring']))
        row.update(regimes(row['net_debt_current'],row['net_debt_future'],row['real_yield'],row['fx_vol_1y'],row['yield_5y'],row['yield_10y']))
        row['errors'].append('MARKET_QUALITY_UNAVAILABLE')
        if demo:
            row['usable_baseline']=False
            row['errors'].append('SYNTHETIC_DEMO')
        rows.append(row)
    baseline_count=sum(r['usable_baseline'] for r in rows)
    core_complete=all(finite(r['real_yield']) and finite(r['fx_vol_1y'])
                      and (r['iso3'] not in config['scoring']['watch_markets'] or finite(r['yield_10y'])) for r in rows)
    ready=baseline_count==27 and core_complete and not system_errors and not demo
    quality={'status':'READY' if ready else 'DATA_HOLD',
             'safe_to_use':ready,'core_inputs_complete':core_complete,
             'safe_to_use_adjusted':False,'baseline_usable':baseline_count,'adjusted_usable':0,
             'country_count':len(rows),'demo':demo,'public_output':public_output,'system_errors':system_errors}
    for row in rows:
        if public_output:
            # The publication gate is conservative at the entire row, including regimes.
            eligible=(source_config['fiscal']['redistribution']=='allowed'
                      and source_config['fx']['redistribution']=='allowed'
                      and next(c['yield']['redistribution'] for c in config['countries']['countries'] if c['iso3']==row['iso3'])=='allowed')
            if not eligible:
                for key in NUMERIC_FIELDS: row[key]=None
                for key in ('fiscal_trend','real_yield_regime','fx_risk','carry','discount_rate'): row[key]='UNAVAILABLE'
                row['usable_baseline']=False;row['usable_adjusted']=False
                row['errors'].append('REDISTRIBUTION_PENDING_REDACTED')
                for provenance in row['provenance']: provenance.pop('value',None)
            else: row['redistribution_status']='allowed'
    if public_output:
        quality['baseline_usable']=sum(r['usable_baseline'] for r in rows)
        quality['safe_to_use']=quality['safe_to_use'] and quality['baseline_usable']==27
        if not quality['safe_to_use']: quality['status']='DATA_HOLD'
    rank_rows(rows,'baseline');rank_rows(rows,'adjusted')
    return {'as_of':as_of.isoformat(),'model_version':config['scoring']['version'],'rows':rows,'quality':quality,
            'coverage':{'yield5_observations_parsed':sum(bundle.get('yields',{}).get(c['iso3']+':5') is not None
                                                       for c in config['countries']['countries'])},
            'http_records':bundle.get('http_records',[])}

def demo_bundle(config,as_of):
    """Synthetic examples, deliberately ineligible for rankings and live acceptance."""
    values={metric:{} for metric in ('net_debt','gross_debt','overall_balance','inflation')}
    yields={}
    for i,c in enumerate(config['countries']['countries']):
        for metric,initial in [('net_debt',40+i),('gross_debt',60+i),('overall_balance',-2),('inflation',2)]:
            values[metric][c['iso3']]={y:initial for y in range(as_of.year,as_of.year+6)}
        yields[c['iso3']+':5']=Observation(c['iso3'],'yield_5y',3+i/20,as_of.isoformat(),c['currency'],
                                          provider='SYNTHETIC_DEMO',tenor_years=5,yield_type=c['yield']['yield_type'])
    fx={}
    for n in range(1100):
        day=as_of-timedelta(days=n)
        if day.weekday()<5:
            fx[day]={'KRW':1500+n/10,**{c['currency']:1 for c in config['countries']['countries'] if c['currency'] not in ('KRW','EUR')}}
    fiscal={'edition':'SYNTHETIC_DEMO','values':values,'horizon_start':as_of.year,'horizon_end':as_of.year+5,
            'cpi_years':list(range(as_of.year+1,as_of.year+6)),'pdf_fills':[]}
    return {'fiscal':fiscal,'fx':fx,'yields':yields,'errors':[]}
