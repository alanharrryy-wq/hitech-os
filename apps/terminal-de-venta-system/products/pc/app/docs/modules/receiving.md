# PC I04 - Recepción

## Objetivo

Recepción contra orden, diferencias faltantes/sobrantes y estado de posting operativo.

## Alcance I04

- Usa `getOperationWorkspace`.
- Lee persistencia canónica mediante Prisma cuando está disponible.
- Expone estados honestos si la DB no existe o no responde.
- No toca Tablet, Mobile, shared-kernel ni contratos compartidos.
- No modifica schema Prisma ni hace migraciones.

## Evidencia esperada

- `tools/verify_pc_operation_04.mjs` en PASS.
- `pnpm exec tsc --noEmit` en PASS cuando hay dependencias.
- DB smoke de compras/recepción/reabasto/KPI si existe `canonical.db`.
- HTTP smoke de `/purchasing`, `/receiving`, `/replenishment`, `/dashboard` si PC está levantada en `127.0.0.1:3130`.
