"""Reviewed official rating routes, without copied grades or inferred observations."""
REVIEWED = '2026-10-07'
TE_INDEX = dict(provider='Trading Economics', url='https://ko.tradingeconomics.com/country-list/rating',
    scope='Secondary sovereign-rating discovery index; S&P candidates visible for all configured countries',
    limitation='Summary omits currency, term and per-agency assessment dates; TE score is a separate model; no API or grade dataset imported; API credentials and permitted use need separate verification',
    reviewed_on=REVIEWED)

# A link can identify an edition, historical action, gated page or research index.
# It never certifies a current same-agency long-term local-currency observation.
OFFICIAL_ROUTES = {
    'ISL': ('Iceland Government Debt Management', 'https://www.lanamal.is/EN/investors/credit-rating',
            'Explicit domestic/foreign currency and term; last-change date has month precision only; not latest assessment'),
    'NOR': ('Norges Bank', 'https://www.norges-bank.no/tema/Statsgjeld/Investorrelasjoner/',
            'Long-term table dates mean rating effective since, not latest assessment; currency unverified'),
    'AUS': ('Australian Treasury', 'https://ministers.treasury.gov.au/ministers/jim-chalmers-2022/media-releases/sp-global-reaffirms-aaa-credit-rating',
            'Dated 2026-08-06 historical affirmation release; no current table, explicit currency/term or outlook established here'),
    'KOR': ('Korean Ministry of Finance and Economy', 'https://english.mofe.go.kr/pc/selectTbPressCenterDtl.do?boardCd=N0001&seq=6398',
            'Dated 2026-04-29 affirmation release; currency and term unverified; not an automatically refreshed table'),
    'JPN': ('Japanese Ministry of Finance', 'https://www.mof.go.jp/english/policy/jgbs/publication/debt_management_report/2026/index.html',
            'Annual supplement has long-term home-currency snapshot as at 2026-04-03; historical outlook-change date is not latest assessment; no PDF observation imported'),
    'CZE': ('Czech Ministry of Finance', 'https://mf.gov.cz/en/fiscal-policy/state-debt/basic-information/rating',
            'Explicit LC/FC long-term tables lack assessment dates and retain older outlook; compare the 2026-09-25 official announcement; no current observation imported'),
    'BGR': ('Bulgarian Ministry of Finance', 'https://www.minfin.bg/bg/69',
            'Workbook link reported on official landing page; direct access returned 403 and workbook schema was not inspected'),
    'CAN': ('Canadian Department of Finance', 'https://www.canada.ca/en/department-finance/services/publications/debt-management-report/2024-2025.html',
            'Annual LC/FC LT/ST snapshot as at 2025-03-31; previous action date and footer are not latest assessment'),
    'IRL': ('National Treasury Management Agency', 'https://www.ntma.ie/business-areas/funding-and-debt-management/investor-relations/credit-ratings',
            'Current LT/ST table has no assessment date or currency scope'),
    'DNK': ('Danmarks Nationalbank', 'https://www.nationalbanken.dk/en/government-debt/investor-relations/rating',
            'Collected long-term domestic/foreign debt diagnostic; most recently confirmed is not rating action; currency needs separate linked PDF verification'),
    'LTU': ('Lithuanian Ministry of Finance', 'https://finmin.lrv.lt/en/competence-areas/state-debt-management/credit-ratings/lithuania-s-credit-ratings-history/',
            'LC/FC and LT/ST history has month-only action dates; current-page calendar dates are future schedules, not assessments'),
    'SWE': ('Swedish National Debt Office', 'https://www.riksgalden.se/en/our-operations/central-government-borrowing/sweden-as-an-issuer/rating/',
            'Issuer-grade summary lacks outlook, agency assessment date, currency and term; page review date is not assessment'),
    'HRV': ('Croatian Ministry of Finance', 'https://mfin.gov.hr/vijesti/s-p-podigao-kreditni-rejting-hrvatske-s-a-na-a-uz-stabilne-izglede/4118',
            '2026-03-14 release reports 2026-03-13 action; LT/ST explicit, currency absent; historical action, not current table'),
    'NLD': ('Dutch State Treasury Agency', 'https://english.dsta.nl/subjects/c/capital-markets',
            'Generic credit-quality prose; no agency-specific exact dated current table verified'),
    'SVN': ('Slovenian Ministry of Finance', 'https://www.gov.si/en/topics/investor-relations/',
            'Table separates last change and latest revision, but jurisdiction attestation requires user representations; research only, no collector'),
    'SVK': ('National Bank of Slovakia', 'https://nbs.sk/en/about-the-bank/international-relations/international-institutions/rating/',
            'Collected current summary with last-change date only; latest assessment, currency and term remain unverified'),
    'AUT': ('Austrian Treasury', 'https://www.oebfa.at/en/presse/presseuebersicht/2026/s-p-news-02-2026.html',
            'Public 2026-02-06 historical release links explicit LC/FC LT/ST PDF; current ratings page requires jurisdiction attestations; no collector'),
    'PRT': ('Portuguese Treasury and Debt Management Agency', 'https://www.igcp.pt/pt/investidores/ratings',
            'Jurisdiction attestation page; no automated collection or eligibility representation; ungated bond issue dates are not rating assessments'),
    'ISR': ('Israeli Ministry of Finance', 'https://www.gov.il/BlobFolder/news/press_140526a/en/RatingsDirect_ResearchUpdate_Israel_3559560_May-8-2026.pdf',
            'Explicit LC/FC LT/ST historical action dated 2026-05-08; ministry announcement May 14 is a separate date; no current table'),
    'ESP': ('Spanish Treasury', 'https://www.tesoro.es/en/deuda-publica/calificacion-crediticia',
            'Indexed transposed LT/ST table with As at date, currency absent; production request returned 502, no numeric collector'),
    'GBR': ('S&P Global Ratings', 'https://www.spglobal.com/ratings/en/regulatory/article/-/view/sourceId/101677731',
            'Historical 2026-04-10 action explicitly separates term and LC/FC; no current DMO rating table found'),
    'ITA': ('S&P Global Ratings', 'https://www.spglobal.com/ratings/en/regulatory/article/-/view/type/HTML/id/3352820',
            'Historical 2025-04-11 action; cannot certify current outlook; no current Ministry rating table verified'),
    'BEL': ('Belgian Debt Agency', 'https://www.debtagency.be/en/datafederalstaterating',
            'Collected confirmation date from current row; ignore future review and rating-scale comparison; currency/term absent'),
    'USA': ('S&P Global Ratings', 'https://www.spglobal.com/ratings/en/regulatory/ratings-actions?app=sp',
            'Agency action-search entry point only; no current US Treasury rating table or country-filtered current observation verified'),
}


def official_credit_links():
    return {iso: dict(provider=provider, url=url, scope='Official sovereign credit-rating research route',
                      limitation=limitation, reviewed_on=REVIEWED)
            for iso, (provider, url, limitation) in OFFICIAL_ROUTES.items()}
