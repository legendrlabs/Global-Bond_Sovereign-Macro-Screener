# Official issuer credit diagnostics — 2026-10-07 KST

The development branch extends the v0.1.5 codebase. Existing UK and Sweden liquidity
adapters remain intact. This is not a published package release.

## Sources and interpretation

| Country | Official source | Selected S&P row date | Classification | Result |
| --- | --- | --- | --- | --- |
| New Zealand | [NZDM current ratings](https://debtmanagement.treasury.govt.nz/investor-resources/credit-ratings) | 2026-08-28 | Domestic currency; long-term basis checked separately | AVAILABLE_DIAGNOSTIC |
| Germany | [Finanzagentur](https://www.deutsche-finanzagentur.de/en/federal-funding/government-as-issuer/ratings) | 2026-04-24 | Long-term; currency not established by summary | REPORTED_TYPE_UNVERIFIED |
| France | [AFT](https://www.aft.gouv.fr/en/frances-credit-ratings) | 2026-05-29 | Term and currency not established by summary | REPORTED_TYPE_UNVERIFIED |

NZDM's [official 2026/27 securities overview](https://debtmanagement.treasury.govt.nz/resource/new-zealand-government-securities-overview-2026-27)
contains an explicitly long-term local/foreign table. Both grades and outlooks match
the current table. Its older S&P date, 2025-10-14, is retained as classification evidence;
it does not replace the current table's 2026-08-28 date. If a later run finds a mismatch,
missing caption, newer basis than current row or unavailable overview, the reported
domestic rating is retained with unverified term. No scoring eligibility is inferred.

The German summary's S&P link labelled 2026-04-24 points to
[an actual 2025-06-13 research PDF](https://www.deutsche-finanzagentur.de/fileadmin/user_upload/Finanzagentur/pdf/ratingberichte/20250613_S_P_Research_Update.pdf).
The document was checked; it cannot establish the currency basis of the 2026 row.
AFT's future scheduled review is not used as its assessment date.

## Production transport check

All four current/basis requests returned HTTP 200 through the production HttpClient's
curl_cffi transport in a bounded issuer-only run. Source bodies remain private. Every
row records its URL, raw SHA-256, retrieval time and transport; NZDM also records basis
URL/hash/retrieval time and the older basis date. A failed refresh cannot reuse an old
response except after explicit HTTP 304 hash revalidation.

The collector is independent of yield-provider selection and the liquidity switch.
Successful official issuer diagnostics take precedence over WGB's unspecified reported
ratings. A valid WGB report survives issuer failure with that failure attached. Public
reports omit grades, outlooks and actions in both display and provenance. Synthetic
reports discard real issuer download metadata. Credit and Adjusted scores remain absent.

## AOFM ruling

The official Data Hub's actual link was resolved to
[new_turnover_-_treasury_bonds.xlsx](https://www.aofm.gov.au/sites/default/files/2026-05-29/new_turnover_-_treasury_bonds.xlsx).
Direct download returned HTTP 502 (159-byte error body), while another transport timed
out. Therefore only the candidate URL and failure evidence were registered. No numeric
parser, turnover ratio or guessed workbook schema was introduced. The 2026 survey
perimeter changes require checking the actual workbook before adding Australia.

## Verification

- Baseline on the v0.1.5 branch: 206 tests passed.
- New synthetic parser, collector, privacy, report and switch tests: 13 passed.
- Whole suite after integration: 219 tests passed.
- Production refresh: three issuer pages plus NZDM basis page, four HTTP 200 responses.
- Existing UK/Sweden and ADB diagnostic contracts remain covered by the whole suite.

Tests use invented grades and dates rather than copied issuer rating tables. No raw
issuer page, rating snapshot or downloaded workbook is committed. This note contains
classification and date evidence only; it is not a rating recommendation.

## Whole-branch review and decisions

A fresh reviewer independently ran the 219-test suite and found no Critical or
Important issues. One Minor was initially deferred: explicit synthetic tests for
foreign-only, outlook-only and newer-basis-date mismatches. The follow-up below now
protects those implemented safeguards against regression.

The review retained the following decisions:

- AOFM stays a candidate until its workbook can be acquired. Cost: Australia is not
  added to observed liquidity coverage; no unsupported numerical schema is guessed.
- A separate branch based on v0.1.5 preserves the user's original pending edits and
  existing UK/Sweden adapters. Cost: this development change still needs integration.
- An older matching NZDM overview establishes reported term classification only.
  Cost if that inference is wrong: diagnostic wording, never a score; mismatches remain
  unverified and assessment dates are kept separate.
- WGB notes are blocked in public rows by the existing publication gate. The alleged
  eligible-WGB notes leakage is unreachable today; any future gate change needs
  independent credit privacy tests.
- Source availability was checked by the executor's four actual production HTTP 200
  requests. Future uptime is not guaranteed; failures retain unavailable diagnostics.
- The continuing instruction authorizes a reviewable draft PR. Existing work is
  preserved; a package release and main-branch merge are not part of this change.

## Delivery status

Implementation and review are complete. An earlier automatic approval review blocked
public GitHub publication because implementation authorization did not explicitly
cover the complete code/documentation payload. No workaround was attempted.
On 2026-10-07 at 04:13 KST, the user explicitly approved publishing the reviewed
branch and creating a draft PR. Delivery proceeds under that approval; no package
release or main-branch merge is included.


## External review follow-up

The supplied Gemini review was checked against the actual implementation. A dedicated
regression test now isolates four conflicts: foreign grade only, local outlook only,
foreign outlook only, and a basis date newer than the current assessment (but not
future relative to the run). Each must retain both current grades/outlooks and the
current assessment date, report the exact verification error, keep term unverified,
and remain ineligible for scoring.

The 14-test issuer suite passes. In isolated in-memory mutations, disabling the
rating/outlook comparison causes three subcases to fail; disabling the date-order
guard causes one to fail. No production parser behavior was changed.

The review's statement that public output removes all source hashes is incorrect.
An actual publish check confirmed the public manifest retains the issuer raw hash
without grade/outlook/action keys. Demo output has no real issuer provenance. The
integration test now explicitly protects public hash preservation. Hashes identify
source objects for verification; they do not contain the original rating table.

The fixed 2026/27 overview is a reviewed source edition. On fiscal-year rollover,
check the newly issued official page and update **both** BASIS_URL and its expected
heading/table contract; do not fabricate the next URL from the calendar. A missing
or conflicting edition retains the current domestic-currency diagnostic with term
unverified and a basis_verification_error.
