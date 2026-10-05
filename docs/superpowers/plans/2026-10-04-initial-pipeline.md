# Sovereign Macro Initial Pipeline Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Ship a runnable keyless research pipeline, preserving missing inputs while additional sources are investigated.
**Architecture:** Source adapters return dated observations to a validation/scoring core. A run stages six standard outputs plus a local HTML viewer; current attempts and last successful runs remain separate. Source configuration separates numerical access, semantic compatibility, and redistribution eligibility.
**Tech Stack:** Python 3.11+, requests, PyYAML, openpyxl, pypdf; unittest; GitHub Actions.
**Spec:** ../specs/2026-10-04-sovereign-macro-design.md

## Authorization update
The user explicitly authorized implementation on 2026-10-04 KST despite incomplete acquisition: build now and strengthen data afterwards. This supersedes the earlier research-only gate. Unavailable sources and MarketQuality still remain unavailable; the scope is an initial runnable implementation, not full operational acceptance.
Execution: inline in a fresh checkout on feat/initial-pipeline; one independent whole-branch review.

## Global Constraints
- Preserve all 27 ISO3 rows and the exact Baseline formula.
- Fiscal 0.40, Real Yield 0.30, FX 0.20, Market Quality 0.10; no reweighting.
- Require the Seoul calendar reference year and complete declared fiscal/CPI horizons.
- Missing, stale, malformed, mismatched and unapproved observations cannot become fabricated numbers or ranks.
- No user/provider secrets; raw runtime caches are excluded from git and public artifacts.
- Unknown redistribution eligibility suppresses provider-derived numbers in public output.
- Network-free tests are distinct from live health checks and authentic April 2026 regression.

## Review Focus
- A failed current run after a valid earlier run must publish current DATA_HOLD, preserving separately dated last_success.
- IMF API ignores country filters: exact ISO3 and complete horizon selection must prevent aggregate leakage.
- Daily labels can contain old or blank observations: actual observation dates control freshness.
- Missing FX dates must not become artificial zero returns; historical currency changes cannot be silently joined.
- Public output must not expose raw or derived restricted-provider numbers merely because the request was keyless.

### Task 1: Core contracts, scoring, FX and regimes
**Files:** src/sovereign_macro/{models,scoring,fx,validation,regimes,config}.py; config/{countries,scoring,sources}.yaml; tests/test_core.py; pyproject.toml.
**Interfaces:** Observation dataclass with provenance and yield definition; baseline(nd_current, nd_future, balances, yield_pct); adjusted(fiscal, real_yield, fx_vol, market_quality, settings); fx_metrics(points, currency, as_of, provider_dates, continuity); evaluate_regimes(...).
- [x] Write failing tests for literal formula examples, negative domain, overflow-safe logistic, missing/zero adjusted inputs, FX inversion/identity/sample counts/gaps, ties and regime boundaries.
- [x] Run unittest and verify missing implementations fail.
- [x] Implement contracts and exact versioned calculations; validate finite values and no missing-axis reweighting.
- [x] Run complete suite and commit.

### Task 2: HTTP and verified source adapters
**Files:** src/sovereign_macro/{http,collect,fiscal,yields}.py; tests/test_sources.py; source catalog and documented provisional slots.
**Interfaces:** HttpClient.fetch(url, method, data) returns bytes plus retrieval metadata; FiscalData carries edition/horizon and annual observations; collectors return Observation lists and structured errors, not scores.
- [x] Write failing contract tests for mixed editions, incomplete years, generic same-edition PDF fallback, newest valid observations, Japanese era/units, KOFIA summary rows and time tokens, malformed sources, retries and timeout isolation.
- [x] Run tests and inspect expected missing-function failures.
- [x] Implement IMF+ECB and actual verified yield routes, prioritizing CAN, USA, JPN, AUS, NOR, Riksbank, KOR; add remaining verified file routes where their parser can be validated. Unimplemented/unverified sources remain explicit catalog slots.
- [x] Check public metadata dynamically, preserve response hashes/source dates, and record definition mismatches without silently substituting.
- [x] Run complete suite, a bounded live collection, and commit.

### Task 3: Run orchestration, reports, CLI and CI
**Files:** src/sovereign_macro/{pipeline,report,cli,__main__}.py; tests/test_pipeline.py; .github/workflows/{test,weekly}.yml; README.md; docs/{methodology,data-sources}.md.
**Interfaces:** run(output_dir, client, as_of, public_output) produces run result and six standard output files; CLI exposes collect/report options and an explicit network-free demo mode.
- [x] Write failing tests for all 27 rows, partial-rank gating, source-license redaction, complete current snapshots on provider failures, and last_success preservation.
- [x] Run tests and verify expected failures.
- [x] Implement staging/snapshot publication, manifest/quality, six outputs and a local HTML viewer; publish no raw responses.
- [x] Add pinned Actions: network-free test CI; Sunday 11:15 UTC collection; independent read/write jobs; diagnostic uploads; non-silent publication failures.
- [x] Document installation, local/public modes, known coverage, pending models, and extension contract.
- [x] Verify full suite, packaging, CLI, live DATA_HOLD outputs, snapshot consistency and no provider raw data tracked; commit.

### Final acceptance
- [x] Independent branch review, one fix pass for important findings, regression tests and full suite.
- [ ] Push reviewed code and plan to the requested repository, verifying remote content/commit.
- [ ] Report runnable features, tests and material coverage limits; do not claim complete 27-country data or Adjusted readiness.

## Verification log

- 2026-10-04 KST: 44 network-free tests pass. Same independent reviewer confirmed all six important findings resolved. Additional PDF footer edition regression passes.
- Initial live run: 13 yield sources parsed, seven Baseline routes eligible, Italy stale. Public snapshot redaction, 27-row preservation and manifest hashes verified. Some later calls returned 429/read timeout; those remain explicit DATA_HOLD errors.
- IMF Table A8 physical page 23 matched 27 country rows; all API overlaps passed rounding tolerance before filling SVK15 annual cells.
- Python wheel builds; installed wheel executes the demo outside the source checkout. Raw caches are ignored and excluded from publication.
- Scope remains initial implementation: unresolved country routes, Market Quality, redistribution rights and authentic April regression are not represented as completed.
