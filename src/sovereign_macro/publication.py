"""Bind source-specific reuse clearance to the actual collected observations."""
from urllib.parse import parse_qs, urlsplit


def matches_scope(url, scope):
    if not isinstance(scope,dict) or not isinstance(scope.get('query',{}),dict): return False
    try:
        actual=urlsplit(url);expected=urlsplit(scope['url'])
        if (actual.scheme!='https' or actual.username or actual.password or actual.fragment
                or (actual.scheme,actual.netloc,actual.path.rstrip('/'))
                !=(expected.scheme,expected.netloc,expected.path.rstrip('/'))):
            return False
        query=parse_qs(actual.query,keep_blank_values=True)
        return all(query.get(k)==[v] for k,v in scope.get('query',{}).items())
    except (KeyError,TypeError,ValueError):
        return False


def yield_reuse_allowed(country, observations):
    route=country['yield']
    if route['redistribution']!='allowed': return False
    if 'redistribution_review' not in route: return True  # Existing unscoped configuration contract.
    review=route['redistribution_review']
    if not isinstance(review,dict) or not all(review.get(k) for k in ('scope','evidence_url','notice')):
        return False
    if not isinstance(review['scope'],list): return False
    if not observations or not route.get('series'): return False
    return all(obs.redistribution=='allowed' and obs.iso3==country['iso3']
               and obs.series==route['series']
               and all(getattr(obs,key,'') for key in review.get('required_provenance',[]))
               and any(matches_scope(obs.url,scope) for scope in review['scope'])
               for obs in observations)
