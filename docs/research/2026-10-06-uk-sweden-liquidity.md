# UK DMO and Swedish Riksbank liquidity diagnostics

These adapters add source-specific observations to `market_inputs.liquidity`.
They never create Market Quality, Adjusted or country liquidity rankings.

## United Kingdom

Index: https://www.dmo.gov.uk/data/gilt-market/turnover-data/

Discover the labelled maturity-band XLSX from the official index instead of
freezing a dated filename. Verify Notes, units, unique maturity rows and totals.
Select the newest completed quarter in the newest eligible year; stop reading
older sheets after finding an observation. Q2 ends June 30, not the file date.

The measure is GEMM-reported purchases plus sales at market value, GBP million
per quarter, all maturities including index-linked gilts. Repo and derivatives
turnover is excluded. Trades between non-GEMMs are absent and dealer reports
can double-count. Never halve all reports or call this unique-trade or exact-5Y
volume. Quarterly age policy is 185 calendar days.

The October 6 download, `gemm-turnover-by-maturity-band-18092026.xlsx`, has SHA256
`5d1ee506cbf424a2d9d8ea756a86f97c2e383fa15209c331d1ed39f110791179`.
Its Q2 combined total was reproduced in private verification. Supplier amounts
and raw files are not published here. Redistribution remains pending.

## Sweden

Index: https://www.riksbank.se/en-gb/statistics/turnover-statistics/fi-market/

Discover the daily XLSX and validate the separate official definition workbook:
https://www.riksbank.se/globalassets/media/statistik/omsattningsstatistik/penning_obligationsmarknad/daily_fi_description.xlsx

Select GVB government bonds and SP spot, excluding PRIMM primary-market
counterparties. Inflation-linked bonds, bills, repo and forwards are separate
codes. Sum Adjusted amount (million SEK), already corrected for reporter
double-counting. Do not divide again. Coverage is a reporting-counterparty
sample, all maturities; not whole-market or exact-5Y coverage.

Require unique day/counterparty keys, finite nonnegative amounts, adjusted
amount no greater than raw amount and Complete=True for all latest-day rows.
Incomplete latest data fails without falling back to an older complete day.
Future rows are excluded. Daily age policy is seven calendar days.

The October 6 file SHA256 is
`9a8a477095545c9145f9680af3e29f42199401ad466d1a151946631d4533daae`.
Latest GVB spot date is September 25, 11 days old. Its adjusted sum was checked
privately; the current diagnostic is STALE and value=None. Website updates are not
trade dates. Raw files are not committed and redistribution remains pending.

## Controls and output

`liquidity_enabled` remains the master switch. `uk_dmo_enabled` and
`riksbank_enabled` independently disable their requests. Configuration copies
set `quarterly_max_age_days=185` and `daily_max_age_days=7`.
Discovery requires a unique HTTPS XLSX on the exact official host. Redirects,
ambiguous links, schema/definition failures are isolated by country. Bounds are
source-specific: Swedish history has 128,254 observations and cannot inherit
JSDA's 5,000-row cap.

Existing reports display units, actual period, definition, status and source.
Provenance includes data/index hashes and Sweden's description hash. Public
output hides pending amounts and demo replaces real diagnostics. NY Fed, JSDA,
ADB, yield selection and scoring keep their existing paths.

## Validation

Source-backed collector run on October 6 fetched both official indexes,
discovered current workbooks, checked Swedish definitions and reproduced the
hashes above. UK returned AVAILABLE_DIAGNOSTIC (98 days old); Sweden STALE.
Tests cover source selection, scope filters, units, duplicate/invalid data,
completeness, future/stale observations, independent flags/failures, and
public/demo amount masking. No whole 27-country live collection is claimed.
