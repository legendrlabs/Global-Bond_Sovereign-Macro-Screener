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
| ESP | Banco de España D_G0B1F0ZO | Daily unstripped sovereign 5Y outright spot-market rate; selection/weighting unconfirmed | Yes, disclosed research proxy |
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
5. Keep `baseline_compatible: false` until the definition comparison is accepted. The explicit WGB policy is an exception: validated WGB annualized yields are accepted as Baseline inputs while retaining their provider label. Only mark redistribution `allowed` after a documented rights review; public access alone is insufficient.
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
# 2026-10-05: official-first selection with WGB fallback

All 27 countries now have an explicit `wgb_slug` in both development and packaged country configuration. Existing official routes remain primary. Selection accepts an official observation only after country/currency/tenor/metric, definition, unit, daily period and seven-calendar-day freshness validation. Failed, invalid, monthly or stale official observations trigger the same-country, same-tenor WGB adapter. Successful fallback carries the official failure in `selection_reason`; it is a warning, not an unresolved collection error. An invalid fallback is never replaced with a stale official value.

WGB requests the country page, `/wp-json/country/v1/main`, its exact maturity historical page, and `/wp-json/common/v1/historical`. These are website internal interfaces, not a guaranteed public API contract. JSON requests include Origin/Referer and JSON Content-Type. The adapter verifies page context, government-yield units, maturity, domestic country identity, exact historical URL, curve headers, unique active maturity row, history duplicates and finite numbers. Curve/history/price yields must agree within 0.0005 percentage points. A missing price table is disclosed as a warning; curve and history remain required.

For matching values with different dates, use the older curve-row/history date. A yearless row date is resolved against the history year, including the previous December at a year boundary, then must pass the seven-day gate. Preserve provider update timestamps separately. Neither HTTP modification timestamps nor current collection time supply the observation date. The raw payloads are hashed and cached, and every selected WGB observation links all four request hashes in its notes.

WGB is a separate `annualized_government_yield` definition. The project now treats a validated WGB observation as usable for the Baseline yield input by explicit policy; it remains labelled as WGB and does not inherit another provider's benchmark/par/zero-coupon label or redistribution permission. Existing official definition approvals remain unchanged, and redistribution remains pending. In public output, both values and value-bearing notes are removed. The official-first policy applies to US 10Y monitoring as well as all-country 5Y collection.

## IMF connection failure and validated edition reuse

A network failure in the initial DataMapper indicator request formerly left the entire fiscal bundle absent. Fiscal collection now persists raw responses for a validated complete API edition and re-parses them on transport failure. This is an explicit fiscal source policy; generic HTTP transport still fails a refresh rather than representing cached data as newly fetched.

The saved manifest binds API URL, country/PDF label scope and PDF edition configuration to hash-verified original responses. Each series' own source, unit, projection year and last-modified metadata must agree with the indicator catalogue. Legacy HTTP responses can be promoted only after full revalidation and a retrieval cohort spanning at most 24 hours. A saved dataset must have a current forecast start year, no future retrieval dates and an original retrieval age within 210 calendar days (configurable). A new edition or revision observed during a partial live request blocks rollback; data-validation failures are never treated as transport failures.

Successful reuse preserves original per-source retrieval timestamps and source dates, reports the edition and `latest_release_verified=false`, and adds `FISCAL_SNAPSHOT_USED` as a warning. It does not approve yield definitions, complete the Market Quality axis or grant redistribution permission. No snapshot exists before a successful validated fetch or legacy-cache promotion; ephemeral CI environments do not retain private source caches automatically.

## Source-specific liquidity diagnostics

### Issuer-published sovereign credit diagnostics

`market_inputs.credit_enabled=true` connects free, keyless official AFT (France),
Finanzagentur (Germany) and NZDM (New Zealand) pages independently of liquidity and
BIS size. `market_inputs.enabled` still gates all structural requests. Exact headings,
headers, one S&P row, grade/outlook vocabulary and actual assessment dates are checked.
A future scheduled review is not an assessment. Per-country errors remain isolated;
failed refreshes do not reuse cached success. Retrieval time and last rating assessment
are separate, and an old assessment is not automatically an expired rating.

