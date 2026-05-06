# PRISMA App Mobile 17 - Data Plane real Tablet/PC

## Objetivo

Esta integración sustituye la fuente demo de PRISMA App móvil por una capa de data-plane que conecta, normaliza y expone señales reales desde Tablet POS y PC Backoffice.

## Qué aporta

- Configuración explícita por variables `PRISMA_MOBILE_*`.
- Fetch con timeout, retry y diagnóstico por upstream.
- Adaptadores para ventas del día, inventario bajo, outbox/sync y dashboard PC.
- Normalización a contratos móviles existentes.
- Alertas calculadas por stock, sync, caja y disponibilidad.
- Snapshot `/api/mobile/snapshot` construido desde data-plane.
- Rutas `/api/mobile/*` sin imports demo.
- Matriz funcional de regresión con escenarios de mapeo Tablet/PC.

## Variables principales

```powershell
$env:PRISMA_MOBILE_TABLET_ORIGIN="http://127.0.0.1:3120"
$env:PRISMA_MOBILE_PC_ORIGIN="http://127.0.0.1:3130"
$env:PRISMA_MOBILE_BUSINESS_ID="biz_tablet_standalone"
$env:PRISMA_MOBILE_TERMINAL_ID="terminal_tablet_local_01"
$env:PRISMA_MOBILE_BUSINESS_NAME="PRISMA Operación"
```

## Fuentes esperadas

- Tablet POS: `/api/pos/sales/today`, `/api/pos/inventory/low-stock`, `/api/pos/events/outbox`, `/api/health`.
- PC Backoffice: `/api/backoffice/dashboard`, `/api/health`.

## Regla importante

Si Tablet o PC no responden, Mobile no inventa datos. Marca estado parcial/offline, deja warnings y conserva contrato para que la UI no reviente como licuadora sin tapa.
