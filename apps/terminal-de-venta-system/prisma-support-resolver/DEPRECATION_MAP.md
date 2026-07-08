# Deprecation Map

Fecha: 2026-07-08

| Fuente vieja | Decision | Nuevo canonico | Estado | Nota |
|---|---|---|---|---|
| `apps/terminal-de-venta-system/prisma-control-center` | DEPRECATE_DUPLICATE | `apps/terminal-de-venta-system/Prisma Cloud Ctr` | Legacy reference | No se borra ni se mueve en esta pasada; no debe usarse como autoridad nueva. |
| `tooling/productization/schemas/support-ticket.schema.json` | USE_AND_CONNECT | `prisma-support-resolver/schemas/support-issue.schema.json` | Compatibilidad | Ticket sigue para seguimiento; SupportIssue queda para diagnostico/resolucion. |
| Productization support bundle docs dispersos | MERGE_INTO_CANONICAL | `prisma-support-resolver/contracts/PRISMA_SUPPORT_BUNDLE_STANDARD.md` | Referencia util | Las reglas utiles se condensan sin retirar docs historicos. |
| Productization runtime/device docs dispersos | USE_AND_CONNECT | `prisma-support-resolver/contracts/*RUNTIME*` y `*DEVICE*` | Referencia util | La autoridad tecnica sigue en shared/runtime y tooling schemas. |
| LICFLOW nombres historicos | USE_AND_CONNECT | labels operador: Cloud License Gateway, License Admin Bridge, Prisma Customer Setup | Compatibilidad | LICFLOW queda como lineage tecnico, no lenguaje primario de soporte. |

## No retirado

No se retiro fisicamente ningun archivo a `F:\Trash-old` porque no se confirmo
basura real sin referencias activas. La accion correcta aqui fue mapear,
deprecar y extender sin perdida de historial.
