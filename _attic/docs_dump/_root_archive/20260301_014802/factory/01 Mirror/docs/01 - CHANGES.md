# Factory Contract Changes

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
