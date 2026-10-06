# Bulgaria: observed BGN history rebased at euro adoption

## Scope and decision

Resolve BGR FX continuity without changing Slovakia's yield eligibility, the
Baseline formula, the Market Quality requirements, or redistribution flags.
Keep current currency assignment `EUR` from **2026-01-01**. Do not backdate euro
membership or treat all earlier observations as historical EUR observations.

The reviewed history contract starts on **2020-07-10**. This is the scope of the
evidence reviewed here, not the original start of Bulgaria's currency board.
The ECB describes the BGN currency board and its continued fixed EUR parity at
ERM II entry. ERM II's ordinary +/-15% band is not itself evidence of an exact peg.

## Official evidence

- [ECB Economic Bulletin, Issue 6/2020: BGN and HRK in ERM II](https://www.ecb.europa.eu/press/economic-bulletin/focus/2020/html/ecb.ebbox202006_01~db5e37768d.en.html): BGR entered on 2020-07-10 and retained its currency board. Unlike BGR, HRK was not committed to an exact peg; this change does not authorize HRV history.
- [ECB, Bulgaria introduces the euro, 2026-01-01](https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260101~c830245e42.en.html): adoption and official conversion of **1 EUR = 1.95583 BGN**.
- [ECB technical update, 2025-12-17](https://www.ecb.europa.eu/services/using-our-site/technical-updates/html/ecb.mid_update251217.et.html): BGN reference-rate publication stops from 2026-01-02.
- [ECB historical daily reference XML](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml): observed same-day BGN and KRW rates per EUR. The saved original confirms BGN observations through 2025-12-31, with BGN rate **1.9558**, and no BGN observations after the transition.

## Calculation and failure conditions

Before adoption, calculate **KRW per BGN** from matching ECB observations and
multiply by **1.95583 BGN per EUR**. From adoption, use **KRW per EUR** directly.
This produces a series in equivalent current-currency units and avoids an
artificial return caused by a unit change. Preserve the original observation
dates; do not create BGN rates from a constant or fill missing dates.

The legal conversion has five decimals, whereas published BGN observations have
four. Accept an old BGN/EUR observation only within half a published decimal unit
(**0.00005**, plus numerical epsilon) of parity. Preserve this rounding difference
in the rebased series rather than forcing BGR's volatility to equal EUR's exactly.
A breached parity rejects each affected lookback window. The series measures KRW
reference-rate risk, not executable dealer spreads or the former peg's tail risk.

Require a reviewed contract, matching current-currency assignment and adoption
dates, valid positive rates, actual old-currency observations covering the window
start within seven calendar days, and the existing sample-count, gap and freshness
checks. Missing pre-adoption history cannot pass merely because more than 200
post-adoption EUR observations exist. Invalid contracts and future assignments
remain unavailable. When a window is wholly after adoption, old observations are
no longer required. Normal countries retain their original currency-history gate.

The report includes `FX_HISTORY_REBASED`, a currency-history table, and the
transition contract in row provenance and the run manifest. The contract does
not contain raw daily rates. Public mode keeps existing numerical redaction.
Both editable and packaged country configurations include the same contract.

## Actual-source replay (not a new live refresh)

Latest ECB download attempt timed out. The validation below uses the unchanged
original from the existing 2026-10-06 run, and does not claim a fresh download.

- Original retrieval: **2026-10-06T04:47:58.069007+00:00**.
- SHA-256: `4db461d4caecbd066d81cb77c407084c6415c109960978b772f791cbd02bfb00` (recomputed and matched).
- Latest observation: **2026-10-05**; last BGN observation: **2025-12-31**.
- All reviewed BGN/EUR observations from 2020-07-10 in this original: **1.9558**.
- Evaluation date: **2026-10-06**.
- 1Y / 3Y usable observations: **255 / 764**; rebased old-currency observations in the 3Y window: **570**.
- Annualized volatility: **0.08114747819800132 / 0.07286687565241792** (decimal ratios, approximately **8.115% / 7.287%**).
- 1Y maximum drawdown: **-0.16047813385071708**; FX errors: **none**.

This resolves BGR's FX hold for the verified original. It does not by itself
release global DATA_HOLD: SVK remains definition-unapproved and every other
freshness/completeness gate still applies. Adjusted remains unavailable because
Market Quality is unpopulated. No main merge or package release is implied.

## Regression verification

Tests cover the transition-unit boundary and rounding, pre-adoption gaps and
missing history despite enough post-adoption points, breached parity in each
lookback horizon, stale data, malformed/unverified contracts, assignment-date
mismatches, future assignments, post-transition-only windows, removal of the
contract, public numerical redaction, source metadata and unchanged SVK/Adjusted
holds. The full main-based branch suite passes **218 tests** (206 existing + 12 new).
