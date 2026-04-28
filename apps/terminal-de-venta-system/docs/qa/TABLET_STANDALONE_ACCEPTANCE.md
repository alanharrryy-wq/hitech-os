# Tablet Standalone Acceptance

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

# QA Acceptance Contract

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

Fija criterios de aceptacion para pasar de canon a implementacion de motores/UI/sync.


## Tablet acceptance

- tablet-db-init creates/uses data/tablet-pos.db
- tablet-dev runs without PC
- product search
- barcode/SKU resolve
- build ticket
- complete sale
- decrement stock
- create stock movement
- create events/outbox
- show daily summary
- export sales
- export events
- export movements
- show visible errors
- operate offline
- pass typecheck

## PC acceptance

- show catalog
- show stock
- show movements
- show physical counts
- show purchasing
- show receiving
- show replenishment
- show audit
- show dashboard
- ingest Tablet event
- mark conflict
- consolidate sale
- not block Tablet local sale

## Integration acceptance

- Tablet sells standalone
- Tablet creates outbox
- PC ingests event
- PC consolidates sale
- PC detects conflict
- Tablet keeps selling if PC is down
- Sync does not break local sales
