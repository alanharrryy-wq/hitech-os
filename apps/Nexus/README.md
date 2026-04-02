# Hitech Nexus on Glass Host

This app integrates Nexus as a hosted runtime module inside the reusable PySide6 glass platform.

## What this is

- A desktop-hosted Nexus slice running on `forgeos/shared/pyside6_glass`.
- A clean host/module integration using neutral contracts (`command/query/snapshot/event`).
- In-process adapter as the primary desktop path.
- Optional local HTTP adapter only as an extra bridge.

## What this is not

- Not a rewrite of the glass platform.
- Not direct business logic in shared widgets.
- Not a product-specific web stack.

## Run

```powershell
python F:\repos\hitech-os\apps\Nexus\nexus_app.py
```

Optional local HTTP bridge:

```powershell
python F:\repos\hitech-os\apps\Nexus\nexus_app.py --enable-http-bridge --http-port 3189
```

Smoke:

```powershell
python F:\repos\hitech-os\apps\Nexus\nexus_app.py --smoke
```

## First vertical slice

- Overview summary surface (query-driven).
- Records surface (list + detail).
- Approval surface (state transitions).
- Timeline surface (runtime timeline + integration event poll).
- Health surface.
- Commands:
  - `nexus.record.upsert`
  - `nexus.record.stage.set`
  - `nexus.approval.state.set`
  - `nexus.note.append`
- Queries:
  - `nexus.summary.get`
  - `nexus.records.list`
  - `nexus.record.get`
  - `nexus.approvals.list`
  - `nexus.health.get`
- Snapshots:
  - `nexus.workspace`
  - `nexus.timeline`
  - `nexus.health`

## Host/module boundaries

- Shared visual host stays in `forgeos/shared/pyside6_glass`.
- Nexus runtime/business logic lives in `apps/Nexus/nexus/runtime`.
- Nexus contract registration lives in `apps/Nexus/nexus/integration`.
- Nexus desktop composition lives in `apps/Nexus/nexus/host`.

## Future client compatibility

Because Nexus behavior is contract-backed, future web/mobile/local tools can consume the same service boundary via adapter layers without redesigning the runtime.

