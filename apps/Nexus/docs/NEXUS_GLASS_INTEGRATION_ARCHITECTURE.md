# Nexus + Glass Integration Architecture

## Objective

Host Nexus as a real runtime/business module inside the reusable PySide6 glass host, with neutral contracts as the official boundary.

## Layer split

1. Host platform (reused, unchanged): `forgeos/shared/pyside6_glass/*`
2. Nexus runtime engine: `apps/Nexus/nexus/runtime/engine.py`
3. Nexus contract registration + hosted module bridge: `apps/Nexus/nexus/integration/module.py`
4. Nexus desktop composition in host: `apps/Nexus/nexus/host/window.py` and `apps/Nexus/nexus/host/surfaces.py`
5. App entry: `apps/Nexus/nexus_app.py`

## Contract boundary

Nexus keeps business behavior behind `IntegrationService` endpoints.

Desktop host calls:

- `InProcessIntegrationAdapter.command(...)`
- `InProcessIntegrationAdapter.query(...)`
- `InProcessIntegrationAdapter.snapshot(...)`
- `InProcessIntegrationAdapter.poll_events(...)`

The host does not mutate engine state by directly touching widget internals.

## In-process-first strategy

Desktop path uses in-process adapter by default.

Optional local HTTP bridge can be enabled for external test clients, but it is not required for local desktop operation.

## Host/module relationship

- `GlassPanelTemplate` is the visual shell.
- `GlassWorkspaceRuntime` orchestrates layout/persistence/visibility.
- `NexusHostedModule` plugs runtime + business engine + integration service.
- `NexusGlassDesktopWindow` composes Nexus surfaces and actions from contract calls.

## Vertical slice included

- Summary/overview surface
- Records + detail
- Approvals queue
- Timeline/activity
- Runtime health
- Workspace state save/load
- Layout commands via shared workspace namespace (`workspace.layout.apply`)

## Persistence

Nexus uses platform workspace state persistence through runtime:

- Save: `runtime.save_workspace_state(path=tools/_local/tmp/nexus_workspace_state.json)`
- Load: `runtime.load_workspace_state(path=...)`

## Threading model

Current slice is synchronous in desktop UI thread with lock-protected runtime engine state (`RLock`).

No background workers were added in this iteration.

## What remains intentionally deferred

- Full async/background job execution model for long-running operations
- Production auth and hardened external transport
- Cross-process session coordination
- Complete domain breadth from historical Nexus archives

