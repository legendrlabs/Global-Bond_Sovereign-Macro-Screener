# Implemented source contracts

This initial release deliberately distinguishes researched candidates from callable adapters. No authentication keys or embedded credentials are required by the implemented requests. Endpoint availability may change.

| Data / country | Adapter / exact series | Interpretation | Baseline eligible |
|---|---|---|---|
| Fiscal net debt | IMF GGXWDN_G01_GDP_PT | General government, percent GDP | Complete horizon only |
| Overall balance | IMF GGXCNL_G01_GDP_PT | Overall, not primary balance | Complete forecast period |
| Gross debt | IMF G_XWDG_G01_GDP_PT | Reference field; never net-debt substitute | Not a scoring substitute |
| Inflation | IMF PCPIPCH | Five annual forecasts after reference year | Same-edition WEO |
| FX | ECB eurofxref-hist.xml | Foreign units per EUR, converted to KRW per currency | Matched valid dates only |
| CAN | BoC BD.CDN.5YR.DQ.YLD | 5Y government benchmark | Yes |
| NOR | Norges GOVT_GENERIC_RATES 5Y GBON | Government benchmark | Yes |
| SWE | Riksbank SEGVB5YC | Government benchmark | Yes |
| DEU / NLD / FRA / GBR | Riksbank DEGVB5Y / NLGVB5Y / FRGVB5Y / GBGVB5Y | Government benchmark via Riksbank; underlying Refinitiv rights require review | Yes locally |
| AUS | RBA FCMYGBAG5D | Interpolated constant maturity | Pending definition decision |
| KOR | KOFIA 3007 final quotation | Basket quotation; legacy 1530 request token | Pending definition decision |
| USA | Treasury BC_5YEAR and BC_10YEAR | Par constant maturity | Pending; raw 5Y/10Y regime monitoring permitted locally |
| JPN | MOF 5年 | Constant maturity, CP932 / Japanese era date | Pending definition decision |
| ITA | Bank of Italy MFN_BMK.D.020.922.0.EUR.205 | Benchmark, latest collected 2026-08-31 | Stale; not ranked |
| BEL | NBB D.5Y.F | Fixed residual reference | Pending definition and unit metadata confirmation |
| ISL | CBI FLV nominal par 5Y | Synthetic par constant maturity; Excel percent fractions converted ×100 | Pending definition decision |
| ESP | Banco de España D_G0B1F0ZO | Daily secondary-market sovereign 5Y bucket | Pending definition decision |
| SVK | NBS Yields_SK / ZCY5Y | Estimated zero-coupon; daily observations, weekly publication | Pending definition; existing 7-day stale gate |
| ISR | BOI ZC_TSB_ZND_05Y_MA | Nominal zero-coupon monthly average, percent (PT / multiplier 0) | Monthly frequency fails daily gate |

| CZE | CNB monthly bulletin TABLE_2B:5Y:monthly_average | Published narrative of monthly residual-maturity basket; reference month distinct from edition | Monthly frequency fails daily gate |

NZL, BGR, IRL, DNK, LTU, HRV, SVN, AUT, PRT remain unimplemented slots. Some already have promising researched files, but research coverage is not implementation coverage. The source research document contains those candidates.

## Provenance and fallback

Annual IMF metadata controls vintage, unit and projection start. Forecast end is derived globally before per-country completeness checks. Exact ISO3 rows are selected for the configured universe; aggregates are never selected as country substitutes. Metadata last-modified dates are retained separately from the HTTP retrieval time.

The April 2026 statistical appendix Table A8 is on physical PDF page 23 (printed page 22). Its 15 year columns, country footnote suffixes and Unicode negative signs are parsed generically. Every overlapping API/PDF cell must agree within 0.051 percentage points before any missing cell is filled. At the initial live check all 27 configured rows parsed; 15 SVK years were filled. Existing API values keep their precision. A new edition without a registered matching PDF keeps missing cells unavailable.

`data/cache` retains immutable SHA-256 response objects and URL/method/body-keyed validators. ETag / Last-Modified revalidation may reuse a response only after an explicit HTTP 304 and matching hash. A failed refresh never falls back to the cache as fresh data. Requests have connect/read timeouts, bounded retries and a run-wide request budget. Normal 404 responses are not retried.

## Extension contract

1. Select an official source and verify issuer, local currency, 5Y definition, percentage-point unit, frequency and actual observation date.
2. Add a boundary parser with synthetic fixtures for dates, missing rows, duplicates and scale. Do not multiply decimals by 100 unless source metadata requires it.
3. Register a route returning `Observation` with source URL, retrieved_at, source_date, series, definition, currency, tenor and raw hash.
4. Test a bounded live request. Source changes must produce errors rather than infer a plausible replacement series.
5. Keep `baseline_compatible: false` until the definition comparison is accepted. Only mark redistribution `allowed` after a documented rights review; public access alone is insufficient.
6. Update both editable and packaged YAML defaults, the coverage table and tests.

Fiscal and FX redistribution flags remain `pending`. Yield reuse remains `pending` except the two scoped clearances below. No raw provider downloads are bundled or committed. Public mode conservatively suppresses an entire row's provider-derived numbers and classifications when any required provider is pending. Observation metadata remains inspectable without values. RBA units must explicitly be percent per annum; the Japan header must declare %. BoC response metadata must still identify a 5-year series, and the Riksbank series catalogue is checked once each run for maturity and closure. For metadata-poor sources, unit interpretation remains the researched source contract; Belgium is explicitly unverified and its raw observation is excluded from derived metrics until unit evidence is accepted. Market Quality is an explicit unpopulated extension point; no manually invented quality score is supplied.

## 2026-10-04 extension

The four additional adapters are connected routes, not approved scoring inputs. ISL
selects nominal par rather than indexed or zero-coupon columns and preserves
correction flags / workbook note references in observation provenance. ESP checks
5Y sovereign, percentage and daily metadata; source/notes footer rows are metadata.
SVK keeps the actual date of the estimate, never the workbook retrieval date. ISR
keeps YYYY-MM and frequency=monthly and excludes incomplete future months; no
month-end daily observation is invented. The daily gate rejects monthly periods.
See [live evidence and remaining gaps](research/2026-10-04-connected-sources.md).

CZE discovers a published PDF link on the official monthly bulletin index, validates
the edition and monthly percent metadata, and reads only the explicitly labelled
5Y yield from that edition’s commentary. The reference month must be no later than
the edition and at most three months behind. Changed or ambiguous narrative wording
fails closed; no historical PDF fallback or invented daily date is used.
See [Czech publication evidence](research/2026-10-04-czech-publication.md).


## 2026-10-05 scoped publication clearance

PRT direct BPstat series `12099457` and the exact Croatian-language HRV G8b
catalogue resource have documented reuse clearance. This approves only reuse
within the registered URL/series scope; neither route is implemented or Baseline
approved. The English G8b resource, other BPstat series and third-party products
cannot inherit this clearance.

For scoped routes, public output checks every present yield observation against
its URL, configured series, ISO3 and observation redistribution state. Missing
scope, evidence or attribution keeps the row redacted. HRV also requires the
provider modification date in provenance, printed dynamically with its attribution
and licence notice; a past review date is never represented as the current source
date. CLI, Markdown and HTML share these notices. Fiscal and FX clearance is still
required before any row's provider-derived numbers may be published.

Scoring, maturity definitions, stale/unit checks and Adjusted availability are
unchanged. See [approval scope and verification](research/2026-10-05-publication-gate-update.md).
