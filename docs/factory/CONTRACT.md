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
- `tools/codex/runs/<RUN_ID>/_context/`
- `tools/codex/runs/<RUN_ID>/_apply/`
- `tools/codex/runs/<RUN_ID>/_queue/rework/inbox/`
- `tools/codex/runs/<RUN_ID>/_queue/rework/outbox/`
- `tools/codex/runs/<RUN_ID>/A_worker/`
- `tools/codex/runs/<RUN_ID>/B_worker/`
- `tools/codex/runs/<RUN_ID>/C_worker/`
- `tools/codex/runs/<RUN_ID>/D_worker/`
- `tools/codex/runs/<RUN_ID>/Z_integrator/`

## Worker Bundle Contract

Required worker files:

- `FILES/` (when full-file snapshots are needed)
- `STATUS.json`
- `SUMMARY.md`
- `FILES_CHANGED.json`
- `DIFF.patch`
- `SUGGESTIONS.md`
- `SCOPE_LOCK.json`
- `HANDOFF_NOTE.json`
- `LOGS/INDEX.json`
- `CODEX_OUTPUT.txt`

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
- `FILES_CHANGED_MERGED.json` (compatibility alias)
- `DIFF_MERGED.patch` (compatibility alias)
- `MERGE_PLAN.md`
- `APPLY_INSTRUCTIONS.md`
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

## Preflight And Auto-Repair Contract

- Preflight must execute before launch/oneshot stages.
- Preflight runs in auto-repair mode by default.
- Missing recoverable folders/files must be auto-healed before returning `BLOCKED`.
- Human intervention is only valid for unrecoverable failures (for example: missing `git` executable).

## Worker Auto-Closeout Contract

- `bundle-validate` runs worker auto-closeout by default.
- Auto-closeout must generate/repair all required worker artifacts.
- Auto-closeout must write `CODEX_OUTPUT.txt` in worker bundle and mirror `CODEX_OUTPUT_<WORKER>_<RUN_ID>.txt` in worker worktree when available.

## Session Hygiene Contract

- Prompt materialization must inject clean-session headers.
- Worker prompt must include:
  - `SESSION_POLICY: CLEAN_START_REQUIRED`
  - `AUTO_REPORT_REQUIRED: true`
  - `MANDATORY_READS: KERNEL_CONTEXT.md,docs/factory/FACTORY_RUNTIME_EXPLAINED.md,MODULE_BOUNDARIES.md,ARCHITECTURE_DECISIONS.md`
  - `EXECUTION_GOVERNANCE_PATH: tools/codex/dispatch/execution_rules.json`
  - `SELF_CHECK_REQUIRED: ORPHAN_MODULES,UNUSED_EXPORTS,FILES_CREATED,REAL_CODE_LOC,ARTIFACT_LOC`
- If prior chat context exists, worker must ignore stale context and continue with current run scope.

## Manual Prompt Distribution Integrity Contract

- Command: `python tools/codex/dispatch/validator.py prepare-manual-run --pack-path <PROMPTS_PACK_PATH> [--run-id <RUN_ID>]`.
- Required materialization evidence under `tools/codex/prompts/<RUN_ID>/`:
  - `PROMPTS_PACK_SOURCE.txt`
  - `PROMPTS_PACK_RESOLVED.txt`
  - `PROMPT_MATERIALIZATION.json`
  - `MANUAL_DISTRIBUTION_CHECKLIST.md`
- `PROMPT_MATERIALIZATION.json` must include source-pack checksum and per-worker prompt checksums.
- Manual closeout must run, in order:
  1. `wait-done`
  2. `execution-audit`
  3. `validate-guardrails`

## Visual Baseline Ownership Contract

- Default visual baseline owner is `B_worker`.
- Baseline updates remain explicit/manual command (`--update-baseline`) but ownership is assigned to `B_worker` by default.

## Integrator Watch Contract

- Z prompt is dispatched at run start.
- Z must monitor progress using:
  - `python -m tools.codex.factory watch --run-id <RUN_ID>`
  - `python -m tools.codex.factory ledger --run-id <RUN_ID> --raw-events --limit N`
- Z integration/report work starts after worker completion checks pass.

## Rework File-Queue Contract

Rework transport is file-queue based (not UI automation):

- Inbox root: `tools/codex/runs/<RUN_ID>/_queue/rework/inbox/`
- Outbox root: `tools/codex/runs/<RUN_ID>/_queue/rework/outbox/`
- Dead-letter root: `tools/codex/runs/<RUN_ID>/_queue/rework/deadletter/`
- Queue state index: `tools/codex/runs/<RUN_ID>/_queue/rework/state/index.json`

Rules:

1. `validator.py rework-cycle` writes queue request payloads to inbox.
2. Worker acknowledges completion by writing `*.done.json` into outbox.
3. Dispatcher waits on outbox ack before `DONE.marker` validation for rework cycles.
4. Queue message IDs must be deterministic and idempotent for repeated cycles.

## Anti-Hallucination + Metrics Governance Contract

Machine policy:

- `tools/codex/dispatch/execution_rules.json`

Enforcement command:

- `python tools/codex/dispatch/validator.py execution-audit --run-id <RUN_ID> --workers A_core,B_tooling,C_features,D_validation,Z_aggregator`

Required artifacts:

- Per worker: `tools/codex/runs/<RUN_ID>/<WORKER>/EXECUTION_RULES_REPORT.json`
- Run summary: `tools/codex/runs/<RUN_ID>/_debug/EXECUTION_RULES_SUMMARY.json`

Hard checks include:

- disallowed top-level architecture additions
- forbidden generic utility files
- low product-impact change sets
- real-code/artifact LOC ratio thresholds
- hard file size cap
- max new files per run

Warnings include:

- recommended file-size band
- test LOC ratio guidance
- change density guidance
- orphan-module risk when strict mode is disabled

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

## Memory Layer Contract

Persistent memory root:

- `tools/codex/memory/`

Required files:

- `RUN_HISTORY.json`
- `TECH_DEBT.json`
- `FAIL_PATTERNS.json`
- `SUCCESS_PATTERNS.json`
