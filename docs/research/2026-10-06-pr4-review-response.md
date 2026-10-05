# PR4 external review response

Reviewed against head `aad93ffa9b193d3666eefa9e8a5c538929f1d169`. API-key onboarding remains deferred by the user. This response separates reproduced defects from documented limitations and unverified assumptions.

| Finding | Assessment | Action |
| --- | --- | --- |
| One invalid BIS country clears all size data | Reproduced. A missing confidentiality flag, invalid multiplier/value or duplicate in one matched country raises a response-wide exception. This affects the optional size inventory, not all Baseline collection. | Group matched series by country. Reject an invalid country's entire input with `INVALID_DATA` and a reason while retaining other countries. Truncated/malformed XML still rejects the whole response. |
| Demo provenance exposes values/serialized notes | Reproduced when supplied notes contain values, or when a mixed bundle is passed to evaluate with demo enabled. Normal CLI demo uses synthetic inputs rather than collecting live data. | Strip `value` and `notes` from all demo row provenance even in private mode. Copy provenance before redaction so shared fiscal/FX bundle metadata is not mutated. Verify HTML, manifest and country CSV exports. This does not make arbitrary real input bundles synthetic. |
| Mixed quote conventions distort strict comparison | A real research limitation. Treasury/Japan compound conventions are supported by official explanations. However WGB's `Annualized Yield` header does not itself establish annual effective compounding for every country. Japan's constant-maturity definition alone does not establish that it is the same par-curve construction as Treasury. The 4.5–5Y KOFIA range does not establish a 4.75Y average, or simple-interest yield calculation. | Preserve previously accepted exploratory nominal-5Y research comparisons and definition disclosures. No blanket AEY conversion or invented average maturity. A strict harmonized-return ranking needs country/source-specific convention evidence and a separately reviewed method. |
| Demo scope displays every country as unavailable | Reproduced display defect: zero live eligibility was presented as actual country missingness. | Keep zero live-eligible counts and the synthetic label, but omit missing-country lists in demo scopes. Do not count synthetic data as usable live inputs. |
| Five countries permanently missing under S1311 | Saved replay found no matching data for those countries under the chosen scope/period. That alone does not prove permanent absence or that every country reports only S13. S13 general government is a different reporting perimeter. | Keep exact scope, expose missing-series status, and do not silently substitute S13. Alternate series can be researched as separately labelled diagnostics. |
| Official-selected countries lack WGB rating | Known limitation: the diagnostic reuses the selected WGB yield response with no additional network requests. No claim of full credit coverage is made. | Remains disclosed. A separate credit collector requires country/type validation and a bounded request design; it is not introduced as part of this bug repair. |

## Confidentiality handling

The suggested default `CONF_STATUS=None → F` is not adopted. This repair isolates failures without weakening the explicit-public evidence rule. SDMX attribute attachment/inheritance should be verified against the actual BIS DSD and response before accepting omitted observation attributes. An unverified flag yields a country-local diagnostic, not a fabricated public value.

## Definition evidence

- Treasury FAQ: https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/interest-rates-frequently-asked-questions — CMT is a point on the theoretical par curve, potentially different from a particular security.
- Japan MOF Q&A: https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/qa.htm — semiannual compound constant-maturity interest rates from prevailing secondary-market fixed-income JGB prices.
- WGB collection verifies the actual table header `Annualized Yield`; no verified provider-wide AEY conversion contract has been established. The mathematical conversion `(1+y/2)^2-1` is valid for the stated nominal semiannual convention, but applying it to a subset does not harmonize unverified conventions elsewhere.

## Verification

Before the repair, country-isolation fixtures raised the reported BIS errors and the demo provenance/display tests failed. After the repair, all 166 tests passed. New coverage verifies country-local confidentiality and duplicate failures, unchanged valid-country values, demo provenance redaction across exported files, input-bundle immutability and synthetic eligibility without country-missingness lists. No fresh live market data success, completed Market Quality or changed ranking formula is claimed.
