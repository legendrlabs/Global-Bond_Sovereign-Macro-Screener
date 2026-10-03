"""Failure-isolated collection: absence stays absence."""
from datetime import date
from .fiscal import collect_fiscal
from .sources import collect_yield, parse_ecb

def collect(config,client,as_of):
    countries=config['countries']['countries']
    bundle={'fiscal':None,'fx':{},'yields':{},'errors':[],'provenance':{}}
    try:
        bundle['fiscal']=collect_fiscal(client,config['sources']['fiscal'],countries,as_of)
        bundle['errors'].extend(bundle['fiscal']['errors'])
    except Exception as exc:
        bundle['errors'].append('FISCAL:'+type(exc).__name__+':'+str(exc)[:180])
    try:
        p=client.fetch(config['sources']['fx']['url'])
        bundle['fx']={date.fromisoformat(d):r for d,r in parse_ecb(p.body).items()}
        bundle['provenance']['fx']={'url':p.url,'raw_sha256':p.sha256,'retrieved_at':p.retrieved_at,
                                    'redistribution':config['sources']['fx']['redistribution']}
    except Exception as exc:
        bundle['errors'].append('FX:'+type(exc).__name__+':'+str(exc)[:180])
    for country in countries:
        for tenor in ([5,10] if country['iso3'] in config['scoring']['watch_markets'] else [5]):
            key=country['iso3']+f':{tenor}'
            try: bundle['yields'][key]=collect_yield(client,country,as_of,tenor)
            except Exception as exc:
                bundle['errors'].append(key+':'+type(exc).__name__+':'+str(exc)[:180])
    bundle['http_records']=client.records
    return bundle
