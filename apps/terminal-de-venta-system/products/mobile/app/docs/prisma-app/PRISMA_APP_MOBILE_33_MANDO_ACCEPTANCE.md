# PRISMA App Mobile i03 - Mando del dueño

## Objetivo

Rehacer i03 completa y limpia: Mobile/Pulso debe mostrar el mando del dueño con seis superficies reales: Command Center, Action Inbox, Daily Brief, Decision Ledger, Pulse Timeline y Health Radar.

## Cambios instalados

- `PrismaMobileDashboard.tsx` integra las seis superficies de mando.
- `package.json` agrega `verify:mando` y lo encadena en `check:all`.
- `tools/verify_prisma_app_mobile_33_mando_contracts.mjs` valida contrato real del repo, sin depender de palabras literales frágiles en el componente.
- `docs/prisma-app/qa/prisma-app-mobile-33-mando-runtime-scenarios.json` documenta escenarios de aceptación.

## Fuera de alcance

- No toca Tablet.
- No toca PC.
- No toca shared-kernel.
- No toca shared/contracts.
- No toca Prisma, DB ni migraciones.

## READY

READY requiere: lane Mobile correcta, checksums válidos, verifier 33 PASS, verifiers Mobile 20-25 si existen PASS, pnpm `verify:mando`, `typecheck`, `build`, `check:all` PASS y smoke HTTP en 3140 PASS o caveat explícito sólo si el entorno bloquea levantar servidor.
