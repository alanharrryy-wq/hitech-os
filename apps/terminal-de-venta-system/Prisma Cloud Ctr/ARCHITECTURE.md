# Prisma Cloud Ctr Architecture

## Canonical Home

```text
apps/terminal-de-venta-system/Prisma Cloud Ctr
```

This folder is the canonical home for Prisma Cloud Ctr.

## Components

- `internal/py/prisma_unified_lab_v3.py` runs the local-only HTTP server on `127.0.0.1:3160`.
- `internal/py/licflow4_admin_bridge.py` owns the local/admin LICFLOW4 bridge for status, activate, refresh, revoke, sanitized audit, and diagnostics.
- `internal/py/cloud_saas_api.py` reads config, calls safe read-only cloud endpoints, and exposes LICFLOW3 metadata.
- `internal/py/license_ops_api.py` reads local runtime/license state without mutating provisioning.
- `internal/web/cloud_command_center.html` is the main UI entrypoint.
- `internal/web/cloud_command_center.js` renders operator surfaces and calls local APIs.
- `internal/config/cloud_saas.json` contains base URL, endpoints, and LICFLOW3 live metadata.

## External Owners Kept Outside

- Cloudflare Worker: `apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker`
- Shared licensing contracts: `apps/terminal-de-venta-system/shared/licensing`
- Verifiers: `apps/terminal-de-venta-system/tools/verify-licflow3.mts` and `apps/terminal-de-venta-system/tools/verify-licflow4.mts`
- Operational manual: `apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md`

These are referenced, not copied, to avoid duplicate adapters and duplicate Control Centers.

## Data Flow

Browser UI -> local 3160 server -> Python adapters -> safe cloud GETs or local read-only runtime files.

Confirmed admin actions flow through:

```text
Browser UI -> /api/licflow4/bridge/* -> licflow4_admin_bridge.py -> LICFLOW3 live endpoint
```

The admin token is detected as a boolean for UI/status. Its value is read only inside `licflow4_admin_bridge.py` immediately before the outbound server-side call and is never serialized back to the browser or diagnostics.

## Non-Goals

- No new Worker.
- No duplicate LICFLOW2.
- No duplicate root folder.
- No D1 exports.
- No secret handling in frontend.
