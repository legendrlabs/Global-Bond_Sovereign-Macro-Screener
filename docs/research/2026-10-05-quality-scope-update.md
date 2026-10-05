# Quality scope update

## Implemented

Korea, US and Japan official nominal 5Y observations are accepted for exploratory Baseline comparisons while preserving distinct definitions and explicit warnings. No collection priority, freshness, unit, publication or currency-continuity rule is relaxed. Report availability is split by scope and the usage mode precedes the global hold. Fiscal rollover no longer incorrectly adds a definition hold.

Definition evidence reviewed on 2026-10-05:

- US Treasury FAQ: https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/interest-rates-frequently-asked-questions — 5Y CMT is the par curve's constant-maturity point, not necessarily a particular bond. Bond-equivalent annual quotes preserve the Treasury convention. Search retrieved the official FAQ; the subsequent open returned a server error.
- Japan MOF Q&A: https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/qa.htm — constant-maturity secondary-market yields, semiannual compound convention, JSDA reference prices; full official page retrieved.
- KOFIA final quotation page: https://www.kofiabond.or.kr/ — the official indexed final quotation table identifies code 3007 as the government 5Y basket with remaining maturity 4.5–5Y. Its dynamic page open returned no text. This review establishes definition scope, not a fresh market observation or independent live-value cross-check.

## Market Quality finding and next design

This is still an unimplemented model, rather than a transient API error. The approved original spec requires market size, liquidity, credit quality and accessibility. The current pipeline passes `None` to the fourth Adjusted axis. A credit rating alone would change the model's meaning and is not implemented as a substitute.

Source candidates reviewed:

| Axis | Candidate | Finding / outstanding work |
| --- | --- | --- |
| Size | BIS central government debt securities C2, https://data.bis.org/topics/DSS/tables-and-dashboards/BIS%2CSEC_C2%2C1.0 | Official outstanding amounts in USD billions; confirm domestic currency scope, all 27 country coverage and common period by downloading actual observations. Government total debt is not an interchangeable bond-market-size measure. |
| Liquidity | National debt agencies / exchanges | Need directly comparable sovereign turnover or bid/ask measures; World Bank stock-market turnover is not sovereign bond liquidity. Coverage and definitions not yet established. |
| Credit | Rating agency sovereign long-term local-currency rating; WGB candidate mirror | Validate rating type, agency and dated effective rating for every country. CDS or fiscal score is not an interchangeable rating input. |
| Accessibility | IMF AREAER capital controls, https://www.imf.org/en/publications/sprolls/annual-report-on-exchange-arrangements-and-exchange-restrictions | Official annual exchange/capital-control information exists. Database access can require subscription: https://www.elibrary-areaer.imf.org/Login/NoAccess.aspx. A public free 27-country bond-accessibility feed is not verified. |

Recommended next stage: a source-backed input inventory before selecting normalization or weights. For each axis require value, unit, observation period, source URL, retrieval time, raw hash and defined interpretation. Show the four components independently, with missing reasons. Only after actual coverage is known, review a versioned normalization proposal and its rank sensitivity, then connect the composite to Adjusted. Never replace a missing component with zero or reweight the remaining Adjusted axes.

This change deliberately does not claim complete Market Quality or complete Adjusted rankings.

## Follow-up: structural-input inventory

Added one optional BIS size request per live collection, isolated from Baseline collection errors. The exact filter is quarterly central government excluding social security (`S1311`), nominal value (`N`), liabilities (`L`), positions (`LE`), debt securities (`F3`), all original maturities, all currencies and all markets. Only USD with multiplier 9 is accepted, and values remain USD billions. This is a broad sovereign bond-market size observation, not the size or liquidity of a particular 5Y bond or of the local-currency investable index.

