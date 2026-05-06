# Runtime Modes Contract

Estado: canon listo para codigo.
Idioma operativo: es-MX.
Alcance: contratos, arquitectura y criterios de implementacion; no implementa motores finales.

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

## Proposito

Define los modos oficiales de ejecucion para Tablet/PC sin dejar que sync sustituya autonomia local.


## `standalone`

Tablet operates with local DB and exports data.
PC required: no.
Internet required: no.

## `managed`

Tablet syncs with PC/backoffice.
PC required: yes for governance/sync.
Internet/network: intermittent or stable.

## `degraded_managed`

Tablet belongs to a managed operation, but keeps selling if PC/network goes down.
PC required: yes for governance, no for basic sales.
Internet required: no for basic sales.

## Mandatory runtime rules

- Tablet must never block basic sale because PC is absent.
- If sync fails, allowed local sale continues.
- Sensitive operations are marked.
- Events go to outbox.
- PC resolves conflicts later.
- Tablet commands must not validate PC existence for Tablet tasks.
- Do not depend on tools/_local/data/terminal-de-venta-system/canonical.db for selling.
- Do not use cwd as trusted root.
- Do not invent magic DB paths.

## Variables Tablet

- `TABLET_DATABASE_URL`
- `TABLET_RUNTIME_MODE`

## DB local canonica

- Ruta del proyecto: `products/tablet/app/data/tablet-pos.db`
- Fallback Prisma: `file:./data/tablet-pos.db`
