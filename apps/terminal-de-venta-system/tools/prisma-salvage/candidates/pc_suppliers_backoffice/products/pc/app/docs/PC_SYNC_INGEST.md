# Pc Sync Ingest

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

PC es backoffice/governance. PC no bloquea venta local basica Tablet.


PC ingesta `OutboxEvent`, valida contrato, consolida, marca `acked`/`conflict` y nunca exige estar presente para que Tablet haya vendido localmente.
