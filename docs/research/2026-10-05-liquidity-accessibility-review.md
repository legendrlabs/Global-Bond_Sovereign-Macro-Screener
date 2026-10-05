# Liquidity and accessibility source review

The purpose is a 27-country sovereign research screener. Delayed daily yields can support ranking/flow inspection; tolerance for a short delay does not resolve differences in the definition of structural inputs. This follow-up records source discovery rather than asserting successful observation collection.

## Official major-market liquidity candidates

| Country | Source and observed publication structure | Definition issue before implementation |
| --- | --- | --- |
| Korea | MOFE links its residual-maturity OTC Treasury statistics to KRX: https://ktb.moef.go.kr/curbSrviveExprtnNtpbnDdelngQy.do → https://kasp.krx.co.kr/ktbasp/ktb/ktb40205.jsp. The page labels its source KOFIA and shows trading volume, amount and transaction count, in KRW 100 million, for multiple residual-maturity buckets. | 3–5Y is a maturity bucket, not the generic 5Y yield observation. No populated observation table was retrieved; query period, dynamic request and reported unit need validation. |
| United States | NY Fed primary-dealer statistics: https://www.newyorkfed.org/markets/counterparties/primary-dealers-statistics. Weekly data are published Thursdays at about 4:15pm with the previous week's statistics; export and API routes are advertised. | Primary dealers are the reporting perimeter. Positions, transactions and financing are distinct; the exact Treasury transaction series, units, release date and duplication conventions must be established before deriving any turnover ratio. No live numeric response was retrieved. |
| Japan | JSDA OTC bond statistics: https://www.jsda.or.jp/en/statistics/bonds/index.html. Current workbook link: https://www.jsda.or.jp/shiryoshitsu/toukei/tentoubaibai/koushasai.xlsx. Definitions: https://www.jsda.or.jp/en/statistics/bonds/Explanatory_Materials2024.pdf. | Member-reported yen OTC transactions, monthly, generally face amounts in JPY 100 million. Exchange transactions excluded; auction and BOJ purchases are included. Outright/repo and JGB basket columns must be distinguished. Publication is generally on the 20th or following business day. No workbook observations were retrieved. |

On 2026-10-05 direct Python requests to the NY Fed API documentation, the JSDA workbook and the Korean KRX page each returned `ReadTimeout` with a `(5,15)` connection/read timeout. Search/open retrieval confirmed explanatory pages and the Korean empty table schema. This is not evidence that the APIs cannot work in another environment.

None of these is a verified common 27-country liquidity input. No market-size-to-liquidity conversion, price-volatility proxy, stock-market turnover or average of incompatible perimeters is introduced.

## Common-source candidates

- OECD's 2026 sovereign-borrowing chapter describes the 2025 survey of liquidity changes: https://www.oecd.org/en/publications/global-debt-report-2026_e9d80efd-en/full-report/sovereign-borrowing-outlook_4470147b.html. An improvement response is not an absolute liquidity level. No comparable 27-country numeric observation feed was verified.
- ECB FM metadata describes worldwide coverage depending on business needs and notes licensing limits on external dissemination of MDP data: https://data.ecb.europa.eu/data/datasets/fm/data-information. Catalogue presence alone does not establish a public bid/ask feed or rights to all underlying observations. The indexed metadata was retrieved; a subsequent direct open failed.
- FTSE institutional nominal-government-market accessibility is a plausible framework, not proof of retail broker availability: https://www.lseg.com/en/ftse-russell/fixed-income-country-classification. Prior review found an April 2026 table and an October placeholder; this follow-up did not retrieve a newer completed classification. No FTSE classifications or licensed numeric data are imported.

## Report change

The existing structural-input inventory now includes reviewed **research links**, source scopes and outstanding verification requirements. These are explicitly `RESEARCH_LINK`, with `usable_for_scoring=false`. The shared report groups five unique candidate links; a country appearing in the candidate table means it needs review, not that the source covers it or an observation exists. The inventory still has no liquidity/accessibility values, normalized Market Quality or Adjusted ranking. This adds no HTTP requests or dependency.

Next numeric implementation requires an actual sample response and a source contract covering metric, reporting population, frequency, unit, date and permitted use. Until then the useful delivered output is partial Baseline plus independently labelled size and reported-credit diagnostics.

Validation: all 162 existing tests passed after the report extension. The public synthetic summary contains exactly five grouped candidate references across 27 country diagnostics, each ineligible for scoring and with no liquidity/accessibility value. Diff whitespace validation passed. No claim of live data success or newly enabled ranking is made.
