# PRISMA App móvil 18 - Production Data Cleanup

## Objetivo

Quitar residuos que hacían que PRISMA App móvil pareciera inconclusa y dejar la superficie preparada para operar con fuentes conectadas de Tablet y PC.

## Qué cambia

- Se retira código heredado de maqueta visual que ya no debe participar en runtime.
- Se corrige el guardado de caché móvil para conservar únicamente el payload del snapshot.
- El endpoint `/api/mobile/snapshot` reporta una fuente honesta según el modo real: conectado, parcial u offline.
- La pantalla principal deja de anunciar número de iteración o estado de instalación.
- Se agrega `tools/verify_prisma_app_mobile_18_production_data_cleanup.mjs`.
- Se agrega un set de escenarios operativos conectados para QA móvil.

## Riesgo controlado

No se toca Tablet, PC, shared-kernel ni contratos compartidos. La entrega opera dentro de `products/mobile/app`.

## Validación local

```powershell
pnpm -C products/mobile/app run verify:production-data
pnpm -C products/mobile/app run typecheck
```

## Estado de madurez después de aplicar

La app móvil queda como tablero conectado con respaldo local, lista para que la siguiente iteración conecte caja/cortes reales y cierre el hueco más importante de operación.
