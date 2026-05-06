# PRISMA App Mobile 25E - Data-plane type contract final

## Objetivo
Cerrar los errores de `pnpm run typecheck` detectados después de 25D sin tocar la UI del Health Radar.

## Problemas corregidos

1. `summary.health` quedaba inferido como `string` al construir el snapshot, aunque el contrato exige solo `sano | revisar | urgente | offline`.
2. `buildOperationalAlerts` esperaba una propiedad heredada `sales`, pero el estado real del data-plane usa `salesToday`.

## Archivos tocados

- `src/lib/prisma-app/mobile-data-plane/payload-builders.ts`
- `src/lib/prisma-app/mobile-data-plane/alerts-policy.ts`
- `tools/verify_prisma_app_mobile_25e_data_plane_type_contract.mjs`
- `docs/prisma-app/qa/prisma-app-mobile-25e-type-contract-regression-corpus.jsonl`
- `package.json`

## Validación esperada en Windows

```powershell
cd F:epos\hitech-ospps	erminal-de-venta-system\products\mobilepp
pnpm run verify:data-plane-types
pnpm run verify:health-radar
pnpm run typecheck
```

## Nota sobre puerto 3140

Si `pnpm run dev` marca `EADDRINUSE`, la app ya está levantada o hay otro proceso ocupando el puerto. Este paquete no mata procesos ajenos; primero se identifica al dueño del puerto.
