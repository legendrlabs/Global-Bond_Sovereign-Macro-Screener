# Sovereign Macro Screener — public distribution design
Design date: 2026-10-04 (Asia/Seoul)
Repository: legendrlabs/Global-Bond_Sovereign-Macro-Screener
Status: design for review; application implementation and CI are not yet present.

## Purpose and constraints
Build a reproducible weekly macro sensor for fiscal health, sovereign yields, expected real yields and currency risk from a KRW investor perspective. Preserve the supplied Baseline formula and independently compute Adjusted scores. Outputs inform subsequent analysis of the US discount-rate environment; they never issue trading instructions or orders.
The default distribution must require no user API keys, citizenship verification, provider accounts or broker credentials. Authenticated providers are optional adapters, disabled by default. Missing observations remain missing. Never impute net debt from gross debt, substitute a 10Y yield for 5Y, or replace an individual euro sovereign yield with a euro-area aggregate. Country-specific result corrections are prohibited; source routing and dated currency assignments are explicit metadata.

## Universe
ISO3 IDs: ISL, NOR, AUS, NZL, KOR, CZE, BGR, CAN, IRL, DNK, LTU, SWE, HRV, NLD, SVN, DEU, SVK, AUT, PRT, ISR, ESP, GBR, FRA, ITA, BEL, USA, JPN.
Keep all 27 rows even when a score is unavailable. Display names and country IDs are separate. Bond currency is a dated assignment, not an immutable country property. Shared currency series are fetched once; historical currency changes require documented continuity before multi-year FX metrics are enabled.

## Recommended architecture
A small Python package with configurable source adapters:
config/countries.yaml — ISO3, display names, dated currency assignments, source-series routing.
config/scoring.yaml — versioned normalization and regime thresholds.
src/sovereign_macro/ — HTTP/cache, fiscal, inflation, yields, FX, validation, Baseline, Adjusted, regime, reporting, CLI.
tests/ — formula, source-schema, gate, publication and fixed-vintage regression checks.
docs/methodology.md and docs/data-sources.md.
data/raw/<run_id>/ — immutable responses plus hashes and retrieval metadata.
data/processed/<run_id>/ — standardized observations and validation outcomes.
results/ — latest.md, sovereign_scores.csv, country_details.csv, macro_regime.csv, quality.json, run_manifest.json.
results/runs/<run_id>/ — execution snapshots; last_success metadata remains distinct from the current run.

The selected approach uses public official APIs plus official machine-readable downloads. A scraping-only implementation is less stable; a manual-only spreadsheet cannot support the requested weekly refresh. A source adapter returns observations, never scores.

## Source feasibility evidence
The following checks were executed from this session without Authorization headers, keys or cookies. A successful HTTP response is not a full semantic or production validation.

| Provider / route | Observation | Use |
| --- | --- | --- |
| IMF DataMapper v2 indicators | HTTP 200 JSON; official documentation advertises v2 | Metadata/edition discovery |
| IMF v2 GGXWDN_G01_GDP_PT | HTTP 200; April 2026 Fiscal Monitor; 26/27 requested ISO3 keys present; SVK absent | Net debt, with explicit SVK missing flag |
| IMF v2 GGXCNL_G01_GDP_PT | HTTP 200; April 2026 Fiscal Monitor; all 27 ISO3 keys present; projection-year 2026; terminal year 2031 | Overall fiscal balance |
| IMF v2 G_XWDG_G01_GDP_PT | HTTP 200; April 2026 Fiscal Monitor; all 27 ISO3 keys present; projection-year 2026; terminal year 2031 | Gross debt |
| IMF v2 PCPIPCH | HTTP 200; April 2026 WEO; all 27 ISO3 keys present; projection-year 2026; terminal year 2031 | Forecast average CPI inflation |
| Bank of Canada Valet BD.CDN.5YR.DQ.YLD | HTTP 200 JSON, metadata identifies a 5-year government benchmark yield, recent observations present | First confirmed sovereign 5Y adapter |
| ECB eurofxref-hist.xml | HTTP 200 XML; 7,106 dated entries; newest date 2026-10-02 | FX candidate pending continuity and per-currency validation |
| ECB eurofxref-hist.csv | HTTP 200, but newest parsed date 2010-02-14 in this session | Reject for current-run FX, do not silently prefer it |
| ECB SDMX FX request | Read timeout during first probe | Public API candidate, not verified in this session |
| OECD public SDMX dataflow catalogue | HTTP 200 XML | Dataset discovery; no 27-country 5Y coverage claim |
| BIS public SDMX dataflow catalogue | HTTP 200 XML | Market-size / FX discovery; no 5Y coverage claim |
| IMF new portal API link | Redirected to sign-in during documentation check | Not a required default dependency |

Canonical official references:
- https://www.imf.org/external/datamapper/api/
- https://data.imf.org/Datasets/FM
- https://data.imf.org/Datasets/WEO
- https://www.bankofcanada.ca/valet-api-how-to/
- https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html
- https://data.ecb.europa.eu/help/getting-data-web-services-sdmx-0
- https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html
- https://data.bis.org/help/tools
- https://www.bankofengland.co.uk/statistics/yield-curves

