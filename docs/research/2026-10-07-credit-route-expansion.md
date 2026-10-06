# 27-country credit-source expansion — 2026-10-07 KST

Trading Economics is registered as a secondary discovery index for all 27 configured
countries. Its summary is not imported as a same-agency long-term local-currency
rating feed. It omits rating currency, term and per-agency assessment dates. Its own
numerical score is a separate model. No TE API credential or rating dataset is added.

## Newly connected official diagnostics

Belgium uses the current confirmation date inside the S&P row, ignoring next review
and the separate generic rating-scale comparison. Term and currency remain unverified.
Denmark validates both header levels and their column spans before selecting long-term
domestic and foreign debt columns. The date means most recently confirmed, not rating
action. The linked PDF distinguishes currencies but is not parsed automatically here:
the HTML diagnostic explicitly retains currency-unverified status.
Slovakia transposes the NBS table and preserves Last change as last_action_date with
issuer_last_change date_type. It never supplies a latest assessment_date. Term and
currency remain unverified. This credit diagnostic does not alter SVK yield eligibility.

All three remain REPORTED_TYPE_UNVERIFIED, value=None, usable_for_scoring=False and
redistribution=pending. Grades and outlooks are hidden in public output. The report
now displays a Date basis column. Demo mode discards actual issuer provenance.

## Coverage and follow-up inventory

Six automatic official HTML diagnostics are connected (three existing plus three new).
The other 21 countries have research routes, not observed rating inputs. A listed link
can be a historical action, annual edition, gated page or agency search entry point;
it is not proof of a current complete observation. No grades or raw supplier tables
are copied below. Most countries still need explicit scope and/or an exact agency date.

