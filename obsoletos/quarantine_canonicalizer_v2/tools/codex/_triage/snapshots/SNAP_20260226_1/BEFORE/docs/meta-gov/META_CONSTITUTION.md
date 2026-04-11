---
doc_id: META_GOV_CONSTITUTION_L2
title: HITECH Federation Meta-Constitution (Level 2)
doc_type: governance
status: active
version: 1.0.0
owners:
  - federation-governance
last_updated: 2026-02-26
---

# META_CONSTITUTION

## 1. Purpose

This constitution defines the Level 2 federation governance law for multi-repository operations.
The scope is transversal governance only.
No product runtime logic is governed by this document directly.

## 2. Level Model

Level 1 governs one repository.
Level 2 governs a federation of repositories.
Level 2 consumes Level 1 outputs.
Level 2 does not force Level 1 mutations by default.

## 3. Canonical Inputs

The canonical per-repo input is:
`docs/govos/_reports/FINAL_REPORT.md`

If a repo is online and this input is missing:
The orchestrator may run `Docs-Doctor --check`.
If tooling is missing, repo status becomes `MISSING_TOOLING`.

## 4. Canonical Outputs

Level 2 writes:

- `docs/meta-gov/FEDERATION_STATUS.json`
- `docs/meta-gov/GLOBAL_DEBT_LOG.json`
- `docs/meta-gov/META_REPORT.md`
- `docs/meta-gov/_runs/<RUN_ID>/...`
- `docs/meta-gov/LATEST_RUN.txt`
- `docs/meta-gov/LATEST/...`

## 5. Federation Law

Federation status follows strict deterministic rules:

1. If any ONLINE repo has constitutional blockers, federation is `BLOCKED`.
2. Else if strict mode is enabled and any repo is OFFLINE, federation is `DEGRADED`.
3. Else if any repo is `DEGRADED` or `MISSING_TOOLING`, federation is `DEGRADED`.
4. Else federation is `OK`.

OFFLINE repos do not block by default.

## 6. Determinism Mandates

Determinism is mandatory.
No randomness is allowed.
No non-deterministic sorting is allowed.
No time-dependent branch behavior is allowed except for run id timestamp.

Deterministic controls:

- Stable repo sort: by name ascending.
- Stable blocker sort: repo + category + message.
- Stable debt sort: debt_id ascending.
- Stable JSON key order: lexicographic.
- Stable excerpt length: fixed line count.
- Stable run artifact naming.

## 7. Feature Flags

All feature flags default to OFF.
Convergence actions are gated.
Forced repo changes are disabled by default.
No implicit writeback to external repos is allowed.

## 8. Non-Negotiables

- No silent pass.
- No hidden policy bypass.
- No product code edits from meta-governance.
- No mass moves.
- No cross-universe merges.
- No deletion during federation orchestration.
- No write outside approved meta-governance output roots.

## 9. Additive-Only Degradation Behavior

When mandatory reads are missing in a target repo:

- Federation collects evidence.
- Federation marks affected state as degraded or blocked per law.
- Federation avoids forced replacement docs.
- Federation remains additive on meta outputs.

## 10. Mandatory Read Contract

Before federation adjudication, each online repo should satisfy:

- `KERNEL_CONTEXT.md` present
- `docs/factory/FACTORY_RUNTIME_EXPLAINED.md` present

If the second file is a pointer stub:
Pointer resolution must be explicit.
The canonical target may be used as runtime authority.

## 11. Repo Status Contract

Per-repo status enum:

- `OK`
- `BLOCKED`
- `DEGRADED`
- `OFFLINE`
- `MISSING_TOOLING`

## 12. Blocker Taxonomy

Blockers are grouped into:

- constitutional
- policy
- tooling

Constitutional blockers always dominate federation state.
Tooling blockers degrade by default.

## 13. Debt Contract

Debt extraction is deterministic.
Signals are derived from report text lines containing:

