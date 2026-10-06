# SVK research-proxy decision and BGR integration replay

## Proposed research comparison policy

This branch combines the reviewed BGR currency-continuity implementation from
PR #14 with a conditional SVK nominal 5Y research-comparison approval. It does not
convert, relabel, or claim equivalence between the NBS zero rate and par or coupon
bond yields. The actual value, observation date, `estimated_zero_coupon` type,
`ZCY5Y` series and provider compounding metadata stay intact. Approval is a project
comparison policy, not an NBS endorsement of the model or an executable yield.

[The NBS source page](https://nbs.sk/en/statistics/financial-markets/interest-rates/estimated-yield-curve/)
identifies NSS estimates from sovereign securities and updates the daily-observation
workbook weekly. NBS explicitly notes persistent inaccuracies arising from limited
liquidity and securities, and that the data is for public information rather than
price/yield quotation or investment-opportunity identification. Its historical
error discussion is not a calibrated confidence interval for today's 5Y value.

The convention uncertainties documented in the
[previous definition investigation](2026-10-06-spain-slovakia-definition.md) are
still unresolved. The proposed decision supersedes **only the ranking exclusion**
for exploratory nominal comparison, with `BASELINE_DEFINITION_DIFFERENCE` and a
note disclosing NSS/zero/YTM/par differences, unverified workbook compounding,
and no par conversion. No annual-compounding harmonization is claimed.

Setting `baseline_compatible: false` restores the explicit definition hold.
Date, unit, country, currency, tenor, metric, yield-type, fiscal horizon and
publication gates remain active. Public numbers remain redacted where permissions
are pending. The Baseline formula, weights, source selection and freshness rules
are unchanged. Market Quality and Adjusted are still unavailable.

## Independent verification of the Gemini review

PR #14's GitHub Tests run 37524923559 completed successfully. Its BGR exact-date,
observed-history, rounding, parity, coverage, gap and stale-data protections remain.
The previously supplied simulated point estimates and ranks are **not** accepted
as actual-source results. A positive synthetic fixture only proves readiness logic.
The separate saved-source replay below uses the original non-synthetic observations.

## Saved-source replay, not a new live refresh

- Evaluation date: **2026-10-06**.
- Original run: `20261006T045142-17d742d6`.
- Original report file hashes were checked against its manifest.
- **28** saved yield observations (27 5Y plus USA 10Y); their **27** distinct raw
  file hashes were recomputed and matched. No yields were manually inserted.
- The original IMF **April 2026** snapshot manifest and all six response hashes
  were verified. The production fiscal parser and existing same-edition PDF
  fallback were rerun. Replay use is disclosed as `FISCAL_SNAPSHOT_USED` with
  original retrieval metadata and `EXPLICIT_SAVED_SOURCE_REPLAY_NOT_LIVE`.
- ECB original hash: `4db461d4caecbd066d81cb77c407084c6415c109960978b772f791cbd02bfb00`.
  The original XML was reparsed; BGR counts remain **255 / 764** for 1Y / 3Y.
- Readiness result: **READY**, `safe_to_use=True`, Baseline **27/27**, real yield
  **27/27**, FX 1Y **27/27**, required watch-market tenor present, system errors **[]**.
- Adjusted: **0/27**, `safe_to_use_adjusted=False`; all values remain `None`.

Private replay files are written to a separate `results/svk-bgr-replay` output,
without replacing the live current pointer or last-success record. This is not a
new network refresh, a public numerical publication, a main merge, a package
release, or proof that the next live run will be complete. Optional structural
input collection is not rerun by this readiness replay.

## Regression verification

The main-based integration suite passes **222 tests**: the 218-test BGR branch
plus four SVK/readiness regression methods. Existing strict-policy fixtures remain
explicitly strict rather than silently losing their coverage. New regressions
cover the raw zero-rate identity and warning, an explicit opt-out, stale/future
observations, mismatched identity/units/tenors/types, positive complete-fixture
readiness, and renewed HOLD when old BGN history, USA 10Y, a fiscal horizon cell,
or an error-free collection is missing. Synthetic mode remains ineligible.