| Country | Route | Connection | Limitation |
| --- | --- | --- | --- |
| ISL | [Iceland Government Debt Management](https://www.lanamal.is/EN/investors/credit-rating) | Research only | Explicit domestic/foreign currency and term; last-change date has month precision only; not latest assessment |
| NOR | [Norges Bank](https://www.norges-bank.no/tema/Statsgjeld/Investorrelasjoner/) | Research only | Long-term table dates mean rating effective since, not latest assessment; currency unverified |
| AUS | [Australian Treasury](https://ministers.treasury.gov.au/ministers/jim-chalmers-2022/media-releases/sp-global-reaffirms-aaa-credit-rating) | Research only | Dated 2026-08-06 historical affirmation release; no current table, explicit currency/term or outlook established here |
| NZL | [New Zealand Debt Management / The Treasury](https://debtmanagement.treasury.govt.nz/investor-resources/credit-ratings) | Automatic diagnostic | collector uses the agency row date, not the footer; the official 2026/27 securities overview establishes long-term basis only if both currency grades and outlooks match; no credit score |
| KOR | [Korean Ministry of Finance and Economy](https://english.mofe.go.kr/pc/selectTbPressCenterDtl.do?boardCd=N0001&seq=6398) | Research only | Dated 2026-04-29 affirmation release; currency and term unverified; not an automatically refreshed table |
| CZE | [Czech Ministry of Finance](https://mf.gov.cz/en/fiscal-policy/state-debt/basic-information/rating) | Research only | Explicit LC/FC long-term tables lack assessment dates and retain older outlook; compare the 2026-09-25 official announcement; no current observation imported |
| BGR | [Bulgarian Ministry of Finance](https://www.minfin.bg/bg/69) | Research only | Workbook link reported on official landing page; direct access returned 403 and workbook schema was not inspected |
| CAN | [Canadian Department of Finance](https://www.canada.ca/en/department-finance/services/publications/debt-management-report/2024-2025.html) | Research only | Annual LC/FC LT/ST snapshot as at 2025-03-31; previous action date and footer are not latest assessment |
| IRL | [National Treasury Management Agency](https://www.ntma.ie/business-areas/funding-and-debt-management/investor-relations/credit-ratings) | Research only | Current LT/ST table has no assessment date or currency scope |
| DNK | [Danmarks Nationalbank](https://www.nationalbanken.dk/en/government-debt/investor-relations/rating) | Automatic diagnostic | Collected long-term domestic/foreign debt diagnostic; most recently confirmed is not rating action; currency needs separate linked PDF verification |
| LTU | [Lithuanian Ministry of Finance](https://finmin.lrv.lt/en/competence-areas/state-debt-management/credit-ratings/lithuania-s-credit-ratings-history/) | Research only | LC/FC and LT/ST history has month-only action dates; current-page calendar dates are future schedules, not assessments |
| SWE | [Swedish National Debt Office](https://www.riksgalden.se/en/our-operations/central-government-borrowing/sweden-as-an-issuer/rating/) | Research only | Issuer-grade summary lacks outlook, agency assessment date, currency and term; page review date is not assessment |
| HRV | [Croatian Ministry of Finance](https://mfin.gov.hr/vijesti/s-p-podigao-kreditni-rejting-hrvatske-s-a-na-a-uz-stabilne-izglede/4118) | Research only | 2026-03-14 release reports 2026-03-13 action; LT/ST explicit, currency absent; historical action, not current table |
| NLD | [Dutch State Treasury Agency](https://english.dsta.nl/subjects/c/capital-markets) | Research only | Generic credit-quality prose; no agency-specific exact dated current table verified |
| SVN | [Slovenian Ministry of Finance](https://www.gov.si/en/topics/investor-relations/) | Research only | Table separates last change and latest revision, but jurisdiction attestation requires user representations; research only, no collector |
| DEU | [Deutsche Finanzagentur](https://www.deutsche-finanzagentur.de/en/federal-funding/government-as-issuer/ratings) | Automatic diagnostic | Summary does not separate local and foreign currency; collected as long-term, currency-unverified diagnostic; S&P link labelled 2026-04-24 resolves to a 2025-06-13 PDF and cannot certify the current row |
| SVK | [National Bank of Slovakia](https://nbs.sk/en/about-the-bank/international-relations/international-institutions/rating/) | Automatic diagnostic | Collected current summary with last-change date only; latest assessment, currency and term remain unverified |
| AUT | [Austrian Treasury](https://www.oebfa.at/en/presse/presseuebersicht/2026/s-p-news-02-2026.html) | Research only | Public 2026-02-06 historical release links explicit LC/FC LT/ST PDF; current ratings page requires jurisdiction attestations; no collector |
| PRT | [Portuguese Treasury and Debt Management Agency](https://www.igcp.pt/pt/investidores/ratings) | Research only | Jurisdiction attestation page; no automated collection or eligibility representation; ungated bond issue dates are not rating assessments |
| ISR | [Israeli Ministry of Finance](https://www.gov.il/BlobFolder/news/press_140526a/en/RatingsDirect_ResearchUpdate_Israel_3559560_May-8-2026.pdf) | Research only | Explicit LC/FC LT/ST historical action dated 2026-05-08; ministry announcement May 14 is a separate date; no current table |
| ESP | [Spanish Treasury](https://www.tesoro.es/en/deuda-publica/calificacion-crediticia) | Research only | Indexed transposed LT/ST table with As at date, currency absent; production request returned 502, no numeric collector |
| GBR | [S&P Global Ratings](https://www.spglobal.com/ratings/en/regulatory/article/-/view/sourceId/101677731) | Research only | Historical 2026-04-10 action explicitly separates term and LC/FC; no current DMO rating table found |
| FRA | [Agence France Tresor](https://www.aft.gouv.fr/en/frances-credit-ratings) | Automatic diagnostic | Currency and rating term are not separated in the summary; collected as a reported diagnostic only; do not infer long-term local-currency classification |
| ITA | [S&P Global Ratings](https://www.spglobal.com/ratings/en/regulatory/article/-/view/type/HTML/id/3352820) | Research only | Historical 2025-04-11 action; cannot certify current outlook; no current Ministry rating table verified |
| BEL | [Belgian Debt Agency](https://www.debtagency.be/en/datafederalstaterating) | Automatic diagnostic | Collected confirmation date from current row; ignore future review and rating-scale comparison; currency/term absent |
| USA | [S&P Global Ratings](https://www.spglobal.com/ratings/en/regulatory/ratings-actions?app=sp) | Research only | Agency action-search entry point only; no current US Treasury rating table or country-filtered current observation verified |
| JPN | [Japanese Ministry of Finance](https://www.mof.go.jp/english/policy/jgbs/publication/debt_management_report/2026/index.html) | Research only | Annual supplement has long-term home-currency snapshot as at 2026-04-03; historical outlook-change date is not latest assessment; no PDF observation imported |

## Source conflicts and date distinctions

The Czech Ministry rating table has explicit LC/FC long-term scope but no agency
dates and retains the earlier outlook. Its
[2026-09-25 announcement](https://mf.gov.cz/cs/ministerstvo/media/tiskove-zpravy/2026/ratingova-agentura-s-and-p-zlepsuje-vyhled-ceske-r-65306)
reports a later outlook change. No current observation is imported from the old table.
Lithuania's scheduled review calendar is not an assessment date, and its history has
month precision only. Norway's rating-since date and Canada's previous-action/annual
snapshot date do not establish latest assessment. Japan's annual home-currency snapshot
and historical outlook-change dates also have separate meanings.

Slovenia, Portugal and Austria's current ratings pages require jurisdiction/access
representations. They remain links; no collector accepts those attestations. Austria's
public action news remains a separate historical source. Bulgaria's landing page was
blocked and its linked workbook was not inspected. Spain's indexed table could be
read through search, but direct production-transport download returned 502. No schema
is guessed for these inaccessible or gated sources.

This expansion targets PR #13's credit-diagnostics branch. PR #15's BGR FX continuity
and SVK yield policy remain a separate change. Neither merging main nor releasing a
new package is part of this draft. Market Quality and Adjusted remain unimplemented.

## Verification

Synthetic date, header, scope, candidate and report regressions were written before
the corresponding new behavior. The complete suite passes 226 tests. New actual
Belgium, Denmark and Slovakia HTML bodies were separately acquired with HTTP 200 and
parsed successfully. Source downloads remain private, outside the repository. The
production refresh and actual publication checks are recorded below after completion.

Production refresh: seven official current/basis requests returned HTTP 200 through
HttpClient's curl_cffi transport. All six country parsers succeeded: NZL is an available
long-term local-currency diagnostic; the other five retain type-unverified status.
URLs, raw hashes, actual retrieval timestamps and transport were preserved.

Actual published public and demo JSON files plus serialized market_inputs/provenance
CSV fields were recursively checked for grade/outlook/action keys: none remained.
Public mode retained all six issuer source hashes; demo retained none. All 27 rows
kept Market Quality and Adjusted scores absent. The other inputs in this publication
check are synthetic, so these artifacts are not a live 27-country ranking.
