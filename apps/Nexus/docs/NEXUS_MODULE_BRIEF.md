# Nexus Hosted Module Brief

## 1) What is the base class of a visual module?

`NexusVisualModuleBase` in `apps/Nexus/nexus/host/surfaces.py`, which subclasses `QWidget`.

## 2) How does the host register a module?

`NexusGlassDesktopWindow` creates `NexusHostedModule` via `create_nexus_hosted_module(runtime, namespace="nexus")`, which wires `IntegrationService`, `GlassRuntimeIntegrationBridge`, Nexus contracts, and `InProcessIntegrationAdapter`.

## 3) How does a module send a command/query?

Via `NexusHostedModule.command(...)` and `NexusHostedModule.query(...)`, which forward envelopes to `InProcessIntegrationAdapter`.

## 4) How does it receive snapshots/events?

- Snapshots: `NexusHostedModule.snapshot(snapshot_id, selector)`
- Events: `NexusHostedModule.poll_events(since_sequence, limit)`

Both use the same contract boundary through the in-process adapter.

## 5) How is workspace state persisted?

Through `GlassWorkspaceRuntime.save_workspace_state(...)` and `load_workspace_state(...)`, wrapped by `NexusHostedModule.save_workspace_state()` and `load_workspace_state()`, stored at `tools/_local/tmp/nexus_workspace_state.json`.

## 6) What is the threading model?

Single UI-thread command/query/snapshot dispatch in this slice, with `NexusRuntimeEngine` protected by `RLock` for safe shared state access.

## 7) What actor/session context is available?

`IntegrationClientContext` fields are populated in `NexusHostedModule.context(...)`:

- `client_id`
- `session_id`
- `origin`
- `workspace_id`
- `device_hint`
- `capabilities`
- `metadata`

## 8) What is the first slice integrated?

A runnable desktop Nexus host with:

- overview summary
- records/detail
- approvals
- timeline/events
- health
- command path (`record.upsert`, `record.stage.set`, `approval.state.set`, `note.append`)
- query path (`summary`, `records`, `record`, `approvals`, `health`)
- snapshot path (`workspace`, `timeline`, `health`)
- event poll path
- workspace state save/load

