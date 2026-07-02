# PRISMA Tablet Shell Product Navigation Wiring 0207

## Resultado esperado

Este cambio conecta el shell moderno de Tablet (`PrismaTabletShellUnified`) al contrato de producto `TABLET_FINAL_NAVIGATION`.

## Cambios

- `components/tablet-shell/tablet-nav.ts` deja de mantener navegación final hardcodeada.
- `TABLET_NAV_ITEMS` se deriva de `TABLET_FINAL_NAVIGATION`.
- `PrismaTabletShellUnified` deja de promover `/` y `/catalog` como navegación principal/dock.
- El dock principal queda centrado en operación: vender, turno, stock, ventas, devoluciones y sync.
- La marca del shell manda a `/pos`, no a `/`.
- El chip de tienda manda a `/stock`, canonical de inventario para vender.

## No tocado

- Mobile.
- Shared UI.
- Web/Edit.
- Control Center.
- CSS global.
- Rutas físicas.
- Prisma generate.
- Procesos, puertos o dev servers.

## Pendiente posterior

Después de este wiring, la validación visual/runtime debe confirmar que ninguna ruta lab/dev/reference aparece en el menú final Tablet y que las rutas secundarias siguen accesibles desde sus flujos.
