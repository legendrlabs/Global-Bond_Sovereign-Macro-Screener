"""Use validated official yields first; isolate and disclose WGB fallback."""
from dataclasses import replace
import json

from .models import DataError
from .sources import collect_yield
from .wgb import BASE, collect_wgb


def yield_contract(country, observation, config):
    if observation.provider != 'wgb': return country['yield']
    fallback = config['sources'].get('yield_fallback', {})
    tenor = observation.tenor_years
    slug = country.get('wgb_slug', '')
    if (not fallback.get('enabled') or tenor not in (5, 10) or not slug
            or observation.series != f'{slug}:{tenor}Y'
            or observation.url != f'{BASE}/bond-historical-data/{slug}/{tenor}-years/'):
        raise DataError('WGB_SOURCE_CONTRACT')
    return fallback


def validate_yield(country, observation, config, as_of, tenor):
    observation.valid_on(as_of, config['scoring']['stale_days'])
    contract = yield_contract(country, observation, config)
    if (observation.metric != f'yield_{tenor}y'
            or observation.yield_type != contract['yield_type']):
        raise DataError('YIELD_DEFINITION_MISMATCH')
    if (observation.iso3 != country['iso3'] or observation.currency != country['currency']
            or observation.tenor_years != tenor):
        raise DataError('COUNTRY_CURRENCY_TENOR_MISMATCH')


def collect_preferred_yield(client, country, config, as_of, tenor=5):
    try:
        observation = collect_yield(client, country, as_of, tenor)
        validate_yield(country, observation, config, as_of, tenor)
        return replace(observation, selection_reason='OFFICIAL_VALID')
    except Exception as exc:
        official_error = type(exc).__name__ + ':' + str(exc)[:180]
        if not config['sources'].get('yield_fallback', {}).get('enabled'): raise
    try:
        observation = collect_wgb(client, country, as_of, tenor=tenor,
                                  stale_days=config['scoring']['stale_days'])
        validate_yield(country, observation, config, as_of, tenor)
        return replace(observation, selection_reason='OFFICIAL_UNAVAILABLE:' + official_error)
    except Exception as exc:
        raise DataError('OFFICIAL[' + official_error + '] WGB['
                        + type(exc).__name__ + ':' + str(exc)[:180] + ']') from exc


def observation_warnings(observation):
    warnings = ['WGB_FALLBACK_USED'] if observation.provider == 'wgb' else []
    if observation.provider == 'wgb':
        try:
            notes = json.loads(observation.notes)
            warnings.extend(notes.get('warnings', []))
        except (ValueError, TypeError, AttributeError): pass
    return warnings
