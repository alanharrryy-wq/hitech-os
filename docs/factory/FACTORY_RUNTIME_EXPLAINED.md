## 1. PURPOSE OF THIS DOCUMENT
- This document is the canonical operational explanation of the Multi-Codex Factory runtime model in HITECH-OS.
- This document is not:
  - A change proposal.
  - A feature roadmap.
  - An implementation patch guide.
- This document should be read by:
  - Engineers authoring worker bundles.
  - Operators running factory commands.
  - Reviewers auditing deterministic evidence.

## 2. CANONICAL SOURCES OF TRUTH
- Ordered source list:
  1. `docs/CONTRACT.md`
  2. `docs/factory/CONTRACT.md`
  3. `docs/factory/CHANGES.md`
  4. `docs/factory/ARCHITECTURE.md`
  5. `docs/factory/COMMUNICATION_PROTOCOL.md`
  6. `docs/factory/CONTRACTS_REGISTRY.md`
  7. `docs/factory/DETERMINISM_POLICY.md`
  8. `docs/factory/RUNBOOK.md`
  9. `docs/factory/ROLE_HARDENING.md`
  10. `docs/factory/SECURITY.md`
  11. `docs/factory/AUDIT.md`
  12. `docs/factory/FORENSICS.md`
  13. `docs/factory/WORKTREE_OPERATIONS.md`
  14. `KERNEL_CONTEXT.md`
- Explicit precedence rules:
  - `docs/CONTRACT.md` defines repository-wide enforcement priority and states that contract-level constraints override conflicting local workflow.
  - `docs/factory/CONTRACT.md` defines factory contracts (run ID, layout, status semantics, ledger, locking, write policy).
  - `docs/factory/CHANGES.md` records contract-impacting deltas for Block A and Block B.
  - If precedence among non-contract factory docs is not explicitly stated, precedence is `UNDEFINED`.
- Statement: "If it’s not in these sources, it does not exist."

## 3. FACTORY MODEL OVERVIEW
- What the Multi-Codex Factory is:
  - A deterministic, contract-driven pipeline with five roles: `A_worker`, `B_worker`, `C_worker`, `D_worker`, and `Z_integrator`.
  - A bundle-based workflow where workers emit required artifacts and Z integrates, validates, and reports.
  - An auditable execution model with append-only ledger events and run attestations.
- Why it exists:
  - To produce explicit `PASS`/`BLOCKED`/`FAIL` outcomes.
  - To preserve deterministic outputs and reproducible audits.
  - To enforce scope, overlap, and write-policy constraints.
- High-level mental model:
  - `A/B/C/D` create scoped bundles.
  - `Z` consumes bundles, runs required checks, and writes final integration artifacts.
  - Ledger and attestation files provide replayable forensic evidence.

## 4. WORKERS AND ROLES
- `A_core` (mapped to `A_worker`)
  - Responsibilities:
    - Produce required worker bundle artifacts.
    - Stay within declared scope lock.
    - Perform primary domain changes.
  - Explicit non-responsibilities:
    - Integrator-level merge/report ownership.
    - Writing to other worker bundles.
  - Allowed outputs:
    - `DIFF.patch`
    - `FILES_CHANGED.json`
    - `HANDOFF_NOTE.json`
    - `LOGS/INDEX.json`
    - `SCOPE_LOCK.json`
    - `STATUS.json`
    - `SUMMARY.md`
    - `SUGGESTIONS.md`
  - Forbidden behavior:
    - Crossing scope lock boundaries.
    - Omitting required artifacts.
    - Writing to another worker bundle.
- `B_tooling` (mapped to `B_worker`)
  - Responsibilities:
    - Produce required worker bundle artifacts.
    - Perform secondary surface and UX changes.
    - Stay within declared scope lock.
  - Explicit non-responsibilities:
    - Integrator-level merge/report ownership.
    - Writing to other worker bundles.
  - Allowed outputs:
    - `DIFF.patch`
    - `FILES_CHANGED.json`
    - `HANDOFF_NOTE.json`
    - `LOGS/INDEX.json`
    - `SCOPE_LOCK.json`
    - `STATUS.json`
    - `SUMMARY.md`
    - `SUGGESTIONS.md`
  - Forbidden behavior:
    - Crossing scope lock boundaries.
    - Omitting required artifacts.
    - Writing to another worker bundle.
