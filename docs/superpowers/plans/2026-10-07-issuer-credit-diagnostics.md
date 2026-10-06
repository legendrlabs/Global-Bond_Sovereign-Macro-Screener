# Official Issuer Credit Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Collect dated S&P sovereign rating diagnostics from NZDM, Finanzagentur and AFT without inventing a credit score.

**Architecture:** A bounded HTML adapter validates exact source-specific table headers and a unique S&P row. NZDM's separate official long-term overview establishes rating term only when its local/foreign ratings and outlooks match the current ratings page. Optional collection is independent of size and liquidity; successful issuer rows take priority over WGB's unspecified reported ratings.

**Tech Stack:** Python 3.12, BeautifulSoup, existing HttpClient, unittest.

**Spec:** docs/research/2026-10-06-gemini-source-verification.md

## Global Constraints

- 27-country universe and Adjusted weights remain unchanged.
- Free, keyless official pages only; no credentials or authenticated APIs.
- Source-specific diagnostics only; `value=None`, `usable_for_scoring=false`.
- Current source date, classification evidence and retrieval time remain distinct.
- Ratings are not treated as expired merely because the last assessment is old; every run must refresh the current issuer page.
- Future assessment dates, schema drift, duplicate or missing S&P rows fail closed.
- Public and synthetic outputs omit rating/outlook/action values and basis copies.
- No raw issuer pages or provider-derived rating fixtures enter the repository.

## Review Focus

- Foreign-currency and local-currency grades differ: use the domestic column.
- Older issuer overview: its date must not replace the current row date.
- Basis verification fails: retain a reported domestic rating without claiming long-term verification.
- One country fails: other issuer rows and WGB fallback remain usable as reported diagnostics.
- Successful issuer row with an official yield: independent credit collection must still be displayed.

### Task 1: Parse exact issuer tables and dates

**Files:** Create `src/sovereign_macro/issuer_credit.py`; create `tests/test_issuer_credit.py`.

**Interfaces:** `parse_issuer_credit(iso, body, as_of, basis_body=None) -> dict`;
`collect_issuer_credit(client, settings, as_of) -> dict[iso, dict]`;
`redact_credit(row) -> None`.

- [x] Write parser tests for local/foreign distinction, current date over footer/overview, future dates, next-review dates, duplicate/missing agencies, headers, invalid rating/outlook and conflicting basis values.
- [x] Run `PYTHONPATH=src <existing-venv>/python -m unittest discover -s tests -p test_issuer_credit.py -q`; expect missing parser failures.
- [x] Implement bounded exact-header parsing, English/ISO dates and grade/outlook validation. NZDM verifies the official long-term overview; AFT term/currency and Germany currency remain unverified.
- [x] Add collector tests for per-country isolation, redirected source rejection, disabled collection and basis failure. Verify failures before implementation.
- [x] Implement collection with hashes, transport and retrieval metadata, no offline snapshot reuse, and conservative redaction.
- [x] Run the targeted suite and commit the parser/collector/tests.

### Task 2: Integrate diagnostics, source catalogue and reports

**Files:** Modify `market_inputs.py`, `pipeline.py`, `summary.py`, `http.py`, both `sources.yaml` files, `market_research.py`, `docs/data-sources.md`; extend `tests/test_issuer_credit.py`.

**Interfaces:** `bundle.market_inputs.credit[iso]` carries issuer diagnostics; an enabled global market-input switch and `credit_enabled` control collection independently of liquidity.

- [x] Write integration tests: independent switches, issuer priority over WGB, WGB survives issuer failure with failure disclosed, public/demo outputs and provenance omit ratings, reports show classification and assessment date.
- [x] Run targeted tests and verify integration failures.
- [x] Implement routing and rendering, with pending redistribution and no score creation. Add browser-compatible transport only for the three issuer hosts.
- [x] Run full `unittest discover -s tests -q`, then live issuer-only collection through production HttpClient; preserve successful/failed source metadata privately.
- [x] Commit all remaining changes, perform a whole-branch review and prepare a reviewable PR.

## Source ruling

AOFM's observed official XLSX URL is registered as a candidate, but direct download returns 502 or timeout in this runtime. Do not implement an AOFM numeric parser without the actual workbook. This is a bounded scope adjustment, not an approval pause.
