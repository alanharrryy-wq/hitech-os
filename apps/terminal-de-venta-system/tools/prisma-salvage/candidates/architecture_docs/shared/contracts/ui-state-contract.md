# Shared UI State Contract

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

Evita flujos silenciosos y fija estados visuales de Tablet y PC.


## Estados canonicos

- `idle`
- `loading`
- `ready`
- `empty`
- `error`
- `offline`
- `sync_pending`
- `sync_failed`
- `success`

## Rule

No operational flow may be silent on error, conflict, offline state, or sync failure.

## Tablet visual states

Product search, barcode/SKU resolve, cart/ticket, sale completion, payment method, stock decrement, outbox, daily report, export, offline/degraded runtime, sync pending and sync failed.

## PC visual states

Dashboard, catalog, stock, movements, physical counts, purchasing, receiving, replenishment, audit, sync ingest and conflicts.
