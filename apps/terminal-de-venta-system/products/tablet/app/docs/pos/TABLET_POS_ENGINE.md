# Tablet POS Engine

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

Brief tecnico para el futuro motor de venta local Tablet.


`pos-engine` ejecuta reglas atomicas de venta local: validar ticket, resolver producto, calcular totales, cerrar venta, crear lineas, decrementar stock, registrar `StockMovement` y emitir `OutboxEvent`.

Flujo: `UI Touch -> API Routes / Server Actions -> pos-api -> pos-engine -> Prisma Client -> SQLite local tablet-pos.db -> Outbox/Event Log`.

Invariantes: no consultar PC para autorizar venta basica local; no depender de `tools/_local/data/terminal-de-venta-system/canonical.db`; emitir eventos operacionales por venta/stock/ticket.
