# Factory Contract

## Scope

This contract defines:

- Run ID generation semantics
- Run artifact layout
- Worker and integrator status semantics
- Ledger event format
- Z-integrator write policy

## Run ID

Format:
`<kind>_<YYYYMMDD_HHMMSS>_<BASE_REF_HASH8>_<NNN>`

Rules:

- Timestamp uses UTC compact form.
- Base ref hash token is first 8 chars of sha256(rev-parse(base_ref) or base_ref fallback).
- Sequence (`NNN`) increments based on existing ledger run IDs for same prefix.
- Sequence always starts at `001`.

## Run Layout Contract

All writes for a run must remain under:
`tools/codex/runs/<RUN_ID>/`

Required paths:

- `tools/codex/runs/<RUN_ID>/RUN_MANIFEST.json`
- `tools/codex/runs/<RUN_ID>/A_worker/`
- `tools/codex/runs/<RUN_ID>/B_worker/`
- `tools/codex/runs/<RUN_ID>/C_worker/`
- `tools/codex/runs/<RUN_ID>/D_worker/`
- `tools/codex/runs/<RUN_ID>/Z_integrator/`

## Worker Bundle Contract

Required worker files:

- `STATUS.json`
- `SUMMARY.md`
- `FILES_CHANGED.json`
- `DIFF.patch`
- `SUGGESTIONS.md`
- `SCOPE_LOCK.json`
- `HANDOFF_NOTE.json`
- `LOGS/INDEX.json`

Worker status JSON:

- Schema: `worker_bundle_status.schema.json`
- Status values:
  - `PENDING`
  - `PASS`
  - `BLOCKED`
  - `WARN`
  - `FAIL`

## Integrator Bundle Contract

Required integrator files:

- `STATUS.json`
- `FINAL_REPORT.txt`
- `FILES_CHANGED.json`
- `DIFF.patch`
- `MERGE_PLAN.md`
- `LOGS/INDEX.json`

Integrator status JSON:

- Schema: `integrator_status.schema.json`
- Status values:
  - `PENDING`
  - `PASS`
  - `BLOCKED`
  - `WARN`
  - `FAIL`

## Status Evaluation Contract

Final status logic:

- `PASS`: all required checks have `rc == 0` and schema validations have zero errors.
- `BLOCKED`: any required check non-zero or any schema/policy/overlap/scope blocker.
- `FAIL`: internal error.

Exit codes:

- `PASS` -> `0`
- `BLOCKED` -> `2`
- `FAIL` -> `1`

## Ledger Contract

Ledger file:
`tools/codex/runs/factory_ledger.jsonl`

Ledger signature:
`tools/codex/runs/factory_ledger.sha256`

Format:

- Append-only
- Line-delimited JSON object per event

Required fields per line:

- `schema_version` (integer >= 1)
- `ts_utc` (string)
- `run_id` (string)
- `event_type` (string)
- `actor` (string)
- `event_id` (string)
- `parent_event_id` (string)
- `duration_ms` (integer >= 0)
- `file_counts` (object)
- `hashes` (object of hash values)
- `rc` (integer)
- `details` (object)

Schema:

- `run_ledger_event.schema.json`

Rendering order contract:

- Deterministic order by `ts_utc`, then `event_type`.

Replay contract:

- `python -m tools.codex.factory ledger-replay` reconstructs run status from ordered events.

## Z No-Write Policy Contract

Allowed root:
`tools/codex/runs/<RUN_ID>/`

Policy:

- Z-integrator write attempts outside allowed root must raise a policy error.
- Result must be non-pass (`BLOCKED` or `FAIL`).
- Human-readable policy message must be included in `FINAL_REPORT.txt`.

## Schema Registry Contract

Registry file:
`tools/codex/contracts/factory/contracts_registry.json`

Must include:

- Core factory schemas
- `run_ledger_event` schema reference

## Runtime Config Contract

Runtime config file (optional):
`tools/codex/factory/factory.config.json`

Precedence:

- defaults < config file < env (`FACTORY_*`) < CLI overrides

Schema:

- `factory_config.schema.json`

Required sections:

- `run`
- `paths`
- `workers`
- `security`
- `feature_flags`

## Locking Contract

Per-run lock:

- `tools/codex/runs/<RUN_ID>/locks/run.lock`

Per-worker lock:

- `tools/codex/runs/<RUN_ID>/locks/<WORKER>.lock`

Lock behavior:

- second acquisition attempt must BLOCK.

## Attestation Contract

Run attestations:

- `tools/codex/runs/<RUN_ID>/attestations/bundles.sha256`
- `tools/codex/runs/<RUN_ID>/attestations/ledger.sha256`
- `tools/codex/runs/<RUN_ID>/attestations/report.sha256`