The parser rejects malformed/truncated XML, duplicates, nonfinite/negative values, unverified confidentiality and incorrect multipliers. Other sectors/valuations are excluded rather than added together. The latest completed quarter is selected; future quarters are not observations. Structural freshness is explicitly 365 days from quarter-end, separate from the 7-day daily-yield rule, and this parameter does not make a score or grant ranking eligibility.

Private reports now show the four Market Quality input statuses and the available size with its definition, period, source URL, raw hash and retrieval time. Unconnected components retain explicit reasons. Public-mode numerical redaction and the conservative entire-row gate cover the new nested input, too. No source observations are bundled in the distribution.

### Actual evidence and limitations

- Stored BIS narrow-response replay: 22 of 27 countries have a 2026-Q1 observation under the exact filter. Missing under this filter: AUS, ISL, ISR, NOR, NZL. Original XML prepared timestamp: 2026-10-03T15:52:59Z. Raw SHA256: `749b38e4ae5beb7c3c1455b6dbe23ca557d9c697dafd9e34fc0ca836f9597662`. This is stored original-response verification, not a successful current download. The broader raw response was truncated and rejected, rather than partially parsed.
- One fresh BIS request on 2026-10-05 timed out. Runtime reports that failure without treating it as new data or invalidating Baseline. A failed fresh request is not silently replaced with the research file.
- Cached WGB country-response identity checks found 19 country tables with an S&P row and a reported update date. A page context and exact POST cache key were matched for each. These rows do not establish same-agency long-term local-currency rating scope for 27 countries, so the credit component is not filled from an unspecified rating type.
- S&P's current indexed list describes a July 31, 2026 reference date, but the direct page extraction returned no rating table: https://www.spglobal.com/ratings/en/regulatory/article/sovereign-ratings-list-s101701846 . A successful full-table parse is not claimed.
- FTSE's official nominal government-market classification table contains accessibility levels and index-specific size/rating fields. The table retrieved from the current classification page is April 2026, and size is defined as index-eligible par amount at March 2026 month-end. It must not be joined to BIS total nominal bonds as if they were the same metric. The October 2026 announcement linked from the page is a placeholder rather than a completed new classification. Publication restrictions expressly cover storage/use/distribution, so no automated FTSE dataset is added to the package.
  - Classification page: https://www.lseg.com/en/ftse-russell/fixed-income-country-classification
  - Nominal table: https://www.lseg.com/content/dam/ftse-russell/en_us/documents/country-classification/ftse-fi-country-classification-for-nominal-government-markets.pdf
  - October placeholder: https://www.lseg.com/content/dam/ftse-russell/en_us/documents/country-classification/fixed-income-country-classification-october-2026-results.pdf
- OECD's 2026 report describes the 2025 sovereign secondary-market liquidity survey. Change in liquidity, turnover and bid/ask commentary are not an absolute liquidity score or a comparable 27-country numeric feed. Do not map an improvement indicator directly to high liquidity.
  - https://www.oecd.org/en/publications/global-debt-report-2026_e9d80efd-en/full-report/sovereign-borrowing-outlook_4470147b.html

## Validation

Editable package install succeeded in a fresh environment. All 149 tests passed, including five new tests covering official major-market eligibility, independent scope counts, stale/definition/unit rejection, public redaction and fiscal-rollover attribution. Demo report generation and diff whitespace validation passed. Synthetic tests establish behavior, not current market values.

One fresh direct request per official Korea, US and Japan route on 2026-10-05 ended in `HTTP_FAILURE:ReadTimeout` for all three in this execution environment. No new successful live values or complete live ranking are claimed. This does not negate the user's separately reported successful run.

Structural-input follow-up validation: all 157 tests passed. Eight additional tests cover scope/valuation separation, quarterly units, latest completed-quarter selection, future/stale periods, invalid/conflicting/truncated inputs, optional failure isolation, collector provenance and nested public/entire-row redaction. Private and public demo reports each contain 27 input rows; all generated file hashes were verified. Demo inputs are explicitly synthetic and unavailable for real rankings.
