# Shared Bridge Contract

## 1. What Shared Is / Is Not
- Shared bridge is an optional ingest/publish layer between canonical factory runs and a shared mount.
- Shared bridge is not a replacement for canonical runtime paths.
- Canonical paths remain:
  - `tools/codex/worktrees/<RUN_ID>/<WORKER>`
  - `tools/codex/runs/<RUN_ID>/...`
- Bridge features are OFF by default.

## 2. Feature Flags
- `HITECH_SHARED_MODE=off|consume|publish|both` (default: `off`)
- `HITECH_SHARED_ROOT=<path>` (optional fallback root)
- `HITECH_SHARED_REQUIRE_CURRENT=0|1` (default: `0`)
- `HITECH_SHARED_STRICT_SCHEMA=0|1` (default: `0`)
- `HITECH_SHARED_HASH_STRATEGY=none|sha256` (default: `sha256`)
- `HITECH_SHARED_DRYRUN=0|1` (default: `0`)

## 3. Resolution Rules
### 3.1 `resolve_shared_root(repo_root)`
1. Prefer `<repo_root>/tools/codex/shared` when it exists (dir or junction).
2. Else use `HITECH_SHARED_ROOT`.
3. Else disable bridge (`None`).

### 3.2 `resolve_shared_current_run_root(shared_root, flags)`
- Prefer `shared_root/CURRENT`.
- Fallback: treat `shared_root` as current run root when run markers exist (`META`, `WORKERS`, `HEALTH`).
- If `HITECH_SHARED_REQUIRE_CURRENT=1` and neither layout is valid: fail clearly.

## 4. CURRENT Behavior
- `MODE=consume`:
  - reads shared incoming payloads.
  - writes only to `tools/codex/runs/<RUN_ID>/incoming_shared/`.
- `MODE=publish`:
  - reads canonical run outputs under `tools/codex/runs/<RUN_ID>/`.
  - writes shared outputs under `WORKERS/*` and `AGGREGATE/*`.
- `MODE=both`:
  - runs consume pre-hook and publish post-hook.
- `MODE=off`:
  - no bridge writes, no bridge side effects.

## 5. Shared Layout (Minimal Contract)
```text
<shared_current_run_root>/
  META/
    FACTORY_POINTER.json
  LEDGER/
    BRIDGE_EVENTS.ndjson
  INCOMING/
    FACTORY/
      <RUN_ID>/
        incoming_shared/...
  WORKERS/
    A_worker/...
    B_worker/...
    C_worker/...
    D_worker/...
    Z_integrator/...
  AGGREGATE/
    RUN_MANIFEST.json
    FINAL_REPORT.txt
    attestations/
      bundles.sha256
      ledger.sha256
      report.sha256
  HEALTH/
    publish_manifest.json
```

Compatibility notes:
- Worker alias fallback is supported when legacy directories already exist:
  - `A_core`, `B_tooling`, `C_features`, `D_validation`, `Z_aggregator`
- Shared section names may be uppercase or lowercase (`WORKERS`/`workers`, `AGGREGATE`/`aggregate`).
- Legacy mirrors are optionally written when present (`meta`, `artifacts/human`, `artifacts/machine`).

## 6. Pointer Files
### 6.1 `META/FACTORY_POINTER.json`
```json
{
  "schema_version": 1,
  "run_id": "<RUN_ID>",
  "factory_run_root": "tools/codex/runs/<RUN_ID>",
  "factory_worktrees_root": "tools/codex/worktrees/<RUN_ID>",
  "shared_current_run_root": "<path>",
  "mode": "off|consume|publish|both",
  "dry_run": false
}
```

### 6.2 `tools/codex/runs/<RUN_ID>/SHARED_POINTER.json`
```json
{
  "schema_version": 1,
  "run_id": "<RUN_ID>",
  "factory_run_root": "tools/codex/runs/<RUN_ID>",
  "shared_root": "<path>",
  "shared_current_run_root": "<path>",
  "mode": "off|consume|publish|both",
  "dry_run": false
}
```

## 7. Deterministic Bridge Ledger (NDJSON)
- Path: `<shared_current_run_root>/LEDGER/BRIDGE_EVENTS.ndjson`
- Append-only; one JSON object per line.
- Serialization:
  - `json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=False)`

Event skeleton:
```json
{
  "actor": "shared_bridge",
  "event_type": "CONSUME|PUBLISH|LOCK_SKIP|ERROR",
  "run_id": "<RUN_ID>",
  "mode": "off|consume|publish|both",
  "rc": 0,
  "details": {
    "copied": [],
    "unchanged": [],
    "skipped": []
  }
}
```

## 8. Publish Overwrite Policy
- Publish is append-only by default.
- Never delete files from shared.
- Overwrite existing shared file only when:
  - content differs, and
  - target is not immutable (name/extension/manifest marker).
- Deterministic publish manifest categories are required:
  - `copied`
  - `unchanged`
  - `skipped`

## 9. Lock Detection & Respect
- Detect lock files under:
  - `tools/codex/runs/<RUN_ID>/`
  - resolved shared current run root
- If lock is present:
  - do not publish/overwrite outputs,
  - do not write canonical factory outputs,
  - append `LOCK_SKIP` bridge ledger event,
  - exit gracefully unless strict mode requires blocking.

## 10. Determinism Rules
- Sort path lists lexicographically before persistence.
- Sort JSON keys on serialization.
- Avoid nondeterministic fields in bridge artifacts.
- `RUN_ID` may include time token by contract; artifact ordering/content remains deterministic for equal inputs inside the same run.

## 11. Minimal Embedded Schema Block
```json
{
  "$id": "shared_bridge.min.schema.v1",
  "type": "object",
  "required": [
    "mode",
    "run_id",
    "copied",
    "unchanged",
    "skipped"
  ],
  "properties": {
    "mode": {
      "enum": ["off", "consume", "publish", "both"]
    },
    "run_id": {
      "type": "string",
      "minLength": 1
    },
    "copied": {
      "type": "array",
      "items": {"type": "string"}
    },
    "unchanged": {
      "type": "array",
      "items": {"type": "string"}
    },
    "skipped": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["path", "reason"],
        "properties": {
          "path": {"type": "string"},
          "reason": {"type": "string"}
        }
      }
    }
  }
}
```

## 12. Examples
Consume only:
```powershell
$env:HITECH_SHARED_MODE = "consume"
python -m tools.codex.factory operator bootstrap --base-ref HEAD
```

Publish only:
```powershell
$env:HITECH_SHARED_MODE = "publish"
python -m tools.codex.factory operator watch --run-id <RUN_ID> --base-ref HEAD
```

Consume + publish:
```powershell
$env:HITECH_SHARED_MODE = "both"
python -m tools.codex.factory operator phase1-extract --base-ref HEAD
```

Bridge dry-run (manifest-only, no bridge writes):
```powershell
$env:HITECH_SHARED_MODE = "both"
$env:HITECH_SHARED_DRYRUN = "1"
python -m tools.codex.factory operator phase1-extract --base-ref HEAD
```
