# PRISMA Sync Standard

Status: canonical architecture decision.
Scope: apps/terminal-de-venta-system.

## Standard

The primary PRISMA sync architecture is:

Tablet offline-first
-> semantic OutboxEvent
-> PC `/api/sync/ingest` or `/api/backoffice/sync/ingest`
-> validation
-> event ledger lifecycle on `OutboxEvent`
-> Prisma ORM projectors
-> canonical Prisma-governed database
-> Mobile `/api/mobile/snapshot`
-> Control audit and traceability

This is the normal future business path.

## Product Roles

Tablet operates and sells locally.
PC governs, validates, projects, reconciles, and classifies conflicts.
Mobile supervises through snapshot and view models only.
Control audits events, evidence, sync health, conflicts, and history.
Prisma ORM owns the canonical database model.
SQLite is the physical storage engine.

## TRI-DB Bridge Role

`F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma\tri_db_bridge.py` remains available only as:

- rescue
- backfill
- diagnostic
- migration support
- constraint inspection
- emergency projection
- self-test harness

It must not be described as the primary normal sync architecture.

Bridge `acked` is a compatibility marker only. It is not proof that PC validated, accepted, projected, and reconciled the event through governance.

## Route Compatibility

The following routes remain compatible:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\app\api\sync\ingest\route.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\app\api\backoffice\sync\ingest\route.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\app\api\sync\tri-db\run\route.ts`

The first two are primary event-ingest routes.
The TRI-DB route is operator-triggered rescue/backfill tooling.

## Normal Flow

1. Tablet completes the sale locally without calling PC.
2. Tablet writes local domain state and semantic outbox events.
3. PC later receives events through ingest.
4. PC validates envelope, schema version, idempotency, source, terminal, business, and payload.
5. PC stores the event ledger row with precise lifecycle timestamps.
6. PC runs a Prisma ORM projector inside a transaction.
7. PC marks the event as `reconciled`, `conflict`, `failed`, or `dead_letter`.
8. Mobile reads `/api/mobile/snapshot`.
9. Control surfaces status, diagnostics, and traceability.

## Forbidden As Normal Sync

Tablet DB
-> direct SQLite table copy
-> canonical DB

That path is allowed only through bridge tooling for the secondary roles listed above.

## Raw SQL Rule

Normal app business projection must use Prisma Client and Prisma transactions.
Raw SQL is allowed for migrations, SQLite-specific constraints, validation, diagnostics, bridge/rescue tools, and safe local schema preflight where Prisma has no equivalent.