- `C_features` (mapped to `C_worker`)
  - Responsibilities:
    - Perform tooling and infrastructure changes.
    - Produce required worker bundle artifacts.
    - Stay within declared scope lock.
  - Explicit non-responsibilities:
    - Integrator-level merge/report ownership.
    - Writing to other worker bundles.
  - Allowed outputs:
    - `DIFF.patch`
    - `FILES_CHANGED.json`
    - `HANDOFF_NOTE.json`
    - `LOGS/INDEX.json`
    - `SCOPE_LOCK.json`
    - `STATUS.json`
    - `SUMMARY.md`
    - `SUGGESTIONS.md`
  - Forbidden behavior:
    - Crossing scope lock boundaries.
    - Omitting required artifacts.
    - Writing to another worker bundle.
- `D_validation` (mapped to `D_worker`)
  - Responsibilities:
    - Perform validation and hardening changes.
    - Produce required worker bundle artifacts.
    - Stay within declared scope lock.
  - Explicit non-responsibilities:
    - Integrator-level merge/report ownership.
    - Writing to other worker bundles.
  - Allowed outputs:
    - `DIFF.patch`
    - `FILES_CHANGED.json`
    - `HANDOFF_NOTE.json`
    - `LOGS/INDEX.json`
    - `SCOPE_LOCK.json`
    - `STATUS.json`
    - `SUMMARY.md`
    - `SUGGESTIONS.md`
  - Forbidden behavior:
    - Crossing scope lock boundaries.
    - Omitting required artifacts.
    - Writing to another worker bundle.
- `Z_aggregator` (mapped to `Z_integrator`)
  - Responsibilities:
    - Block runs on conflict or missing required artifacts.
    - Merge worker outputs.
    - Validate schemas, overlap, scope, and policy constraints.
    - Write integrator artifacts and final report.
  - Explicit non-responsibilities:
    - Product logic generation.
    - Worker feature invention.
  - Allowed outputs:
    - `DIFF.patch`
    - `FILES_CHANGED.json`
    - `FINAL_REPORT.txt`
    - `LOGS/INDEX.json`
    - `MERGE_PLAN.md`
    - `STATUS.json`
  - Forbidden behavior:
    - Any write outside `tools/codex/runs/<RUN_ID>/`.
    - Feature invention.
    - Skipping required artifact checks.

## 5. EXECUTION MODEL
- Preflight:
  - Validates environment and required paths before launch.
  - Produces a status outcome (`PASS` or `BLOCKED`).
- Worktree creation:
  - Uses branch naming `codex/factory/<RUN_ID>/<WORKER_ID>`.
  - Uses per-run and per-worker locks for concurrency safety.
- Parallel execution (`A/B/C/D`):
  - Worker responsibilities are isolated by design.
  - Worker scheduling mechanism is `UNDEFINED` in docs; independent bundle production is defined.
- Artifact production:
  - Each worker emits the required artifact set.
  - Paths are repo-relative and expected to be deterministically ordered.
- Aggregation phase (`Z`):
  - Validates bundle schemas.
  - Detects overlap, hidden overlap, and scope violations.
  - Enforces Z no-write policy.
  - Writes integrator artifacts and report.
- Final validation:
  - Status logic is applied to required checks, schema errors, and blockers.
  - `FINAL_REPORT.txt`, `STATUS.json`, and CLI exit code must align.
- Summary/reporting:
  - `oneshot` stage order is fixed:
    1. `preflight`
    2. `launch`
    3. `bundle-validate`
    4. `integrate`
    5. summary emission
  - `oneshot` exits non-zero on blocked/failed required stage.
- Ordering guarantees:
  - Ledger rendering order is deterministic by `ts_utc`, then `event_type`.
  - Required stage order for `oneshot` is deterministic.
