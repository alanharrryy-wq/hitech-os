# Factory Contract Changes

## 2026-03-11 - Gravity Report Centrality and Derived Planning Enrichment

### Added

- Formal centrality model in `GRAVITY_REPORT` schema:
  - typed per-node `centrality_metrics`
  - run-level `centrality_summary`
  - metric taxonomy including `BETWEENNESS_CENTRALITY`, `PAGERANK`, `EIGENVECTOR_CENTRALITY`, and related graph metrics
- New derived, schema-validated gravity sections:
  - `refactor_candidates`
  - `protected_node_recommendations`
  - `architecture_risk_flags`
- Vocabulary additions in `tools/codex/contracts/factory/vocabulary.json` for centrality and derived-output taxonomies.

### Updated

- Integrator gravity scaffold payload in `tools/codex/factory/contracts.py` now emits the new centrality and derived sections by default.
- Kernel/factory gravity law docs updated to encode these sections as additive compatibility-safe outputs.

### Contract Impact

- No breaking change to artifact file set.
- `GRAVITY_REPORT.json` gains additive formal structures that improve machine-driven refactor, protection, and architecture-risk planning.

## 2026-03-11 - Graph Subsystem Hardening and Normalization Follow-up

### Added

- Canonical enum normalization across graph-analysis schemas:
  - shared reason-code vocabulary
  - normalized risk-level ordering (`NONE`..`CRITICAL`)
  - normalized protection-level model with legacy aliases
- Semantic compatibility metadata required in all graph-analysis artifacts:
  - `schema_family`
  - `compatibility_mode`
  - `minimum_reader_version`
  - `breaking_change`
- Provenance and lineage normalization:
  - generator invocation/source-input structure
  - repository comparison provenance
  - snapshot lineage object
- Structured blocker/anomaly/dependency-basis models in canonical JSON.
- Structured dispatch decision rationale schema.
- Vocabulary hardening in `tools/codex/contracts/factory/vocabulary.json`.

### Updated

- Graph-analysis schema files tightened with strict identity and compatibility fields.
- Runtime scaffold payloads in `tools/codex/factory/contracts.py` updated to satisfy hardened schemas.
- Kernel and factory docs updated for semver governance, canonical JSON precedence, and compatibility rules.

### Contract Impact

- Canonical graph-analysis artifacts now require richer identity/provenance/compatibility metadata.
- Dispatch and impact artifacts now enforce typed rationale/blocker/dependency structures.
- Compatibility between canonical and legacy worker naming is explicit and schema-governed.

## 2026-03-11 - Graph Analysis and Impact-Aware Planning Formalization

### Added

- Law docs:
  - `docs/codex-kernel/docs/35_ARCHITECTURAL_GRAVITY.md`
  - `docs/factory/ARCHITECTURAL_GRAVITY_POLICY.md`
- New canonical schemas:
  - `tools/codex/schemas/gravity_report.schema.json`
  - `tools/codex/schemas/protected_nodes.schema.json`
  - `tools/codex/schemas/impact_cone_report.schema.json`
  - `tools/codex/schemas/dependency_diff.schema.json`
  - `tools/codex/schemas/dispatch_recommendations.schema.json`

### Updated

- Contract registry mapping in:
  - `tools/codex/contracts/factory/contracts_registry.json`
- Runtime schema index in:
  - `tools/codex/factory/schemas.py`
- Integrator required artifact set and schema validation wiring in:
  - `tools/codex/factory/contracts.py`
  - `tools/codex/factory/factory.config.json`
- Kernel law docs:
  - `docs/codex-kernel/docs/INDEX.md`
  - `docs/codex-kernel/docs/30_OUTPUT_CONTRACT.md`
  - `docs/codex-kernel/docs/50_INTEGRATION_RULES.md`
- Factory docs:
  - `docs/factory/INDEX.md`
  - `docs/factory/CONTRACT.md`
  - `docs/factory/ARCHITECTURE.md`
  - `docs/factory/CONTRACTS_REGISTRY.md`
  - `docs/factory/ADD_CONTRACTS.md`

### Contract Impact

- Z_aggregator now has mandatory graph-analysis artifacts as part of completion criteria.
- JSON graph-analysis artifacts are canonical and schema-validated.
- Protected-node mutation protocol is explicitly enforced as blockable policy.
- Compatibility between canonical planning IDs and legacy runtime IDs is explicit and documented.

