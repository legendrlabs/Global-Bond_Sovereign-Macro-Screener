# Official-first yields with WGB fallback implementation plan

> **For agentic workers:** Use superpowers:executing-plans in this session. Steps use checkbox syntax.

**Goal:** Use valid official sovereign yields first for all 27 countries, and fetch WGB when an official route is unavailable, invalid or older than seven days.

**Architecture:** A WGB adapter returns existing Observation objects with source evidence. A selection layer validates official and fallback observations independently; pipeline/reporting show the selected provider, actual observation date, age and fallback reason.

**Tech Stack:** Python 3.11+, requests, Beautiful Soup using the standard HTML parser, unittest.

**Spec:** User-approved conversation on 2026-10-05: official-first for every country, WGB fallback, seven calendar days, older date when matching values have different dates. Existing docs/superpowers/specs/2026-10-04-sovereign-macro-design.md governs formulas, definitions and publication.

## Global Constraints

- Keep 27 country IDs and existing score formulas, weights and definition approvals.
- Never substitute 10Y for 5Y or silently change source dates.
- WGB annualized sovereign yields have a distinct definition; do not label them official benchmark/par yields or inherit official redistribution clearance.
- User decision after implementation: validated WGB annualized yields may enter Baseline calculations; retain the WGB definition and keep redistribution pending.
- Match country, tenor, percent unit, finite values and series; reject future/stale dates, conflicting duplicates and discontinued series.
- Allow matching WGB values with differing dates using the older confirmed date; expose the discrepancy as a warning.
- Keep provider raw responses in local caches only; do not commit them.

## Review Focus

- New-year rows without a year: choose a uniquely recent date from the history date, never the collection date.
- Network failures and fallback errors: preserve diagnostics without retaining a stale official value.
- Missing/changed HTML headings or multiple maturity rows: fail closed.
- Official redistribution approval: cannot authorize WGB fallback publication.
- HTTP budget: enough for all-country fallback without unbounded requests.

### Task 1: WGB adapter and HTTP support

**Files:** src/sovereign_macro/wgb.py, http.py, pyproject.toml, tests/test_wgb.py, tests/test_http.py.

**Interfaces:** collect_wgb(client, country, as_of, tenor=5) -> Observation; client.fetch(url, method='GET', body=None, headers=None).

- [x] Write tests for actual-shaped page/JSON responses, metadata checks, seven-day date handling, duplicate/nonfinite/discontinued rejection and HTTP headers.
- [x] Run targeted tests and verify the new behavior fails before implementation.
- [x] Implement the adapter and optional HTTP headers; retain all response hashes in cache/provenance.
- [x] Run targeted tests and the project suite.

### Task 2: Selection and visible provenance

**Files:** src/sovereign_macro/yield_selection.py, collect.py, pipeline.py, publication.py, report.py, summary.py, cli.py, models.py, both config/defaults copies, tests/test_yield_selection.py.

**Interfaces:** collect_preferred_yield(client, country, config, as_of, tenor=5) -> Observation; yield_contract(country, observation, config) -> metadata contract.

- [x] Test valid official preference, fallback after stale/monthly/invalid/failed official data, seven-day boundaries, isolation and public redaction.
- [x] Verify failures, then implement routes for every country and source/age/fallback fields.
- [x] Show provider/date/fallback warnings in HTML and summary; increase the bounded request budget for fallback collection.
- [x] Run targeted tests and the project suite.

### Task 3: Live validation and delivery

**Files:** README.md, docs/data-sources.md, docs/research/2026-10-05-official-wgb-integration.md.

- [x] Replay saved responses through the production adapter and run live selection for the universe.
- [x] Verify 5Y/10Y selection, actual dates, fallback reasons, raw hashes, public redaction and packaged default configuration.
- [x] Run the full test suite and review the complete diff.
- [x] Commit and publish a reviewable feature branch; no automatic merge or release.
