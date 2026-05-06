# PC Backoffice Contract

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

Define PC como panel administrativo/gobierno sin volverlo dependencia para venta local Tablet.


## PC sirve

- full catalog administration
- SKU/barcode control
- stock by location
- movements
- physical counts
- purchasing
- receiving
- replenishment
- audit
- executive dashboard
- sync and reconciliation
- multi-branch/multi-terminal control

## PC puede

- define policies
- publish catalogs
- receive events
- reconcile conflicts
- audit sales
- consolidate information

## PC must not be required for

- basic local sale
- local ticket
- local stock decrement
- local day report
- local export

## Modulos objetivo

- `catalog`
- `stock`
- `counts`
- `purchasing`
- `receiving`
- `replenishment`
- `audit`
- `sync`
- `dashboard`
- `settings`
