# Cloud Center Adapter

Decision: `EXTEND_EXISTING`.

Owner vivo:

- `Prisma Cloud Ctr/internal/py/prisma_unified_lab_v3.py`
- `Prisma Cloud Ctr/internal/web/cloud_command_center.js`
- `Prisma Cloud Ctr/internal/py/cloud_saas_api.py`
- `Prisma Cloud Ctr/internal/py/license_ops_api.py`
- `Prisma Cloud Ctr/internal/py/licflow4_admin_bridge.py`

El adapter debe servir `/api/support/*`, leer catalogos del root canonico y
reutilizar diagnostics/bridge existentes.
