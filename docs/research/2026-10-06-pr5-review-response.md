# PR #5 external review response

All four findings were checked against the implementation and controlled fixtures. The final patch preserves source-specific diagnostics and does not enable scoring or change the installed preview.4 release.

| Finding | Verification and action |
| --- | --- |
| Annual total / excessive empty rows | Appending an explicit annual total reproduced `JSDA_MONTH_SCHEMA`. Exclude only `YYYY年度` / `YYYY計`; arbitrary malformed monthly labels still fail closed. The saved current workbook did not contain annual-total rows, so the review does not establish a current live-source failure. An inflated sheet dimension reproduced unbounded declared-row iteration risk. Reject missing/excessive dimensions before scanning (5,000 rows / 128 columns), iterate only four required columns, and preserve data beyond blank gaps. Do not silently truncate a worksheet after ten blank rows. |
| IMF transport reused for liquidity | An injected IMF-only adapter was incorrectly used for JSDA. Add `browser_transport` after the existing positional arguments, preserve the legacy IMF-only override, and route approved liquidity hosts through the general adapter. Treating the old argument as a general alias would preserve the defect; the proposed alias solution was therefore not copied. Default runtime browser-compatible transport remains available. |
| Size / global enable switch | `enabled` is the global switch, not a size-only switch; `enabled=false` must continue to disable all structural requests. Add independent `size_enabled=true` by default. With the global switch enabled, size can be disabled while liquidity is collected. The review's suggestion to default the entire module to enabled when the flag is absent was not adopted. |
| Synthetic size metadata retained | Mixed-input demo diagnostics retained real size URL/hash/time while liquidity discarded them. Synthetic size now discards the real source structure as liquidity already does; the original input bundle is not mutated. This is an input-injection consistency correction, not evidence that ordinary CLI demo fetched live data. |

Regression verification: the new tests reproduced each defect before implementation. All 181 tests passed after the fixes, including legacy IMF injection, independent general/IMF adapter routing, size-only disable, annual-total handling, malformed-month rejection, excessive declared dimensions, and demo metadata removal. The saved real JSDA workbook re-parsed to August 2026. This replay is not a new live download. Existing public/demo numerical redaction, source scopes and absence of Market Quality/Adjusted scores remain tested.

PR #5 remains open for review. No merge, new release or installed-skill update is part of this response.
