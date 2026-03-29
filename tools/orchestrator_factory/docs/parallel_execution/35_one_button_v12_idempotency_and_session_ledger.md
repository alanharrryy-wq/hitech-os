# One-Button v1.2 Idempotency and Session Ledger

## Document Status
- Status: Frozen
- Version: v1.2
- Scope: preventing duplicate session exports and enabling deterministic reuse

## 1. Why idempotency matters
A one-button launcher must avoid producing multiple indistinguishable sessions for the same intent and target state. Duplicate sessions are not harmless. They:
- waste operator time,
- create uncertainty about which zip to use,
- complicate ledger history,
- make validation and debugging noisy.

The solution is a combination of:
1. a stable idempotency key,
2. a project-scoped session ledger,
3. explicit reuse rules.

## 2. Ledger path
`F:\repos\hitech-os\tools\orchestrator_factory\ops\projects\<project_id>\state\sessions\session_ledger.jsonl`

The ledger is append-only in spirit. Each line is a standalone JSON object representing one resolved session.

## 3. Mandatory ledger fields
Each JSONL line must include, at minimum:
- `session_id`
- `created_at_utc`
- `session_mode`
- `policy`
- `project_id`
- `run_id`
- `round_id`
- `idempotency_key`
- `status`
- `session_zip_path`

Recommended additional fields:
- `session_zip_sha256`
- `handoff_copy_path`
- `lock_id`
- `launcher_version`
- `issues_count`

## 4. Idempotency key formula
The v1.2 key is:

```text
sha256(
  session_mode + policy + project_id + normalized_intent +
  target_run_id_or_none + target_round_id_or_none +
  project_manifest_sha256_or_none +
  run_manifest_sha256_or_none +
  round_manifest_sha256_or_none
)
```

## 5. Why context hashes are included
Intent alone is too weak. The same intent text may legitimately target a changed project state. By folding in manifest hashes, the key changes when the underlying project/run/round context changes materially.

This avoids false reuse when:
- manifests changed between runs,
- a new round was opened,
- a new run was created,
- a project was normalized or upgraded.

## 6. Sentinel rules
For sessions that do not yet have prior runtime manifests, the implementation must use stable sentinel values such as `"none"` rather than empty or omitted fields.

Examples:
- new project before run manifest exists -> `run_manifest_sha256_or_none = "none"`
- fresh round before round manifest exists -> `round_manifest_sha256_or_none = "none"`

This is required to avoid unstable keys caused by missing-field ambiguity.

## 7. Reuse semantics
### Completed equivalent session
If the ledger contains a completed session with the same key and a valid canonical zip:
- return `reused`,
- surface the existing zip path,
- do not regenerate the session.

### In-progress equivalent session
If the ledger or live lock indicates an equivalent session is currently in progress:
- do not race it,
- treat as blocked unless policy explicitly supports waiting or inspection,
- preferred exit code path: lock or in-progress conflict.

### Failed equivalent session
If a failed equivalent session exists:
- do not silently reuse it,
- require `--retry` for regeneration.

## 8. Policy-specific behavior
### resume_latest_round
- must never create a new run or round,
- reuse becomes the normal case when a completed equivalent session already exists.

### open_new_round
- the target logical round is new,
- reuse should only occur if a previous session already created that same new round for the same intent and same context hash combination.

### upgrade
- creates a new run lineage,
- reuse only makes sense within the same new run target context, not across prior runs.

## 9. Ledger write timing
The ledger should be written:
- after a session reaches a final state,
- after the canonical zip path is known for successful sessions,
- after `session_manifest.json` has been finalized.

Recommended final statuses:
- `ready_for_dispatch`
- `reused`
- `blocked`
- `failed`

## 10. Corruption handling
If the ledger is malformed:
- do not ignore it silently,
- surface an issue or blocker,
- use a conservative strategy that avoids incorrect reuse,
- prefer failure over unsafe duplicate mutation if integrity cannot be established.

## 11. Relationship to the manifest
The manifest explains the current session. The ledger explains the session history for the project. A good implementation keeps them aligned, but they serve different roles.

## 12. Example ledger entry
```json
{
  "session_id": "sess_20260327_001",
  "created_at_utc": "2026-03-27T18:22:10Z",
  "session_mode": "existing_project",
  "policy": "open_new_round",
  "project_id": "hitech-os",
  "run_id": "run_002",
  "round_id": "round_003",
  "idempotency_key": "sha256...",
  "status": "ready_for_dispatch",
  "session_zip_path": "F:\\repos\\hitech-os\\tools\\orchestrator_factory\\ops\\projects\\hitech-os\\bundles\\sessions\\sess_20260327_001.zip"
}
```

## 13. Practical success criteria
The idempotency subsystem is correct when:
- equivalent sessions are reused,
- failed sessions require explicit retry,
- missing prior manifests still produce stable keys,
- reuse decisions can be audited line-by-line through the ledger.
