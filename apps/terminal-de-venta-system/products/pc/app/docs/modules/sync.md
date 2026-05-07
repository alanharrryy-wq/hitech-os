# Módulo Sync PC

PC gobierna ingest y reconciliación. Tablet conserva venta local: PC valida después, no autoriza cada venta.

## Endpoint

- `GET /api/sync/ingest`: health/contrato.
- `POST /api/sync/ingest?dryRun=1`: clasificación sin persistencia.
- `POST /api/sync/ingest`: persistencia en `OutboxEvent`.

## Estados

- `accepted`: evento válido.
- `duplicate`: eventId repetido.
- `conflict`: evento válido pero requiere revisión.
- `rejected`: contrato inválido.
