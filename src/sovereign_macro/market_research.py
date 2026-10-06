"""Reviewed source links, never observations or scoring inputs."""
from .credit_research import TE_INDEX, official_credit_links

LIQUIDITY_LINKS = {
    'AUS': dict(provider='Australian Office of Financial Management',
        url='https://www.aofm.gov.au/data-hub',
        download_url='https://www.aofm.gov.au/sites/default/files/2026-05-29/new_turnover_-_treasury_bonds.xlsx',
        scope='Market-intermediary survey of AGS secondary-market turnover; Treasury Bonds and Treasury Indexed Bonds are separate datasets',
        limitation='Use new turnover files from 2026 Q1, not the historical 2016–2025 files; observed new Treasury Bonds XLSX returned 502/timeouts in this runtime; schema not verified; verify counterparties, units and matching outstanding before deriving a ratio; not a 5Y bid-ask measure',
        reviewed_on='2026-10-07'),
    'KOR': dict(provider='MOFE / KRX / KOFIA',
        url='https://ktb.moef.go.kr/curbSrviveExprtnNtpbnDdelngQy.do',
        scope='OTC Korean Treasury trading volume, amount and count by residual-maturity bucket',
        limitation='Dynamic KRX table; 3–5Y bucket is not a single 5Y benchmark; current observations not collected'),
    'USA': dict(provider='Federal Reserve Bank of New York',
        url='https://www.newyorkfed.org/markets/counterparties/primary-dealers-statistics',
        scope='Weekly primary-dealer positions, transactions and financing',
        limitation='Dealer reporting perimeter; choose Treasury transaction series and units before collection; not total-market turnover'),
    'JPN': dict(provider='Japan Securities Dealers Association',
        url='https://www.jsda.or.jp/en/statistics/bonds/index.html',
        scope='Monthly member-reported yen-denominated OTC bond transactions',
        limitation='Exchange trades excluded; auction and BOJ purchases included; distinguish outright, repo and JGB basket columns'),
}
OECD_LINK = dict(provider='OECD',
    url='https://www.oecd.org/en/publications/global-debt-report-2026_e9d80efd-en/full-report/sovereign-borrowing-outlook_4470147b.html',
    scope='2025 survey of changes in government-bond secondary-market liquidity',
    limitation='Change in liquidity is not an absolute liquidity level; no comparable 27-country observation feed verified')
ACCESS_LINK = dict(provider='FTSE Russell / LSEG',
    url='https://www.lseg.com/en/ftse-russell/fixed-income-country-classification',
    scope='Institutional local-currency government-bond market accessibility classification',
    limitation='Candidate reference only; edition, market coverage and permitted use need verification; no classification dataset imported')
CREDIT_LINKS = {
    'FRA': dict(provider='Agence France Tresor',
        url='https://www.aft.gouv.fr/en/frances-credit-ratings',
        scope='Issuer-published sovereign ratings, outlooks and agency review dates',
        limitation='Currency and rating term are not separated in the summary; collected as a reported diagnostic only; do not infer long-term local-currency classification',
        reviewed_on='2026-10-07'),
    'DEU': dict(provider='Deutsche Finanzagentur',
        url='https://www.deutsche-finanzagentur.de/en/federal-funding/government-as-issuer/ratings',
        scope='Issuer-published long-term and short-term sovereign ratings, outlooks, report dates and agency report links',
        limitation='Summary does not separate local and foreign currency; collected as long-term, currency-unverified diagnostic; S&P link labelled 2026-04-24 resolves to a 2025-06-13 PDF and cannot certify the current row',
        reviewed_on='2026-10-07'),
    'NZL': dict(provider='New Zealand Debt Management / The Treasury',
        url='https://debtmanagement.treasury.govt.nz/investor-resources/credit-ratings',
        scope='Issuer-published domestic- and foreign-currency sovereign ratings, outlooks and per-agency update dates',
        limitation='collector uses the agency row date, not the footer; the official 2026/27 securities overview establishes long-term basis only if both currency grades and outlooks match; no credit score',
        reviewed_on='2026-10-07'),
}


CREDIT_LINKS.update(official_credit_links())


def research_links(iso, axis):
    if axis=='liquidity':
        sources=([LIQUIDITY_LINKS[iso]] if iso in LIQUIDITY_LINKS else [])+[OECD_LINK]
    elif axis=='accessibility': sources=[ACCESS_LINK]
    elif axis=='credit': sources=([CREDIT_LINKS[iso], TE_INDEX] if iso in CREDIT_LINKS else [])
    else: sources=[]
    return [dict(row,kind='RESEARCH_LINK',reviewed_on=row.get('reviewed_on','2026-10-05'),usable_for_scoring=False) for row in sources]
