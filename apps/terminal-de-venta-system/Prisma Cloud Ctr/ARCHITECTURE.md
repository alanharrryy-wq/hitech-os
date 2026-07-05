# Prisma Cloud Center Architecture

## Canonical Home

```text
apps/terminal-de-venta-system/Prisma Cloud Ctr
```

This folder is the canonical repo home for Prisma Cloud Center. The folder name remains `Prisma Cloud Ctr` for compatibility.

## Components

- `internal/py/prisma_unified_lab_v3.py` runs the local-only HTTP server on `127.0.0.1:3160`.
- `internal/py/licflow4_admin_bridge.py` is the License Admin Bridge implementation for status, Simulation, Confirmed License Operation, sanitized audit, and diagnostics.
- `internal/py/cloud_saas_api.py` is the Cloud License Gateway metadata and safe read-only cloud adapter.
- `internal/py/license_ops_api.py` reads local runtime/license state without mutating provisioning.
- `internal/web/cloud_command_center.html` is the main UI entrypoint.
- `internal/web/cloud_command_center.js` renders operator surfaces and calls local APIs.
- `internal/config/cloud_saas.json` contains Cloud License Gateway base URL, endpoints, and live metadata.

## External Owners Kept Outside

- Cloud License Gateway Worker: `apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker`
- Shared licensing contracts: `apps/terminal-de-venta-system/shared/licensing`
- Verifiers: `apps/terminal-de-venta-system/tools/verify-licflow3.mts` and `apps/terminal-de-venta-system/tools/verify-licflow4.mts`
- Operational manual: `apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md`

These are referenced, not copied, to avoid duplicate adapters and duplicate Control Centers.

## Data Flow

Read-only cloud:

```text
Browser UI -> local 3160 server -> cloud_saas_api.py -> Cloud License Gateway safe GETs
```

Confirmed license operation:

```text
Browser UI -> Local License Admin API -> License Admin Bridge -> Cloud License Gateway API
```

Compatibility paths:

```text
Local License Admin API: /api/licflow4/bridge/*
Cloud License Gateway API: /api/licenses/*
```

Prisma Customer Setup:

```text
Prisma Cloud Center -> Cloud License Gateway source -> Setup Link/Code/QR -> Tablet/PC/Mobile Device Claim
```

The admin token is detected as a boolean for UI/status. Its value is read only inside `licflow4_admin_bridge.py` immediately before a confirmed server-side call and is never serialized back to the browser or diagnostics.

## Non-Goals

- No new Worker.
- No duplicate legacy license flow or adapter.
- No duplicate Control Center root.
- No D1 exports.
- No frontend secrets.
- No customer setup subsystem outside the shared licensing contract and existing Cloud License Gateway source.