IMF public base: https://www.imf.org/external/datamapper/api/v2/
The older v1 route responded during probing but is not the default: the official documentation advertises v2, and a country-qualified v1 request returned additional countries. All parsing must select exact ISO3 keys and reject aggregates.

Source catalog entries track: authentication mode, access-check status, semantic-check status, covered series/countries, units, frequency, retrieval URL, licensing/attribution URL, and latest successful retrieval. Public API access and permission to redistribute raw provider data are separate questions. Distribute original code and derived outputs with attribution; only bundle provider raw files after their permitted use is established. Runtime caching is separate from public repository bundling.

## Observation contract and dates
Each value stores ISO3, currency, metric ID, value, canonical unit, observation period, observation/forecast classification, provider, dataset, series, edition, source date, retrieved_at (UTC), URL, and raw-response hash. Yield observations additionally require tenor_years, yield_type and compounding.
Percent-of-GDP and yields use percentage points (5.06 means 5.06%, not 0.0506). Canonical FX is KRW per unit of bond currency. No automatic unit guessing; conversion requires documented source metadata.
Use the run's Seoul calendar year for ND_current and require that year to exist. Use the edition's projection metadata to identify forecast_start_year. Forecast_end_year comes from dataset coverage, before country-specific missingness is evaluated. Missing terminal values invalidate the affected country rather than shortening its horizon.
Baseline fiscal-balance averaging includes every annual observation from the edition's forecast_start_year through forecast_end_year. This convention is versioned. Annual reference-year rollover with an older edition is flagged; do not fall back silently to the previous calendar year.
Store the IMF indicator last-modified timestamp separately from edition publication date. Do not invent a release date from a retrieval date.

## Baseline (unchanged)
g(D) = 1 / (1 + exp((D - 70) / 15)).
CurrentDebtScore = 15*g(ND_current).
FutureDebtScore = 25*g(ND_future).
BalanceScore = clip(10 + mean(overall fiscal balance over the declared forecast period), 0, 10).
F = CurrentDebtScore + FutureDebtScore + BalanceScore.
R_baseline = 25*(sqrt(1 + yield_5y_pct) - 1).
S_baseline = 2*sqrt(F*R_baseline).

Preserve full precision internally, round only for display. Use a numerically stable logistic evaluation.
A negative nominal yield produces a negative R, so the original final formula is generally outside its real-valued domain. Mark BASELINE_DOMAIN_ERROR rather than clipping, taking an absolute value, or changing the original model. For yield <= -1 percentage point the inner square-root domain also fails. Validate finite values before scoring.
F is bounded by 50; R may exceed 50 and S may exceed 100. These are disclosed properties, not a reason to truncate Baseline. Net debt below zero gets NET_ASSET_SOVEREIGN without country-specific corrections.

## Adjusted v0.1 candidate
Weights remain Fiscal 0.40, Real Yield 0.30, FX 0.20, Market Quality 0.10.
FiscalNorm = F/50.
Expected inflation = arithmetic mean of the five annual CPI forecasts following the run reference year, all from one WEO edition. Require all five years; do not extrapolate if fewer are available. Record the entire horizon and the period mismatch inherent in comparing annual forecasts with a market yield. RealYield is yield_5y_pct minus that mean; it is a forecast-based approximation, not an inflation-linked market yield.
Initial economic normalization candidate:
RealYieldNorm = logistic((RealYield_pct - 1.0)/1.5).
FXNorm = exp(-(FXVol_1y_decimal/0.15)^2).
These are explicit design parameters, not empirically validated optimal thresholds. Before release, assess score/rank sensitivity to real-yield centers 0/1/2 percentage points, scales 1/1.5/2, and FX scales 0.10/0.15/0.20 on the actual collected distribution. Preserve parameters and all changes in the scoring version; never tune to a desired country rank.
AdjustedScore = 100 * product(norm_i ** weight_i).
A valid zero input gives zero. Missing or invalid inputs give unavailable, never zero. Do not reweight the remaining axes.

Market quality requires source-backed metrics for market size, liquidity, credit quality and accessibility, with dated source definitions and a published mapping. Availability has not yet been established. Until a defensible model is approved and its inputs verified, MarketQualityScore and full AdjustedScore remain unavailable. This is an explicit release limitation, not a fabricated completion claim. Raw fiscal, real-yield and FX axes can still be reported independently.

## FX method
For same-date EUR cross rates: KRW_per_currency = KRW_per_EUR / currency_per_EUR; EUR has a mathematically exact denominator of 1.
If base_currency equals bond_currency, FX risk is exactly 0 by a general identity rule. No country-name branch is used.
Compute log returns on valid, matched consecutive observations; annualized standard deviation uses sqrt(252), sample standard deviation, and decimal units. A calendar-year window needs at least 200 paired observations and no unresolved long gap (>5 provider business days). Do not forward-fill gaps into artificial zero returns.
Provide 3Y volatility only with at least 600 paired observations and valid currency continuity. Compute FX maximum drawdown on the KRW-per-currency value path. Report FX risk, not directional forecasts.

