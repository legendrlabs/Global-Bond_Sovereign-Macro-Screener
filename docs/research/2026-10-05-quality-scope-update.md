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

## Validation

Editable package install succeeded in a fresh environment. All 149 tests passed, including five new tests covering official major-market eligibility, independent scope counts, stale/definition/unit rejection, public redaction and fiscal-rollover attribution. Demo report generation and diff whitespace validation passed. Synthetic tests establish behavior, not current market values.

One fresh direct request per official Korea, US and Japan route on 2026-10-05 ended in `HTTP_FAILURE:ReadTimeout` for all three in this execution environment. No new successful live values or complete live ranking are claimed. This does not negate the user's separately reported successful run.
