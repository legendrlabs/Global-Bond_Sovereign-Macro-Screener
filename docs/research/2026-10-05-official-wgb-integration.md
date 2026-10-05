# Official-first / WGB fallback validation — 2026-10-05

User-approved scope: use official yield data first across the universe; use WGB when official data fails, is unavailable, has an invalid contract or is older than seven calendar days. Preserve actual observation dates. For matching values with differing WGB dates, use the older confirmed date and retain a discrepancy warning.

## Implementation and checks

- Existing official routes and their definition approvals are retained. All 27 countries have explicit WGB routes; US 10Y uses the same source-selection policy.
- WGB identity, domestic context, tenor, percent unit, active unique maturity row, historical URL, finite values and duplicate dates are validated. Curve, historical latest value and available price-table yield must match within 0.0005 percentage points.
- Yearless curve dates are resolved to the nearest year around the historical observation, then future dates and seven-day age are checked independently. This handles both directions of a date discrepancy and December/January boundaries.
- The primary curve header must end with a unique Last Update column and its expanded column spans must match the data row. An added trailing column cannot become the observation date.
- Provider, date, age, WGB fallback flag, official failure reason and date warnings are shown in reports and CSVs. Successful fallback does not leave an unresolved source-collection error.
- Raw payloads and hashes remain in private local caches. WGB cannot inherit official redistribution approval; public output removes numeric observations, derivatives and value-bearing notes.

## Actual run

Private run `20261005T102122-279d8e3e`, as-of 2026-10-05:

- Valid 5Y yields: **27/27**.
- Selected official observations: **8** (ISL, NOR, KOR, NLD, DEU, SVK, GBR, FRA).
- Selected WGB observations: **19**.
- US 10Y: collected through WGB after the official request failed.
- KOR used the official October 2 observation; WGB date discrepancies for CAN and LTU used October 2 instead of the history series' October 5 record.
- IMF fiscal request failed with ReadTimeout. The complete report therefore remains DATA_HOLD, Baseline 0/27 and Adjusted 0/27 in this particular run. This is not a claim that scores have become ready.

The finalized adapter also replayed all 27 previously archived real WGB responses successfully, including the three date discrepancies KOR/CAN/LTU. The real-run public redaction and generated report hashes were verified. Provider raw responses and private reports are not committed with this record.

## Review and limits

Independent review found two important defects (asymmetric year inference and trailing-column date selection). Both were reproduced in failing tests and fixed; their regression tests now pass. The suite contains 121 passing tests before packaging verification.

One minor diagnostic limitation remains: very long combined official/fallback failure messages are truncated by the existing report error limit, which can omit the tail of the fallback reason when both sources fail. Successful fallback reasons are preserved in the selected observation.

WGB annualized sovereign yields remain a separate definition. The user subsequently approved their use as Baseline yield inputs; they retain the WGB label and redistribution remains pending. This does not relabel them as official par/zero-coupon/benchmark observations, fill Market Quality, change score formulas or publish a new release.