## Validation, ranking and quality
Validate source identity, official metadata, unit, finite value, series definition, dates, duplicate keys, horizon and currency alignment before score calculation. A plausible numeric value does not prove the correct unit.
Yield/FX staleness threshold: 7 calendar days from the actual observation date, configurable and recorded. Future observation dates are invalid. Fiscal/inflation edition age is checked against the provider release calendar or latest officially discovered edition, not the daily-data threshold.
A source change is flagged and compared for semantic consistency, never accepted as an unannounced fallback. Benchmark/par/zero yields are not interchangeable without a documented compatible definition; mismatches are unranked by default.

Every row has separate usable_baseline, usable_adjusted and metric validity fields. Report all 27 countries; rank only valid scores and label partial coverage conspicuously.
Global safe_to_use is conservative: true only if every requested country has a valid Baseline, all core inputs pass, and there is no systemic error. Full-model availability is separately represented by safe_to_use_adjusted, with its own coverage. A partially usable report therefore may have DATA_HOLD globally while transparently exposing usable rows for inspection.
quality.json includes errors/warnings by country/metric/model, coverage counts, missing/stale countries, source dates/editions, and last successful run. It never claims a fully validated model based on the success of an unrelated axis.

## Macro regimes
All labels are deterministic, threshold-versioned and accompanied by the input metrics and triggered conditions.
Fiscal trend: ND_future - ND_current <= -5 GDP percentage points => IMPROVING; >= 5 => DETERIORATING; otherwise STABLE. Also report fiscal-balance trajectory separately.
Real yield: <0% LOW; 0% through 2% NEUTRAL; >2% HIGH.
FX risk: annualized volatility <8% LOW; 8% through 15% MEDIUM; >15% HIGH.
Sovereign carry: provisional risk-adjusted description, not an expected total return; ATTRACTIVE requires real yield >2%, FX risk LOW and fiscal trend not DETERIORATING; UNATTRACTIVE when real yield <0%; other complete cases NEUTRAL. Required missing inputs => UNAVAILABLE.
US_DISCOUNT_RATE_REGIME evaluates the same generic discount-rate rule configured for the observed market ISO3. Base level from real yield: <0% EASING; 0-1% NEUTRAL; >1-3% RESTRICTIVE; >3% HIGHLY_RESTRICTIVE. Elevate one category when BOTH nominal 5Y and 10Y >=5% and fiscal trend is DETERIORATING, capped at HIGHLY_RESTRICTIVE. All required inputs must be valid. These thresholds are transparent heuristics and require sensitivity review, not validated causal predictions.
Report the US and other configured watch markets using metadata. No NASDAQ BUY/SELL outputs.

## Tests and regression evidence
Unit tests cover exact supplied formulas, stable logistic tails, zero/negative yields, missing inputs, weight handling, explicit unit conversions and rank ties.
Source-contract tests distinguish IMF overall balance GGXCNL_G01_GDP_PT from primary balance GGXONLB_G01_GDP_PT; verify exact country mapping, source edition, complete years and no aggregate leakage.
FX tests cover pair inversion, EUR identity, base-currency identity, date alignment, sample count, gaps and currency transition.
Gate/publication tests cover stale HTTP-200 responses, malformed downloads, provider timeout, systemic failures, mixed editions, missing terminal years and failure after an earlier successful run.
April 2026 reference cases: ISL, NOR, AUS, KOR, CAN, USA, JPN. Archive licensed source observations and independent expected calculations. User-supplied rounded ND/F examples are reference assertions with tolerances, not complete fixtures: average fiscal balance and the original averaging horizon must first be recovered. Never manufacture balance values to make F match.
Network-free fixture tests run in CI; live source health checks have separate statuses. No assertion of April 2026 regression completion until verified source fixtures exist.

## GitHub Actions and publication
Weekly Sunday 11:15 UTC (20:15 KST), manual workflow_dispatch, and test CI on pushes/PRs.
Only standard repository GITHUB_TOKEN is needed to publish the repository's own results; no financial data-provider key is required. Public read-only fetching can run with contents:read, while a separate publication job uses contents:write. Pin actions to reviewed revisions in implementation.
Cache by edition/hash with conditional retrieval, bounded retries/backoff, provider timeouts and request budgets. Check edition changes before reusing fiscal data.
Write each run into a staging directory, validate output schemas, then publish an internally consistent snapshot. latest.md and quality.json always reflect the current attempt. On failure emit DATA_HOLD and keep last_success separately dated; never serve old ranks under a new as-of date.
Always upload diagnostic artifacts when possible. Publication failure remains a workflow failure. GitHub cron timing is best-effort and must not be represented as a guaranteed execution minute.

## Review and acceptance
This commit is a concrete design and feasibility record only.
Implementation acceptance remains the user's original 27-country pipeline, authentic April 2026 regression, real-yield/FX metrics, defensible Adjusted model, quality gates, six outputs, weekly CI, tests and methodology documentation.
Unavailable sources, market-quality inputs and regression evidence remain explicitly reported limitations. No claim of complete operational coverage is allowed while these are unresolved.
Before coding: review this written design, then create and review the implementation plan in the required development workflow.
