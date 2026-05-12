# PRISMA Event Contract

Status: canonical event and lifecycle contract.
Scope: Tablet outbox, PC ingest, projectors, Mobile snapshot, Control audit.

## Machine Source

The machine-readable source is:

`F:\repos\hitech-os\apps\terminal-de-venta-system\shared\contracts\sync-event-contract.v1.json`

Runtime constants are owned by:

`F:\repos\hitech-os\apps\terminal-de-venta-system\shared\twin-kernel\src\sync\events.ts`

## Required Event Envelope

Current PRISMA events must carry:

- `eventId`
- `eventType`
- `topic` as compatibility alias for existing code
- `schemaVersion`
- `idempotencyKey`
- `terminalId`
- `businessId`
- `payload`
- `occurredAt`
- `source`
- `actorId`
- `correlationId` when useful

`eventType` is the semantic event name. Existing `topic` remains accepted for compatibility and must match `eventType` when both are present.

## Lifecycle

Canonical lifecycle states:

- `created_local`
- `queued`
- `sent`
- `received`
- `validated`
- `accepted`
- `projected`
- `reconciled`
- `conflict`
- `failed`
- `dead_letter`

## Compatibility Mapping

`acked` is an old outbox status. It means compatibility acknowledgment only.

It means full reconciliation only when the same ledger row also has:

- `lifecycleStatus = reconciled`
- `receivedAt`
- `validatedAt`
- `acceptedAt`
- `projectedAt`
- `reconciledAt`

Without that lifecycle evidence, `acked` must not be presented as governed reconciliation.

## Core Event Types

Implemented/core projector targets:

- `sale.completed`
- `stock.decremented`
- `cash.session.opened`
- `cash.movement.recorded`
- `inventory.low_stock_detected`

Compatibility event mappings:

- `shift.opened` maps to `cash.session.opened`.
- `shift.closed` maps to `cash.movement.recorded` when payload contains cash movement data.

## Conflict Strategy

PC must classify conflict instead of faking success when it sees:

- duplicate sale IDs with mismatched totals or folios
- impossible stock transitions such as negative `stockAfter`
- overlapping open cash sessions for the same business and terminal
- stale or unsupported `schemaVersion`
- unknown event types
- missing Business, Terminal, Product, or CashSession references

## Idempotency

Primary idempotency key:

`idempotencyKey`

Compatibility fallback:

`eventId`

Tablet sale events create stable idempotency keys from event type, business, terminal, aggregate, and sale context where needed.
PC rejects duplicates inside a batch and treats previously stored idempotency keys as duplicates.

## Structured Diagnostics

Validation/projector failures must preserve:

- conflict code
- lifecycle state
- errors
- diagnostics
- touched projector models

Diagnostics live on the event ledger row in `diagnosticsJson` and `lastError` when relevant.
