# Prisma Cloud Center Architecture

## Canonical Home

```text
apps/terminal-de-venta-system/prisma-control-center-unified-shell-lab-v3
```

This folder remains the canonical home even though its name contains historical terms.

## Components

- `internal/py/prisma_unified_lab_v3.py` runs the local-only HTTP server on `127.0.0.1:3160`.
- `internal/py/cloud_saas_api.py` reads config, calls safe read-only cloud endpoints, and exposes LICFLOW3 metadata.
- `internal/py/license_ops_api.py` reads local runtime/license state without mutating provisioning.
- `internal/web/cloud_command_center.html` is the main UI entrypoint.
- `internal/web/cloud_command_center.js` renders operator surfaces and calls local APIs.
- `internal/config/cloud_saas.json` contains base URL, endpoints, and LICFLOW3 live metadata.

## External Owners Kept Outside

- Cloudflare Worker: `apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker`
- Shared licensing contracts: `apps/terminal-de-venta-system/shared/licensing`
- Verifiers: `apps/terminal-de-venta-system/tools/verify-licflow3.mts`
- Operational manual: `apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md`

These are referenced, not copied, to avoid duplicate adapters and duplicate Control Centers.

## Data Flow

Browser UI -> local 3160 server -> Python adapters -> safe cloud GETs or local read-only runtime files.

Admin/mutating cloud calls are blocked in this version. LICFLOW4 Admin Bridge will own future writes.

## Non-Goals

- No new Worker.
- No duplicate LICFLOW2.
- No duplicate root folder.
- No D1 exports.
- No secret handling in frontend.
