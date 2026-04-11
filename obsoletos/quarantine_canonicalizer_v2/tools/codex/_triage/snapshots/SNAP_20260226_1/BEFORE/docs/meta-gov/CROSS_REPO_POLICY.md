---
doc_id: META_GOV_CROSS_REPO_POLICY_L2
title: Cross-Repo Policy for Federation Meta-Governance
doc_type: governance
status: active
version: 1.0.0
owners:
  - federation-governance
last_updated: 2026-02-26
---

# CROSS_REPO_POLICY

## 1. Objective

Define deterministic cross-repository policy controls for Level 2 federation execution.
Policy is additive by default.
Policy is evidence-driven.

## 2. Coverage

This policy applies to:

- repo availability checks
- report ingestion
- docs-doctor probing
- blocker normalization
- debt aggregation
- federation status publication

This policy does not apply to:

- source-code changes in governed repos
- deployment pipelines
- production runtime behavior

## 3. Primary Sources

Per repository:

- `docs/govos/_reports/FINAL_REPORT.md`
- `tools/ops/Docs-Doctor.ps1` (if present)

Federation output root:

- `docs/meta-gov/`

## 4. Repo Reachability Policy

Repo path missing:

- mark as `OFFLINE`
- do not block federation by default
- include in summary counts

Repo path available:

- mark as online
- proceed with report/tooling checks

## 5. Tooling Availability Policy

If Docs-Doctor is missing:

- repo status becomes `MISSING_TOOLING`
- federation typically degrades
- tooling blocker is recorded

If Docs-Doctor exists and report is missing:

- run `Docs-Doctor --check` unless disabled by flag
- parse result deterministically

## 6. Report Availability Policy

Report present:

- parse and extract status, blockers, mandatory-read state

Report missing after check:

- tooling blocker remains
- repo degrades unless constitutional blockers discovered elsewhere

## 7. Mandatory Read Policy

For each online repo:

- detect `KERNEL_CONTEXT.md` state from FINAL_REPORT
- detect `FACTORY_RUNTIME_EXPLAINED.md` state from FINAL_REPORT
- persist parsed values in repo object

Mandatory read signals are informational inputs for federation risk interpretation.

## 8. Constitutional Blocker Policy

Constitutional blockers are detected by keywords:

- constitution
- constitutional

When found in online repo:

- repo may be `BLOCKED`
- federation becomes `BLOCKED`

## 9. Policy Blocker Policy

Policy blockers include markers:

- policy
- governance
- blocked lines not classified constitutional/tooling

Policy blockers degrade federation unless constitutional blockers exist.

## 10. Tooling Blocker Policy

Tooling blockers include:

- missing docs-doctor
- missing final report
- doctor invocation errors

Tooling blockers degrade federation by default.

## 11. Debt Extraction Policy

Scope is constrained:

- scan only `docs/govos/_reports/*.md`

Signals:

- `DEBT`
- `TODO`
- deterministic fallback: `RISK` or `BACKLOG`

No debt extraction from code trees.

## 12. Debt Identity Policy

Debt IDs are immutable per normalized text and repo:
`sha256(repo_name + normalized_line)`

Normalization:

- lowercase
- trim
- collapse whitespace

## 13. Excerpt Policy

Per-repo report excerpt uses fixed line count.
Line count is invariant between runs.
Excerpt order is top-to-bottom first lines.

## 14. Sorting Policy

All outputs must be stable-sorted:

- repos by name
- blockers lexicographically
- debt items by debt_id
- paths lexicographically

## 15. Hash Policy

Inputs hash:

- registry text
- observed repo status snapshot
- strict/doc-doctor mode switches

Outputs hash:

- federation status json text
- global debt json text
- meta report markdown text

## 16. Strict Mode Policy

Strict mode means:

- OFFLINE contributes degradation

Strict mode does not:

- auto-block federation
- force writes to offline repos

## 17. Open Policy

Open mode attempts UI convenience only.
If open action fails:

- outputs remain valid
- federation result unchanged

## 18. Write Policy

`--write` controls artifact persistence.
Without write:

- orchestration may evaluate state
- no filesystem side effects are required

Wrapper always calls with `--write` by default.

## 19. Path Safety Policy

All internal paths resolve from:

- explicit `--repo-root`
- or auto-detected repo root

No reliance on transient working directory.
No relative-only assumptions for critical writes.

## 20. External Repo Mutation Policy

Default policy forbids forced changes in external repos.
Level 2 reads and evaluates.
Any convergence action must be separately gated and explicitly enabled.

## 21. Feature Flag Policy

Default flags:

- convergence_actions: OFF
- forced_repo_changes: OFF

Policy requires explicit flag + governance approval to change defaults.

## 22. Recovery Policy

If federation is degraded:

1. resolve tooling/report issues
2. rerun orchestrator
3. verify status transitions deterministically

If federation is blocked:

1. resolve constitutional blockers first
2. rerun orchestrator
3. validate blockers section is empty

## 23. Anti-Regression Policy

Do not rename top-level JSON keys without migration version bump.
Do not remove blocker categories.
Do not remove determinism hash fields.
Do not randomize run artifact paths.

## 24. Governance Integration Policy

Meta policy integrates with per-repo GOVOS by consumption, not replacement.
Cross-repo merge of universe docs is explicitly forbidden.
Legacy ambiguity remains local and is not auto-rewritten by Level 2.

## 25. Observability Policy

Every run publishes:

- machine status json
- machine debt json
- human report md
- archived run copy

## 26. Run Archive Policy

Run artifacts are stored at:
`docs/meta-gov/_runs/<RUN_ID>/`

Latest pointer:
`docs/meta-gov/LATEST_RUN.txt`

Latest mirror:
`docs/meta-gov/LATEST/`

## 27. Compliance Checklist

- deterministic sorting
- deterministic hashing
- stable schema shape
- no product code edits
- no deletions
- no cross-universe merges
- no mass moves

## 28. Escalation Policy

Escalation levels:

1. tooling degraded
2. policy degraded
3. constitutional blocked

Higher levels supersede lower levels.

## 29. Audit Notes

Federation outputs are intended for machine + human traceability.
Use run archives for forensic comparison.
Do not use ad-hoc local notes as policy evidence.

## 30. Effective Date

This policy is effective for all Level 2 orchestration runs from the date of this file.
