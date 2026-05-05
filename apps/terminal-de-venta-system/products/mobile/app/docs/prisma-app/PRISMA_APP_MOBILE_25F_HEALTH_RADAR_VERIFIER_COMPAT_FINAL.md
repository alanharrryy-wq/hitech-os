# PRISMA App Mobile 25F - Health Radar verifier compatibility final

## Objetivo
Corregir el falso negativo de `pnpm run verify:health-radar` después de aplicar 25E.

## Diagnóstico
25D sí corrigió las llaves duplicadas del Health Radar, pero su verificador quedó amarrado a `package.version === 0.25.3`.
25E subió el paquete móvil a `0.25.4`, por eso el verificador falló aunque el componente y el contrato seguían correctos.

## Corrección
- `verify_prisma_app_mobile_25_health_radar.mjs` ya no exige versión exacta `0.25.3`.
- Ahora acepta versiones `>= 0.25.3` y `< 0.26.0`.
- Conserva el marcador 25D obligatorio: `prismaMobileHealthRadarDuplicateKeyFinalVersion === 0.25.3`.
- Agrega verificador 25F para evitar que vuelva el pin exacto de versión.

## Archivos tocados
- `package.json`
- `tools/verify_prisma_app_mobile_25_health_radar.mjs`
- `tools/verify_prisma_app_mobile_25f_health_radar_verifier_compat.mjs`
- `docs/prisma-app/PRISMA_APP_MOBILE_25F_HEALTH_RADAR_VERIFIER_COMPAT_FINAL.md`
- `docs/prisma-app/qa/prisma-app-mobile-25f-health-radar-verifier-compat-corpus.jsonl`

## Validación recomendada

```powershell
cd F:epos\hitech-ospps	erminal-de-venta-system\products\mobilepp
pnpm run verify:health-radar-compat
pnpm run verify:health-radar
pnpm run verify:data-plane-types
pnpm run typecheck
```

## Nota
Este paquete no toca UI, rutas ni data-plane. Solo corrige el contrato del verificador para que no trate cada patch version como apocalipsis fiscal.
