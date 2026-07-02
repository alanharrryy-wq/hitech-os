# PRISMA License Surface Visibility Wiring 0207

## Estado

Este patch restaura visibilidad gobernada de surfaces de licencia **ya existentes**. No crea una licencia nueva, no duplica LICDESK4/ADLANT4/LICFLOW2 y no borra source.

## Cambios

- Tablet shell moderno agrega `/settings/license` al dock visible.
- Tablet `screenZoneFromPath` clasifica `/settings/license` y `/settings/data` como soporte operativo en vez de referencia.
- PC promueve `/settings/license` como acceso final visible de configuración.
- PC mantiene `/license-runtime` como secundaria/soporte.
- PC manifiesto agrega `/settings/license` a `finalMenuRoutes`.

## No tocado

- Mobile.
- Shared UI.
- Web/Edit.
- Control Center.
- CSS global.
- Procesos, puertos, dev servers o Prisma generate.

## Motivación

`licsurf 0207` confirmó que las rutas existían. El problema era de visibilidad/discoverability: Tablet la tenía fuera del dock y PC sólo como secundaria/contrato.
