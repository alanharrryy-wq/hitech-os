# PC Tablet Communication Notes

## Boundary

PC governs when present. Tablet never waits for PC to sell, open local history, resolve local catalog, or keep local license fallback.

## Inbound Tablet-to-PC

Inbound communication is represented by existing `OutboxEvent`, `SyncAttempt`, `SyncConflict`, `SyncCheckpoint`, `SyncOutboxStatusBucket`, `DataSourceFreshness`, and `DeviceHeartbeat` models.

PC surfaces now expose:

- inbound event lifecycle;
- per-device heartbeat;
- last successful Tablet-to-PC event timestamp;
- outbox buckets;
- conflicts by severity and code;
- tri-db parity and PC-behind warning.

## Outbound PC-to-Tablet

No live external command delivery channel exists in repo-local code. The implemented equivalent is a governance command ledger:

- contract: `shared/contracts/pc-tablet-governance-command.v1.json`;
- durable model: `AuditEvent`;
- status: `queued_for_pickup`;
- idempotency: deterministic key per business, command, target and day;
- supported commands: `catalog.release`, `price-policy.release`, `license.refresh`, `runtime.refresh`.

This is not a fake send. It is an observable pending command record that can be picked up by a future real transport.

## Ack, retry and cancel

Repo-local ack transport is unavailable. The UI therefore reports pending/picked-up/acked only from persisted command state. Sync retry is implemented only for failed/dead_letter inbound events through `POST /api/backoffice/sync/retry`.

## Multi-tablet behavior

Targets are expressed as:

- `all`;
- `store:<id>`;
- `terminal:<id>`;
- `device:<id>`.

The command notes explicitly keep `safeToContinueSelling: true`.

## No-downgrade guarantee

Pending commands never block Tablet selling. App/schema compatibility is surfaced from heartbeat when available and marked as missing when not reported.