## 2026-03-01 - Worker Closeout + Auto-Heal Rules

### Added

- new CLI command: `auto-closeout`
- worker bundle required artifact: `CODEX_OUTPUT.txt`
- preflight auto-repair flow for recoverable missing paths
- prompt contract injection for session hygiene + auto-report requirements
- Z ledger/watch visibility in run summary (`watch` payload includes ledger tail)
- new tests:
  - `test_auto_closeout.py`
  - `test_preflight_autorepair.py`

### Updated

- `bundle-validate` now runs worker auto-closeout by default.
- `run_iter.ps1` dispatches `Z_aggregator` prompt at run start, waits docs workers first, and runs `watch` + `auto-closeout` before integrate.
- worktree operations now auto-heal missing folders instead of immediate stop where recovery is possible.
- default visual baseline ownership set to `C_features`.

### Contract Impact

- worker contract now includes deterministic `CODEX_OUTPUT` closeout artifact.
- runtime config contract now includes auto-closeout/auto-repair/visual-baseline/Z-watch defaults.
- dispatcher prompt contract now enforces clean-session and auto-report headers.

## 2026-02-18 - Block A Hardening

### Added

- `oneshot` CLI command (`preflight -> launch -> bundle-validate -> integrate -> summary`)
- shared status evaluation module: `tools/codex/factory/status_eval.py`
- strict Z write guard module: `tools/codex/factory/fs_guard.py`
- append-only JSONL ledger event schema: `run_ledger_event.schema.json`
- integration and stress-lite test harness under `tools/codex/factory/tests/`
- CI workflow: `.github/workflows/factory.yml`
- docs:
  - `docs/factory/AUDIT.md`
  - `docs/factory/CONTRACT.md`
  - this file

### Updated

- CLI entrypoint reliability (`python -m tools.codex.factory.cli`)
- package init side-effect removal (`tools/codex/factory/__init__.py`)
- PASS/BLOCKED/FAIL semantics unified across CLI and integrator
- overlap/scope ordering determinism
- ledger format migrated to JSONL event stream
- worker/integrator status schemas expanded to include `FAIL`
- runbook updated for oneshot and audit flow

### Contract Impact

- Ledger storage contract changed from object-style ledger to append-only event JSONL.
- Status contract now explicitly allows and uses `FAIL`.
- Z no-write policy is now mandatory and enforced in integrator output writes.

## 2026-02-18 - Block B Industrialization

### Added

- package entrypoint `tools/codex/factory/__main__.py`
- factory version module `tools/codex/factory/version.py`
- runtime config loader `tools/codex/factory/config.py`
- path hardening guard `tools/codex/factory/path_guard.py`
- lock manager `tools/codex/factory/locks.py`
- deterministic attestation writer `tools/codex/factory/attestations.py`
- artifact normalization utility `tools/codex/factory/normalize_artifacts.py`
- doctor diagnostics `tools/codex/factory/doctor.py`
- docs:
  - `docs/factory/FORENSICS.md`
  - `docs/factory/SECURITY.md`

### Updated

- CLI now supports:
  - `python -m tools.codex.factory ...`
  - `doctor`
  - `ledger` filters
  - `ledger-replay`
  - `open-run`
  - `print-report`
  - `--version`
- Run IDs now include base-ref hash token.
- Worktrees now use fixed worker paths: `tools/codex/worktrees/<WORKER>`.
- Worktree creation now uses per-run/per-worker lock files.
- Overlap detection now reconciles `FILES_CHANGED` with `DIFF.patch` and reports hidden overlaps.
- Ledger events now include event metadata (`event_id`, parent links, durations, file counts) and signature updates.
- Integrator now writes attestation manifests and records ledger signature status in final report.
- CI now runs matrix (Windows primary, Linux best-effort), doctor, contract checks, determinism test, and uploads artifacts on failure.

### Contract Impact

- Run ID format changed to include base-ref hash.
- Runtime config contract introduced with strict schema validation.
- Ledger event contract expanded with metadata fields and signature verification.
- Lock file contract introduced for concurrency safety.
- Attestation artifacts added as required forensic evidence.

