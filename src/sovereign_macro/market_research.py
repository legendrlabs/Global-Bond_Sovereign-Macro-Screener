"""Reviewed source links, never observations or scoring inputs."""
LIQUIDITY_LINKS = {
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


def research_links(iso, axis):
    if axis=='liquidity':
        sources=([LIQUIDITY_LINKS[iso]] if iso in LIQUIDITY_LINKS else [])+[OECD_LINK]
    elif axis=='accessibility': sources=[ACCESS_LINK]
    else: sources=[]
    return [dict(row,kind='RESEARCH_LINK',reviewed_on='2026-10-05',usable_for_scoring=False) for row in sources]
