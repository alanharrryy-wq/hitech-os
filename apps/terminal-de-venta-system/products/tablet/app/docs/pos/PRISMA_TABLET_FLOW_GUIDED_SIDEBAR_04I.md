# PRISMA Tablet Flow Guided Sidebar 04I - Superseded by 05A

## Estado

Este criterio queda superado por:

`PRISMA_TABLET_FLOW_CLARITY_05A_NAV_TOPBAR_COLLAPSE`

## Por que cambio

La navegacion contextual anterior escondia rutas para mantener foco POS. La intencion era correcta, pero en uso real y QA visual hizo dificil encontrar pantallas disponibles.

## Nueva regla

Tablet conserva foco POS, pero la navegacion principal debe estar siempre visible y agrupada:

- Operacion: Vender, Inicio, Turno y caja, Ventas de hoy.
- Consulta rapida: Catalogo, Existencias.
- Soporte: Pendientes, Offline / Export, Estado del sistema, Licencia.

## Diferencia clave

Antes:

- En `Inicio`, el sidebar mostraba solo `Inicio`.
- Catalogo, Existencias, Pendientes y Estado aparecian solo segun contexto.

Ahora:

- El sidebar muestra las pantallas principales siempre.
- El logo PRISMA contrae/descontrae la barra lateral.
- Inicio funciona como mapa de trabajo.
- La barra superior integra el estado operativo en una sola franja compacta.

## Alcance

Toca solo UI/UX Tablet:

- `components/tablet-shell/tablet-nav.ts`
- `components/tablet-shell/prisma-tablet-shell.tsx`
- `components/tablet-shell/prisma-tablet-shell.module.css`
- `components/tablet-runtime/tablet-runtime-status-strip.tsx`
- `components/tablet-home/tablet-home-screen.tsx`
- `components/tablet-home/tablet-home.module.css`
- `tools/verify_tablet_flow_guided_sidebar_04i.mjs`

## No toca

- backend;
- DB;
- Prisma schema;
- sync contracts;
- ventas/carrito/cobro;
- shared-kernel;
- PC;
- Mobile;
- packshots o image resolver.