- What is NOT sequentially safe:
  - Concurrent reuse of the same `RUN_ID` (blocked by lock contract).
  - Integration when required worker artifacts are missing.
  - Proceeding with unresolved overlap/scope/policy blockers.

## 6. ISOLATION & SCOPE ENFORCEMENT
- Worktree layout:
  - `tools/codex/worktrees/<RUN_ID>/<WORKER>`
- Run artifact directories:
  - `tools/codex/runs/<RUN_ID>/A_worker/`
  - `tools/codex/runs/<RUN_ID>/B_worker/`
  - `tools/codex/runs/<RUN_ID>/C_worker/`
  - `tools/codex/runs/<RUN_ID>/D_worker/`
  - `tools/codex/runs/<RUN_ID>/Z_integrator/`
  - `tools/codex/runs/<RUN_ID>/locks/`
  - `tools/codex/runs/<RUN_ID>/attestations/`
- Scope locking rules:
  - Workers must stay inside declared scope lock.
  - Workers must not write to other worker bundles.
  - Scope violations are blocking conditions.
- Path protection rules:
  - Absolute paths are rejected.
  - Drive-path tricks are rejected.
  - Traversal (`..`) is rejected.
  - UNC path tricks are rejected.
  - `.env` and `.git` are protected by default.
  - Symlink/junction escape checks are best-effort and block on detection.
- Collision detection:
  - Overlap detection reconciles `FILES_CHANGED.json` and `DIFF.patch`.
  - Hidden overlaps (patch paths missing from `FILES_CHANGED.json`) are treated as blockers.
- Overlap handling:
  - Conflicts block integration unless explicitly resolved via scope/ownership correction.
  - Deterministic ordering is expected for conflict listings.

## 7. ARTIFACT CONTRACT
- Required artifacts per worker:
  - `DIFF.patch`
  - `FILES_CHANGED.json`
  - `HANDOFF_NOTE.json`
  - `LOGS/INDEX.json`
  - `SCOPE_LOCK.json`
  - `STATUS.json`
  - `SUMMARY.md`
  - `SUGGESTIONS.md`
- Required artifacts for Z:
  - `DIFF.patch`
  - `FILES_CHANGED.json`
  - `FINAL_REPORT.txt`
  - `LOGS/INDEX.json`
  - `MERGE_PLAN.md`
  - `STATUS.json`
- Meaning of `STATUS.json` fields:
  - `status`: documented status enum includes `PENDING`, `PASS`, `BLOCKED`, `WARN`, `FAIL`.
  - `required_checks`: required gate results; `PASS` requires required checks with `rc == 0`.
  - `optional_checks`: non-required checks; blocking effect is `UNDEFINED` unless promoted by policy.
  - `errors`: blocking/internal issues recorded by role.
  - `warnings`: non-blocking issues recorded by role.
  - `run_id`: run identity linkage.
  - `started_at` / `ended_at`: string timestamps; precision/format constraints beyond schema are `UNDEFINED` in docs.
  - `worker_id`: role identity (`A_worker`, `B_worker`, `C_worker`, `D_worker`, `Z_integrator`).
- Sorting and determinism rules:
  - Deterministic file ordering is required.
  - JSON key ordering must be stable.
  - Paths in changed-file reporting are repo-relative.
  - SHA256 is required per changed-file entry.
- Attestation and hashing expectations:
  - Run attestations required:
    - `attestations/bundles.sha256`
    - `attestations/ledger.sha256`
    - `attestations/report.sha256`
  - Ledger signature required:
    - `tools/codex/runs/factory_ledger.sha256`
  - Attestation entries are deterministically sorted by relative path.

## 8. STATUS SEMANTICS
- `PASS`:
  - All required checks have `rc == 0`.
  - Schema validations have zero errors.
- `BLOCKED`:
  - Any required check is non-zero.
  - Any policy/scope/overlap/schema blocker exists.
- `FAIL`:
  - Internal execution error.
- `WARN` (if applicable):
  - Defined in status enums for worker/integrator status/check records.
  - Run-level final-status semantics for `WARN` are `UNDEFINED` in factory contract logic.
- Exit code meaning:
  - `PASS` -> `0`
  - `BLOCKED` -> `2`
  - `FAIL` -> `1`
