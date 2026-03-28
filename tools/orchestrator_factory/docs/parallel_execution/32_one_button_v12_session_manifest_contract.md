# One-Button v1.2 Session Manifest Contract

## Document Status
- Status: Frozen
- Version: v1.2
- Primary artifact: `session/session_manifest.json`

## 1. Purpose
`session_manifest.json` is the canonical machine-readable summary of the session that produced a zip bundle. It is both:
- the primary record of what the launcher decided and did, and
- the handoff anchor for later conversational orchestration and diagnostics.

Every exported session zip **must** contain this file. If this file is missing, the session zip is invalid.

## 2. Design goals
The manifest must:
1. identify the session uniquely,
2. encode lane, policy, target project/run/round,
3. explain how idempotency and locking were resolved,
4. record readiness and validation outcomes,
5. expose output artifact paths and hashes,
6. surface issues without forcing a failed status when warnings are non-fatal.

## 3. Required top-level fields
The following top-level keys are mandatory in v1.2:

- `schema_version`
- `session_id`
- `launcher_version`
- `created_at_utc`
- `session_mode`
- `policy`
- `status`
- `project`
- `run`
- `round`
- `intent`
- `checks`
- `idempotency`
- `lock`
- `artifacts`
- `issues`

## 4. Normative shape
```json
{
  "schema_version": "1.0",
  "session_id": "sess_...",
  "launcher_version": "1.2.0",
  "created_at_utc": "2026-03-27T18:22:10Z",
  "session_mode": "existing_project",
  "policy": "open_new_round",
  "status": "ready_for_dispatch",
  "project": {
    "project_id": "hitech-os",
    "project_name": "HITECH OS",
    "initiative_type": "platform"
  },
  "run": {
    "run_id": "run_002",
    "action": "reuse_existing_run"
  },
  "round": {
    "round_id": "round_003",
    "parent_round_id": "round_002"
  },
  "intent": {
    "raw": "aterrizar launcher one-button",
    "normalized": "Aterrizar contrato e implementación del launcher one-button con zip canónico, lock e idempotencia."
  },
  "checks": {
    "contracts": "pass",
    "smoke": "pass",
    "readiness_stage_install": "ready",
    "readiness_stage_round": "ready"
  },
  "idempotency": {
    "key": "sha256...",
    "decision": "new_session",
    "context_hashes": {
      "project_manifest_sha256": "sha256...",
      "run_manifest_sha256": "sha256...",
      "round_manifest_sha256": "sha256..."
    }
  },
  "lock": {
    "lock_id": "lock_...",
    "lock_path": "F:\\repos\\hitech-os\\tools\\orchestrator_factory\\ops\\projects\\hitech-os\\state\\locks\\one_button.lock.json",
    "pid": 1234,
    "host": "DESKTOP-ABC"
  },
  "artifacts": {
    "session_zip_path": "F:\\repos\\hitech-os\\tools\\orchestrator_factory\\ops\\projects\\hitech-os\\bundles\\sessions\\sess_123.zip",
    "session_zip_sha256": "sha256...",
    "session_zip_size_bytes": 12345,
    "handoff_copy_path": "F:\\OneDrive\\Descargas\\sess_123.zip"
  },
  "issues": []
}
```

## 5. Field semantics
### schema_version
Schema version for the manifest file itself. This is independent from launcher versioning.

### session_id
Stable unique identifier for the emitted session bundle. Must be suitable for filesystem-safe naming and ledger indexing.

### launcher_version
Version string of the one-button launcher implementation that produced this manifest.

### created_at_utc
UTC timestamp when the session manifest was created. Must use ISO8601 with a trailing `Z`.

### session_mode
Allowed values:
- `existing_project`
- `new_project`

### policy
Allowed values:
- `resume_latest_round`
- `open_new_round`
- `upgrade`

### status
Recommended values in v1.2:
- `ready_for_dispatch`
- `blocked`
- `failed`
- `reused`

### project
Object describing the project scope:
- `project_id` required
- `project_name` required
- `initiative_type` required for `new_project`; may be inherited for `existing_project`

### run
Object describing the run scope:
- `run_id` required
- `action` required, examples:
  - `reuse_existing_run`
  - `create_new_run`
  - `reuse_latest_round_only`

### round
Object describing the round scope:
- `round_id` required
- `parent_round_id` required when the new round derives from a previous round; may be null or omitted only when a fresh round has no prior lineage

### intent
Object describing human intent:
- `raw` required
- `normalized` required for all modes; must be non-empty for `new_project`, `open_new_round`, and `upgrade`

### checks
Object capturing contract and readiness results:
- `contracts` required
- `smoke` required
- `readiness_stage_install` required
- `readiness_stage_round` required

Recommended allowed values:
- `contracts`: `pass|fail`
- `smoke`: `pass|fail`
- `readiness_stage_install`: `ready|not_ready|skipped`
- `readiness_stage_round`: `ready|not_ready|skipped`

### idempotency
Object describing the reuse decision:
- `key` required
- `decision` required
- `context_hashes` required

Allowed `decision` values:
- `new_session`
- `reuse_existing_session`
- `retry_requested`
- `blocked_by_in_progress_session`

### lock
Object describing the lock context:
- `lock_id` required
- `lock_path` required
- `pid` required
- `host` required

### artifacts
Object describing resulting outputs:
- `session_zip_path` required
- `session_zip_sha256` required for successful export
- `session_zip_size_bytes` required for successful export
- `handoff_copy_path` optional but recommended

### issues
Array of issue objects or strings. This key must always exist, even when empty.
Recommended issue object shape:
```json
{
  "severity": "warning",
  "code": "HANDOFF_COPY_FAILED",
  "message": "Configured handoff directory was unavailable; canonical zip export succeeded."
}
```

## 6. Required issue behavior
The manifest must list blockers and waivers when they are known. A session may still be `ready_for_dispatch` if issues are warnings rather than blockers. This preserves transparency without forcing false failure states.

Examples of non-fatal issues:
- handoff copy skipped,
- optional packet generation unavailable,
- stale-safe lock recovery executed.

Examples of fatal issues:
- readiness stage install failed,
- session zip contract validation failed,
- lock conflict with live process.

## 7. Relationship to sidecars
A sidecar manifest file may be emitted next to the canonical zip. If emitted, it should match the `session/session_manifest.json` content byte-for-byte where practical. The canonical contract, however, is the copy inside the zip.

## 8. Forward compatibility guidance
Future manifest versions may add keys, but v1.2 consumers should rely on the frozen keys above. Removing or renaming those keys is a contract break.

## 9. Validation expectations
The schema for `session_manifest.json` must enforce:
- required fields,
- string types,
- nested object shape,
- allowed enum values for known status and mode fields,
- presence of `issues[]` even when empty.

## 10. Human-readable mirrors
The zip also contains:
- `session_summary.md`
- `operator_instructions.md`
- `intake_normalized.md`

These are explanatory mirrors. The manifest remains the primary machine contract.