- `DEBT`
- `TODO`

Fallback scan scope is restricted:
`docs/govos/_reports/**`

No source-code debt scanning is allowed in Level 2.

## 14. Debt ID Contract

Stable debt id format:
`sha256(repo_name + normalized_line)`

Normalization includes:

- trim
- lowercase
- whitespace collapse

## 15. Report Contract

`META_REPORT.md` must include:

- Run metadata
- Federation status and rationale
- Repo status table
- Blockers by category
- Debt totals
- Immediate next actions (max 10)
- Appendix with deterministic report excerpts

## 16. Summary Counts Contract

`FEDERATION_STATUS.json` includes summary counts:

- repos_total
- online_total
- offline_total
- ok_total
- degraded_total
- blocked_total
- missing_tooling_total

## 17. Determinism Hash Contract

`FEDERATION_STATUS.json` determinism block includes:

- inputs_hash
- outputs_hash
- stable_sort_rules

`inputs_hash` covers:

- registry content
- repo observed status snapshot
- mode flags

`outputs_hash` covers:

- status json text
- debt json text
- report markdown text

## 18. Strict Mode Contract

Strict mode changes only one rule:
OFFLINE repos degrade federation.

Strict mode never upgrades status.
Strict mode never bypasses blockers.

## 19. Open Mode Contract

`--open` attempts to open `docs/meta-gov/LATEST/`.
Open failure does not invalidate generated artifacts.
Open behavior must not alter deterministic output payloads.

## 20. Registry Contract

Registry is source of federation repo membership.
Default registry path:
`docs/meta-gov/REPO_REGISTRY.yaml`

Required repo fields:

- name
- path
- docs_doctor

## 21. Time Contract

Run id default format:
`RUN_YYYYMMDD_HHMMSS`

Timezone target:
`America/Mexico_City`

If timezone database is unavailable:
Use deterministic fixed offset fallback for run-id generation.
The timezone label remains canonical.

## 22. Security Contract

Meta tooling shall not execute arbitrary commands from registry content.
Only controlled checks are allowed.
Only Docs-Doctor `--check` is executed automatically.

## 23. Error Contract

CLI return codes:

- `0` -> federation `OK` or `DEGRADED`
- `2` -> federation `BLOCKED`
- `1` -> execution failure

## 24. Worker Model Contract

Level 2 run implementation follows 4 workers + 1 aggregator:

- A_core
- B_tooling
- C_features
- D_validation
- Z_aggregator

Each worker writes isolated bundles under:
`tools/codex/<worker>/<RUN_ID>/`

## 25. Aggregator Contract

Z_aggregator consolidates worker artifacts.
Z_aggregator writes the final plaintext report bundle.
Z_aggregator applies only agreed meta-governance file changes.
Z_aggregator does not mutate product runtime code.

## 26. Validation Contract

Mandatory validations:

- orchestrator `--write`
- orchestrator `--write --open`
- Docs-Doctor check where available
- deterministic Python test harness

## 27. Anti-Patterns

- Silent federation pass with missing reports.
- Unstable ordering between runs.
- Reading debt from code trees.
- Auto-converging unrelated repos.
- Forcing external repo writes by default.
- Treating OFFLINE as BLOCKED without strict mode.

## 28. Change Control

Any constitutional update must preserve backward-compatible status model keys unless version bump is explicit.
Any status model key removal requires migration guidance.
Any determinism rule change requires test update and explicit rationale.

## 29. Operational Guidance

Use explicit run artifacts for auditing.
Retain `_runs` history.
Use `LATEST` only as convenience mirror.
Treat `FEDERATION_STATUS.json` as machine contract.
Treat `META_REPORT.md` as human contract.

## 30. Final Clause

This constitution is effective immediately for Level 2 federation orchestration.
Conflicts with non-constitutional docs are resolved in favor of this file for Level 2 behavior only.