- What stops a run immediately:
  - `oneshot` exits non-zero on blocked/failed required stage.
  - Stage-by-stage short-circuit behavior beyond that statement is `UNDEFINED` in docs.

## 9. DETERMINISM POLICY
- JSON ordering rules:
  - Stable JSON key ordering is required.
- File ordering rules:
  - Stable sorted file lists are required.
  - Conflict and ledger rendering order is deterministic where documented.
- Time handling rules:
  - UTC timestamps only.
  - Run ID timestamp token uses compact UTC format.
- Ledger behavior:
  - Append-only JSONL ledger.
  - Required event fields per contract.
  - Deterministic rendering/query order by `ts_utc`, then `event_type`.
  - Replay support is part of contract.
- What is explicitly forbidden:
  - Embedding machine-specific absolute paths in generated artifacts.
  - Including transient metadata (for committed outputs) such as PID/memory/env snapshots.
  - Writing unordered maps directly to disk.
  - Enabling feature flags by default.

## 10. NO-GO ZONES
- Actions workers must never do:
  - Omit required bundle artifacts.
  - Write into another worker bundle.
  - Write outside declared scope lock.
- Actions Z must never do:
  - Invent product features.
  - Skip required artifact enforcement.
  - Write outside `tools/codex/runs/<RUN_ID>/`.
- Paths that are always protected:
  - `.env`
  - `.env.*`
  - `.git/**`
  - `.github/workflows/**`
- Anti-patterns explicitly rejected:
  - Merging without worker `FILES_CHANGED.json`.
  - Relying on manual run tracking.
  - Skipping schema validation.
  - Turning feature flags on by default.

## 11. WHAT A “CORRECT RUN” LOOKS LIKE
- Preconditions:
  - Contract files and required paths exist.
  - Preflight passes required checks.
  - Run ID and run directory are established under `tools/codex/runs/<RUN_ID>/`.
- During execution:
  - Stage order follows documented `oneshot` sequence.
  - Each worker emits required artifacts.
  - Scope/overlap/path/policy checks are applied before final pass.
- After completion:
  - Z required artifacts exist and agree on outcome.
  - Ledger events exist and are parseable.
  - Ledger signature file exists.
  - Attestation files exist for bundles/report/ledger.
- Evidence that must exist:
  - `RUN_MANIFEST.json`
  - `A_worker/*`
  - `B_worker/*`
  - `C_worker/*`
  - `D_worker/*`
  - `Z_integrator/DIFF.patch`
  - `Z_integrator/FILES_CHANGED.json`
  - `Z_integrator/FINAL_REPORT.txt`
  - `Z_integrator/LOGS/INDEX.json`
  - `Z_integrator/MERGE_PLAN.md`
  - `Z_integrator/STATUS.json`
  - `attestations/bundles.sha256`
  - `attestations/ledger.sha256`
  - `attestations/report.sha256`
  - `tools/codex/runs/factory_ledger.jsonl`
  - `tools/codex/runs/factory_ledger.sha256`

## 12. CURRENT KNOWN GAPS OR OPEN QUESTIONS
- Missing docs:
  - Root-level `CHANGES.md` is missing.
  - Root-level `CONTRACT.md` is missing.
  - Root-level `NEXT.md` is missing.
  - Root-level `STATE.md` is missing.
- Undefined behavior:
  - Exact precedence between `python -m tools.codex.factory ...` and `python tools/codex/factory_cli.py ...` command forms across all docs is `UNDEFINED`.
  - Exact scheduler model for A/B/C/D (operator-managed vs orchestrator-managed parallelism) is `UNDEFINED`.
  - Final-status semantics for `WARN`/`PENDING` beyond enum presence are `UNDEFINED`.
  - Whether optional checks can become blockers without becoming required checks is `UNDEFINED`.
- TODOs/backlog explicitly documented:
  - Add full CI under `.github/workflows` when online package install policy is defined.
  - Extend shared TS/ESLint presets in `packages/tooling`.
  - Wire future demo orchestration UI in `apps/demo-engine`.
