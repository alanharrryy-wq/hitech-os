# PRISMA Surface Cleanup 3006

## Authority

This cleanup is authorized by `surfverdict 3006.md` and `automesh mesh1 3006 0635 result.zip`.

Included surfaces: Tablet, PC and Chart Lab.
Excluded surfaces: Mobile and Shared UI.

## Scope

This package only adds product navigation contracts, manifests and a static verification gate. It does not wire runtime menus, move source files, edit CSS, change routes, start servers, stop servers, free ports or run Prisma generation.

## Product decision

Tablet must behave as a floor-selling terminal. PC must behave as a modular backoffice. Chart Lab, Visual OS, reference routes, release gates and visual laboratories must remain outside final-user navigation.

## Tablet final surfaces

- Venta: `/pos`; `/checkout` remains a sale step.
- Turno y caja: `/shift`.
- Inventario: `/stock`, with `/catalog`, `/existencias` and `/inventory/low-stock` as secondary routes.
- Ventas: `/sales/today` and `/sales/history`, with dynamic detail routes opened from lists.
- Devoluciones: `/returns`, plus contextual return from ticket.
- Sync y offline: `/sync`, `/offline`, with outbox as support detail.
- Configuración: `/settings/license` and `/settings/export`.

## PC final surfaces

- Hoy: `/dashboard`.
- Inventario: `/catalog` and inventory secondary routes.
- Compras y proveedores: `/purchasing`, `/proveedores` and purchase secondary routes.
- Ventas y caja: `/sales-control`, `/cash-sessions`, `/metricas-dia`.
- Sync y Tablet Ops: `/sync`, `/devices`, `/sync-operativo`, `/outbox-operativo`, `/tablet-communication`.
- Reportes y BI: `/exportables`, `/prisma-insights` and BI/report secondary routes.
- Sistema y calidad: `/settings`, license, audit and data quality routes.
- Ayuda: `/glosario`.

## Hidden from final users

Tablet Visual OS, visual reference, visual catalog, release gate, dark POS reference and screen previews must not appear in final-user menus.

PC laboratory, visual reference aliases, Chart Lab aliases, governance and technical filter routes must not appear in final-user menus.

## Not touched in this phase

- Mobile.
- Shared UI.
- Web.
- Control Center.
- Runtime menu shell wiring.
- Route file moves.
- Source deletion.
- Global CSS.

Runtime menu wiring requires a fresh owner-specific Mesh that names the exact Tablet and PC navigation/AppShell files.
