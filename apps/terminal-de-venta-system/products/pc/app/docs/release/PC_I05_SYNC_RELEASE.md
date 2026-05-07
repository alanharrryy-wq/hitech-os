# PC I05 - Sync ingest, dedupe, conflictos y release

## Objetivo

Cerrar el backoffice PC con ingest canónico de eventos Tablet, clasificación de duplicados, conflictos, rechazo por contrato y UI visible para supervisar sync.

## Alcance

- `/sync` deja de depender de overview genérico y muestra estado de ingest.
- `POST /api/sync/ingest` valida y persiste en `OutboxEvent` cuando no está en dry-run.
- `POST /api/sync/ingest?dryRun=1` clasifica eventos sin persistir para smoke seguro.
- Dedupe por `eventId` en lote y contra `OutboxEvent` existente.
- Conflictos: producto descontinuado, precio viejo, stock negativo, terminal no registrada, venta fuera de turno, secuencia inconsistente, schema inválido y topic desconocido.

## No toca

- Tablet.
- Mobile.
- `packages/shared-kernel/**`.
- `shared/contracts/**`.
- Migraciones destructivas.

## Evidencia esperada

- `tools/verify_pc_sync_release_05.mjs` PASS.
- DB smoke con tabla `OutboxEvent` PASS cuando existe DB canónica.
- HTTP smoke de `/api/sync/ingest?dryRun=1` PASS cuando PC está levantada.
- `pnpm exec tsc --noEmit` PASS cuando dependencias están instaladas.
