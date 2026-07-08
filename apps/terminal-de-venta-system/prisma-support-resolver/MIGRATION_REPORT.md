# Migration Report

Fecha: 2026-07-08

## Resumen de decision por pieza

| Pieza | Decision | Evidencia |
|---|---|---|
| `shared/licensing/customer-setup-contract.ts` | USE_AS_IS | Contrato vivo para Setup Code, Setup Link, Setup QR, Device Claim y slots. |
| `shared/licensing/licflow3-cloud-contract.ts` | USE_AS_IS | Contrato vivo Cloud License Gateway y endpoints existentes. |
| `shared/licensing/license-governor.ts` | USE_AND_CONNECT | Fuente viva de status local PC/Tablet. |
| `tools/verify-licflow2.mts` | USE_AS_IS | Verifier LICFLOW2 existente. |
| `tools/verify-licflow3.mts` | USE_AS_IS | Verifier Cloud License Gateway existente. |
| `tools/verify-licflow4.mts` | USE_AND_CONNECT | Verifier License Admin Bridge existente. |
| `tools/verify-customer-setup-multidevice.mjs` | USE_AS_IS | Verifier Customer Setup tri-surface existente. |
| `Prisma Cloud Ctr/internal/py/license_ops_api.py` | USE_AND_CONNECT | Diagnostico read-only existente. |
| `Prisma Cloud Ctr/internal/py/cloud_saas_api.py` | USE_AND_CONNECT | Snapshot Cloud License Gateway existente. |
| `Prisma Cloud Ctr/internal/py/licflow4_admin_bridge.py` | USE_AND_CONNECT | Simulacion/operacion confirmada existente. |
| `Prisma Cloud Ctr/internal/web/cloud_command_center.js` | EXTEND_EXISTING | Superficie `#support` existente; se extiende, no se reemplaza. |
| `Prisma Cloud Ctr/internal/web/cloud_command_center.css` | EXTEND_EXISTING | Estilos locales para tablas de soporte dentro del shell existente. |
| `Prisma Cloud Ctr/internal/py/prisma_unified_lab_v3.py` | EXTEND_EXISTING | Router 3160 existente; se conecta `/api/support/*`. |
| `Prisma Cloud Ctr/internal/py/support_resolver_api.py` | CREATE_MISSING | Adapter local faltante para servir catalogos, busqueda, diagnose, simulate, apply y export-case. |
| `products/pc/app/components/license/license-status-card.tsx` | EXTEND_EXISTING | Se agrega issue principal/codigo canonico sin redisenar PC. |
| `products/tablet/app/components/license/license-status-card.tsx` | FIX_EXISTING | Se elimina contradiccion potencial ready/bloqueado y se muestra codigo canonico. |
| `products/mobile/app/src/components/prisma-app/PrismaMobilePremiumNavigator.tsx` | EXTEND_EXISTING | Se agrega superficie "Licencias y dispositivos" en Mobile existente. |
| `tools/verify-support-resolver.mjs` | CREATE_MISSING | Verifier faltante para no duplicados, catalogo, fixtures, API/UI y seguridad. |
| `package.json` | EXTEND_EXISTING | Script `verify:support-resolver` agregado al paquete existente. |
| `prisma-support-resolver/*` | CREATE_MISSING | Root fisico canonico no existia. |
| `prisma-control-center/*` | DEPRECATE_DUPLICATE | Duplicado legacy, no autoridad. |
| `F:\PRISMA_CTX\LICENSING\issuers\adlant4-local\private-key.pem` | BLOCK_SECRET_RISK | Private key externa detectada por nombre/ruta; no se leyo ni copio. |

## Que ya estaba hecho

- LICFLOW2 local/offline/hybrid activation.
- LICFLOW3 Cloud License Gateway contract and live custom-domain baseline.
- LICFLOW4 License Admin Bridge with dry-run and confirmation gates.
- LICFLOW5 Customer Setup shared contract and tri-surface setup entrypoints.
- Productization schemas for runtime, device identity, support ticket and support bundle manifest.
- Cloud Ctr `#support` tab with passive diagnostics/copy support packet.

