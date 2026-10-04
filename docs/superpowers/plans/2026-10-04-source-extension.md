# Official source extension — 2026-10-04

Continue the approved sovereign-macro design without changing scores or quality gates.
Scope: ISL, ESP, SVK and ISR, using the official endpoints already researched.
Each endpoint returned HTTP 200 in a bounded unauthenticated request today.

1. Add synthetic boundary tests before implementation. Catch nominal/indexed or
   par/zero column confusion, wrong maturity, wrong units, monthly/daily confusion,
   missing values, duplicate dates and future observations.
2. Add strict parsers and routes. ISL FLV nominal par 5Y requires Excel percentage
   formatting and converts fractions to percentage points; preserve correction
   flags and note references. ESP selects D_G0B1F0ZO with percentage/daily and
   sovereign 5Y metadata. SVK selects Yields_SK / ZCY5Y, retaining observation dates
   despite weekly publication. ISR validates exact nominal 5Y monthly zero-coupon
   SDMX dimensions and keeps YYYY-MM periods. Monthly periods remain ineligible
   under the existing daily quality gate. No month-end date is invented.
3. Register both editable and packaged defaults. All four retain pending rights
   and baseline_compatible=false. Source coverage is not scoring eligibility.
4. Run the full unittest suite and bounded live collectors; record observations,
   errors, definitions and remaining gaps in source docs. Update the existing PR
   branch without merging main. No provider raw files are committed.
5. Obtain a fresh review of this extension; fix material findings with regression
   tests, then publish and report exact coverage.

Review focus: percent/fraction scale, wrong sovereign/tenor/real series acceptance,
monthly date handling, stale weekly data, schema drift and public redaction.
