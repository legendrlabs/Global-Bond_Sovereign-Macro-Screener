from importlib.resources import files
from pathlib import Path
import yaml


def load_config(directory=None):
    base=Path(directory) if directory else files('sovereign_macro').joinpath('defaults')
    result={name:yaml.safe_load(base.joinpath(name+'.yaml').read_text(encoding='utf8')) for name in ['countries','scoring','sources']}
    rows=result['countries']['countries']
    expected=set('ISL NOR AUS NZL KOR CZE BGR CAN IRL DNK LTU SWE HRV NLD SVN DEU SVK AUT PRT ISR ESP GBR FRA ITA BEL USA JPN'.split())
    if len(rows)!=27 or {r['iso3'] for r in rows}!=expected:
        raise ValueError('Expected the exact 27-country universe with unique ISO3 IDs')
    weights=result['scoring']['weights']
    if weights != {'fiscal':.4,'real_yield':.3,'fx':.2,'market_quality':.1}:
        raise ValueError('Adjusted weights must remain 0.40/0.30/0.20/0.10')
    if result['scoring']['real_scale']<=0 or result['scoring']['fx_scale']<=0:
        raise ValueError('Normalization scales must be positive')
    return result