## Que se uso tal cual

- Shared licensing contracts and exports.
- Existing LICFLOW and Customer Setup verifiers.
- Existing Cloud Ctr shell and visual composition.
- Existing productization schemas as dependencies.

## Que se corrigio o completo

- Falta de root fisico unico para soporte resolutivo.
- Falta de catalogo canonico de codigos de soporte.
- Falta de schemas canonicos SupportIssue y SurfaceStatus.
- Falta de mapas de autoridad, duplicados, deprecacion y migracion.
- Falta de fixture obligatorio para asignacion de negocio incorrecta.

## Que se fusiono

- Reglas de support bundle/redaction desde productization y quality hacia el contrato canonico de soporte.
- Codigos dispersos de licencia/customer setup/runtime/Cloud/POS hacia `support-error-codes.json`.
- Acciones de LICFLOW4 y Customer Setup hacia `resolver-actions.json`.

## Que se creo porque no existia

- `prisma-support-resolver` con docs, contracts, schemas, catalogs, fixtures, adapters, evidence y tests/cases.
- Catalogos `support-error-codes`, `resolver-actions`, `surface-status-catalog`, `feature-gates`.
- Contratos Support Resolver Center, Surface Status, Search/Case, Resolution Action, Bundle, Device Activation, Customer Setup y Runtime Config.

## Que se bloqueo por secretos

- La private key externa en `F:\PRISMA_CTX\LICENSING\issuers\adlant4-local\private-key.pem`.
- Cualquier token/admin header/env real queda fuera de bundles, logs y docs.

## Rollback

Rollback local seguro: revertir los archivos creados/modificados en esta
pasada. No hubo deploy, D1 migration, process kill, puerto liberado ni Prisma
generate.

## Phase 3A · Cross-source identity reconciliation

Decision: `EXTEND_EXISTING`. PC/Admin diagnostic data is now treated as a technical source, not copied as a second truth. Support Resolver detects `CROSS_SOURCE_IDENTITY_SPLIT` when local runtime/license, PC admin customer context, POS local seed and external signed activation candidates disagree. Apply remains blocked until an authority route has backup, rollback and validation.


## recon3b - UI simulate wired to identity reconciliation

- Label: `EXTEND_EXISTING` / `FIX_EXISTING`.
- Fixed Cloud Center Support simulation so `Simular resolución` sends the same PC/Admin, runtime, local license and POS identity context used by the visible reconciliation panel.
- Added `identityReconciliationRequested:true`, `selectedAuthority`, and `authorityStrategy` to support API payloads.
- Promoted split cases to `IDENTITY_RECONCILIATION_REQUIRED` with top-level `primaryIssueCode:CROSS_SOURCE_IDENTITY_SPLIT`, `authorityChoices`, `candidateWorlds`, `identityReconciliation`, and `reconciliation`.
- Added support API hot-reload helper in Prisma Cloud Center so future `support_resolver_api.py` changes do not stay stale in the long-lived 3160 process after relaunch.
- No mutation implemented. `Resolver problema` remains blocked until a rollback-safe authority route exists.
- No license.json edit, no DB edit, no D1, no deploy, no Prisma generate, no token/private-key handling.


## recon4 2026-07-08T11:13:39

Se agregó ruta guiada `setup_claim_or_refresh_guided` para convertir `CROSS_SOURCE_IDENTITY_SPLIT` en un flujo producto: Setup Code / License Refresh. No edita `license.json`, no toca DB/D1/deploy/procesos y mantiene apply bloqueado hasta rollback-safe plan.


## RECON5_SETUP_CLAIM_APPLY_PREFLIGHT

- Added guarded Setup Code / License Refresh apply preflight.
- `simulate` continues to return `SETUP_CLAIM_OR_REFRESH_GUIDED` for `CROSS_SOURCE_IDENTITY_SPLIT`.
- `apply` remains non-mutating until setup code, signed refreshed license verification, backups, rollback and post-checks exist.
- Added UI Setup Code input and apply-plan panel.
- No manual `license.json` edits, no D1 migration, no deploy, no secrets exposed.
