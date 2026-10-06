# Bulgaria FX continuity and New Zealand official benchmark

## Source contracts

- [ECB euro introduction, 1 January 2026](https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260101~c830245e42.en.html): Bulgaria adopts EUR on 2026-01-01; the fixed conversion rate is 1 EUR = 1.95583 BGN.
- [RBNZ B2 definitions](https://www.rbnz.govt.nz/en/statistics/series/exchange-and-interest-rates/wholesale-interest-rates): indicative secondary-market government benchmark closing yields, published with a one-business-day lag. A designated benchmark is not an exact residual-maturity CMT.
- [RBNZ methodology update](https://www.rbnz.govt.nz/statistics/stats-alerts-and-updates/2025/sa-04): the NZFMA close and publication timing changed on 2025-08-25. Preserve this break in observation notes.
- RBNZ workbook: `https://www.rbnz.govt.nz/-/media/project/sites/rbnz/files/statistics/series/b/b2/hb2-daily-close.xlsx`; exact 5Y series `INM.DG105.NZZCF`, unit `%pa`.

## Calculation and quality limits

Before the transition, compute `KRW/EUR-equivalent = (KRW per EUR / BGN per EUR) × 1.95583`. After the transition, use observed KRW per EUR. Retain the published BGN precision; do not round the statutory factor to the ECB reference quote's four decimal places. This is a redenominated predecessor history, not a claim that Bulgaria used EUR before accession. Missing predecessor rates remain missing. The 200/600-observation minimums, gap and seven-calendar-day freshness gates are unchanged.

RBNZ selection checks publisher, table, series definitions and Data sheet headers before reading values. Workbook dimensions are explicitly reset because the captured supplier file declares populated sheets as A1:A1. Expanded ZIP size, entry count and scan bounds remain limited. The RBNZ benchmark is approved only for the existing nominal-yield research Baseline, with definition warnings. It does not establish a comparable liquidity input or an Adjusted score.

## Validation status

The previously downloaded actual RBNZ workbook parsed 2,193 observations; its latest observation date was 2026-10-05 and its publication date was 2026-10-06. No supplier values or original workbook are committed. A subsequent live official request and WGB fallback both timed out in this environment. Fresh end-to-end network success is therefore not claimed. A newly downloaded ECB history was not obtained in that attempt; transition arithmetic, boundary dates, missing predecessor rows, sample counts, stale data and public redaction are tested with synthetic inputs.

Redistribution permissions remain pending. Public reports keep provider-derived values redacted, while displaying the history definition. No complete 27-country rerun, full comparison readiness, or personal skill update is implied by this implementation.
