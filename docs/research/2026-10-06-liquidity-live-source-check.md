# Keyless liquidity source checks after preview.4

Checked on 2026-10-06 KST (2026-10-05 UTC). This is an observation of this execution environment, not a promise of access from every installation. The earlier requests timeouts did not prove permanent source failure. A bounded follow-up using `curl_cffi`, Chrome-compatible transport and a 20-second timeout returned the following responses. No runtime collector or score was enabled by this research.

| Country | Request | Actual result | Remaining issue |
| --- | --- | --- | --- |
| USA | NY Fed API specification, series catalogue, series-break catalogue and latest SBN2024 survey | HTTP 200; JSON observations received. The selected nominal-Treasury transaction aggregate has observation date 2026-09-23. | Confirm units, dealer reporting and transaction duplication conventions, publication lag, missing-value markers and exact series definitions before scoring. This is not whole-market turnover or a single 5Y bond. |
| Japan | JSDA current monthly OTC workbook | HTTP 200; complete workbook parsed, with monthly total rows from April through August 2026. | Separate outright from repo, government bonds from other bonds, regular plus special members from securities firms alone, and maturity classes. Auction/BOJ activity and reporting duplication need explicit treatment. |
| Korea | KRX Treasury OTC page and its observed AJAX endpoint | HTTP 200 for both; the requested August–September 2026 monthly table contains only headers and **no observations**. | Access success is not data collection success. Resolve populated query behaviour before introducing a collector. No API key requirement was established for this page. |

## Reproducible endpoints

- NY Fed specification: `https://markets.newyorkfed.org/static/docs/markets-api.yml`
- NY Fed definitions: `https://markets.newyorkfed.org/api/pd/list/timeseries.json`
- NY Fed breaks: `https://markets.newyorkfed.org/api/pd/list/seriesbreaks.json`
- NY Fed current survey: `https://markets.newyorkfed.org/api/pd/latest/SBN2024.json`
- JSDA workbook: `https://www.jsda.or.jp/shiryoshitsu/toukei/tentoubaibai/koushasai.xlsx`
- Korean page: `https://kasp.krx.co.kr/ktbasp/ktb/ktb40205.jsp`
- Korean POST: `https://kasp.krx.co.kr/ktbasp/ktb/ktb40205_table.jsp`, form `fr_work_dt=202608`, `to_work_dt=202609`, `date_sch_type=mm`; Referer is the page above. These parameters were read from the page script, not guessed.

## Parsing evidence and constraints

The NY Fed latest response includes observations with multiple as-of dates across different indicators. Do not assign the response's maximum date to every series. Select an exact `keyid`, reject conflicting duplicates, preserve its own date, and treat `*` as missing rather than zero. The catalogue describes `PDGSWOEXTTOT` as Treasury transactions excluding TIPS, combining inter-dealer-broker and other transactions. Some other aggregate catalogue descriptions appear inconsistent, so ticker-like names alone cannot establish definitions.

JSDA's `(Ｂ)一般売買高` sheet identifies outright transactions and sell-plus-purchase reporting, in JPY 100 million. The workbook notes that rounding can prevent exact sum reconciliation. The separate sell and purchase sheets corroborate the structure. The government-bond total includes Treasury discount bills; the medium-term column is a class rather than the screener's 5Y benchmark. Use the explicitly reported totals without adding their component classes or combining total and dealer rows again. A monthly figure should not be divided by an assumed number of business days without a documented calendar and comparable reporting scope.

The downloaded JSDA workbook SHA-256 is `d30b1d6ee90e074df2e0807b852251f07f26e1ba63aee3aae510f8fd16e13077`. Raw responses and observed numeric values are retained locally for validation and are not included in this public research note or release assets.

## Implementation boundary

The evidence supports keyless **source-specific diagnostics** for USA/Japan after source contracts and parser tests. It does not support a harmonized 27-country liquidity rank. Source-specific frequency, perimeter and date must stay visible. Redistribution remains pending until verified. API-key onboarding remains deferred. preview.4 contains the earlier research-link inventory, not these future collectors; Market Quality and Adjusted ranks remain unavailable.

## Implemented follow-up (not included in preview.4)

The proposed collector now validates the NY Fed catalogue and selected observations, and JSDA's explicit all-member outright government-bond totals. Three live requests through the common cached HTTP client returned two `AVAILABLE_DIAGNOSTIC` rows: USA observed 2026-09-23 and Japan August 2026 (period end 2026-08-31). `curl_cffi` transport, raw hashes and original retrieval timestamps were recorded. No collection failure was replaced by a cached success.

A reproduction isolated the initially failed runtime collection to the transport's five-second connection cutoff: both Chrome profiles failed at about 5,002 ms with `(5,20)`, whereas a scalar 20-second timeout received the same catalogue with either default or research User-Agent. Exact NY Fed Markets and JSDA hosts now use a scalar 20-second timeout, Chrome-compatible transport and requests fallback. IMF's existing policy is unchanged; lookalike hostnames are excluded. This is an environment-specific connection diagnosis, not evidence of a WAF fingerprint block.

A cookie-preserving GET/POST historical Korean query for January–December 2025 also returned HTTP 200 with no data cells. Korea remains unconnected; the empty response does not establish that source observations do not exist.

Validation: all 175 tests passed, including parser schema/date/unit/duplicate/missing-value checks, independent source failure, exact transport host matching, and demo/public redaction. Live private and public report generation confirmed that observed liquidity numbers appear privately, are hidden publicly, and never create Adjusted scores. API-key onboarding and cross-country liquidity normalization remain deferred.