Only NZDM's domestic column has explicit currency classification. Its separate official
[2026/27 securities overview](https://debtmanagement.treasury.govt.nz/resource/new-zealand-government-securities-overview-2026-27)
establishes long-term basis when both domestic/foreign grades and outlooks agree with
the current ratings page. The older overview assessment date is retained as basis evidence,
never substituted for the current agency-row date. Missing or conflicting basis evidence
keeps a reported domestic-currency diagnostic with unverified term. This comparison
uses the issuer's own reported values; it does not certify an agency's full methodology.

Germany's summary establishes long-term but not currency. Its S&P link labelled
2026-04-24 points to a 2025-06-13 PDF, so that PDF is not used to certify the current
row. France's summary specifies neither term nor currency. These two rows remain
`REPORTED_TYPE_UNVERIFIED`. All three retain `value=None` and `usable_for_scoring=false`.

A successfully collected issuer diagnostic takes priority over WGB's unspecified
reported rating, including when the selected yield is from an official provider.
If the issuer fails, a valid WGB reported rating can remain visible with the issuer
failure attached. Reports show rating kind and assessment/action date. Hash, retrieval
time, transport and optional basis metadata remain in provenance. Public output hides
all local/foreign ratings, outlooks and action values; synthetic output discards real
issuer download metadata. No credit, Market Quality or Adjusted score is created.

AOFM's actual new Treasury Bonds workbook link is registered in the research catalogue,
but 502/timeouts prevented acquisition in this runtime. No numeric AOFM parser is
implemented without the actual workbook's schema and units.

See [the Gemini source verification](research/2026-10-06-gemini-source-verification.md)
and [the issuer implementation check](research/2026-10-07-issuer-credit-source-check.md).

With `market_inputs.liquidity_enabled=true`, bounded requests collect the NY Fed series catalogue and current SBN2024 survey, JSDA's current OTC workbook, and ADB's government-bond turnover CSV. Each country's failure is isolated from BIS size, other liquidity sources and Baseline. No stale response is reused after a failed refresh.

`market_inputs.enabled` remains the global switch (disabled when absent). Set `enabled=true`, `size_enabled=false`, `liquidity_enabled=true` to collect liquidity without requesting BIS; old configurations default `size_enabled` to true. The legacy positional/keyword `imf_transport` injection is IMF-only. New `browser_transport` injection serves general approved browser-compatible hosts; an explicit IMF override takes precedence for IMF requests.

USA selects `PDGSWOEXTTOT` only after checking its catalogue definition: primary-dealer Treasury outright transactions excluding TIPS, inter-dealer brokers plus others, all maturities. Values remain weekly trading-day averages in USD million, with each selected series' own observation date. This reporting perimeter is not all-market unique turnover. The `*` marker, invalid or negative numbers, duplicates and definition drift fail closed.

Japan selects the explicitly reported government-bond total from JSDA's all-member **outright** sell-plus-purchase sheet, preserving JPY 100 million per month. The data include Treasury bills and auction/BOJ activity and exclude exchange trades and repo. Totals are not summed with components; no assumed daily conversion is applied. Headers, sheet, unit, month and duplicate totals are validated. Only completed months are used.

Explicit `YYYY年度` / `YYYY計` aggregate rows are excluded, while malformed monthly labels still fail validation. Workbooks with missing dimensions or more than 5,000 rows / 128 columns are rejected before scanning. Only the four required columns are iterated. There is no blank-gap early exit that could silently discard later observations. Synthetic size and liquidity diagnostics discard real download metadata.

Freshness bounds are separately configured as `weekly_max_age_days=30` and `monthly_max_age_days=120`; these are structural-input limits, not changes to the seven-day yield rule. Rows carry `AVAILABLE_DIAGNOSTIC`, provider, unit, period, definition, hash, retrieval time, transport and `usable_for_scoring=false`. Stale values are hidden. Public output respects component and whole-row redistribution gates; demo output suppresses real liquidity values and provenance. These inputs do not create Market Quality or Adjusted scores. Direct Korean OTC transaction-volume collection remains unconnected; the separate ADB turnover diagnostic below supplements Korea and Japan.

### ADB government-bond turnover: Korea and Japan

`adb_turnover_enabled=true` (default when liquidity collection is enabled) adds a separate `market_inputs.turnover` diagnostic, preserving Japan's JSDA monthly volume. Disable this provider with `adb_turnover_enabled=false`. The request uses [ADB's CSV endpoint](https://asianbondsonline.adb.org/downloads/bond_turn_ratio_csv.php) with `economies=KR^JP`, current and prior years, and `frequency=Quarterly`. The server may return other economies despite the filter, so country codes are filtered from the actual rows. Metadata availability is never treated as a country observation.

The CSV's indicator, quarterly definition, frequency and complete government/corporate column contract are checked. Only **government** turnover is selected: quarterly traded value divided by the average outstanding at previous/current quarter ends, excluding repo. Amounts preserve LCY billions (KRW or JPY); the dimensionless ratio preserves the published two-decimal rounding, which is verified against the amounts. ADB already halves reported sales-plus-purchases for these economies; no further division or annualization is applied. Missing, nonfinite or negative numbers, nonpositive denominators, ratio mismatches, malformed quarter ends and duplicate periods invalidate that country without erasing the other. Future periods are excluded.

`turnover_max_age_days=185` is a configurable diagnostic freshness policy (about two quarters), not a provider release deadline or the daily yield rule. The latest completed quarter is selected; stale ratios and underlying amounts are hidden, rather than falling back to an older quarter. A failed refresh reports `UNAVAILABLE`, with no cached-success substitute. Provenance includes the request URL, hash, retrieval time, transport, observation date, [indicator metadata](https://asianbondsonline.adb.org/xml/get-indicator.php?code=Bond_turn_ratio) and [country-note chart](https://asianbondsonline.adb.org/charts/bond_turn_ratio.php?module=data-portal&economies=KR%5EJP&years=2026&frequency=Quarterly).

Country notes identify OTC coverage and upstream JSDA (Japan) / KG Zeroin (Korea). Japan's government category includes municipal, government-guaranteed, FILP-agency and transportation/NHK bonds; Korea's precise category composition remains unverified. Both cover all maturities. These differences preclude a comparable sovereign-only or 5Y liquidity ranking, Market Quality normalization or Adjusted score. Private reports show the turnover diagnostic separately. Public output suppresses the ratio **and its numerator/denominator**, including provenance, when either component or whole-row reuse gates block release. Synthetic demo output discards real values and download metadata. Test fixtures are synthetic, not redistributed supplier observations.

See [live source checks](research/2026-10-06-liquidity-live-source-check.md). Requests use browser-compatible transport only on exact approved IMF, NY Fed Markets, JSDA and the three issuer hosts, with requests fallback; compatibility is not a guarantee that any execution environment can reach a source.

## 2026-10-06 Spain definition decision and Slovakia hold

Spain’s exact daily series D_G0B1F0ZO is accepted for exploratory Baseline comparison. The original `secondary_market_bucket` label is retained; the definition note identifies outright spot transactions in unstripped State bonds and explicitly discloses unresolved issue selection and weighting. No constant-maturity, benchmark, or redistribution approval is inferred. Freshness, units, identity and fiscal gates remain unchanged.

Slovakia ZCY5Y remains a valid displayed zero-coupon observation, excluded from Baseline ranking. The row now includes the definition source and reason. The referenced 2015 IFP manual gives a model discount function using exponential discounting but also presents a discrete-compounding introductory relation. Current workbook convention must be verified before deriving a par coupon from multiple zero-curve maturities. No derived observation is generated by this change.

See [source evidence and limits](research/2026-10-06-spain-slovakia-definition.md).

## UK and Sweden source-specific liquidity diagnostics

UK DMO quarterly GEMM purchases plus sales and Riksbank daily secondary-market GVB/SP adjusted turnover are collected independently. Their definitions, period-specific freshness gates, discovery, validation and redistribution limits are documented in [the UK/Sweden evidence](research/2026-10-06-uk-sweden-liquidity.md). Neither measure creates cross-country scores; stale or incomplete Swedish observations are not displayed as current values.
