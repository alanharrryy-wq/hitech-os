# PRISMA Runtime Navigation Wiring 0207

Este cambio conecta la fase de `surface-cleanup` con navegación runtime de bajo riesgo.

## Autoridad

- `navmesh 0207 0116 result.zip`
- `navown 0207 0123 result.zip`
- contratos/manifiestos `surface-cleanup` ya aplicados

## Alcance aplicado

- Tablet: `src/composition/navigation.ts` deja de depender de `TABLET_NAV_ITEMS` para el contrato de navegación final y consume `TABLET_FINAL_NAVIGATION`.
- PC: `src/composition/navigation.ts` deja de mantener una lista primaria artesanal y deriva la navegación principal desde `PC_FINAL_NAVIGATION`.
- PC: el menú primario añade `Glosario` y elimina mención/promoción de Chart Lab en Análisis.
- Gate nuevo: `tools/quality/verify_surface_runtime_navigation_wiring_0207.mjs`.

## Alcance no aplicado

No se toca Mobile, Shared UI, Web, Control Center, CSS global, procesos, puertos, dev servers ni Prisma generate.

## Nota Tablet

Este wiring actualiza el owner `src/composition/navigation.ts`. Si una pantalla usa `PrismaTabletShellUnified` con `components/tablet-shell/tablet-nav.ts`, esa pieza queda para una fase siguiente con owner explícito de shell unificado.
