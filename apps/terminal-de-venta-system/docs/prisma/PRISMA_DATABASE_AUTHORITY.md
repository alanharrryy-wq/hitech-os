# PRISMA Database Authority

Status: canonical database authority decision.
Scope: apps/terminal-de-venta-system.

## Authority

Prisma ORM is the model authority for the canonical database:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\prisma\schema.prisma`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\prisma\migrations`
- Prisma Client usage in PC projectors and canonical readers

SQLite is the physical storage engine. It is not the business architecture.

## Canonical Database

Default PC canonical DB path:

`F:\repos\hitech-os\tools\_local\data\terminal-de-venta-system\canonical.db`

PC resolves this through:

`F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\src\server\prisma\client.ts`

## Tablet Local Database

Tablet local DB path:

`F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\data\tablet-pos.db`

Tablet local SQLite is allowed for offline POS autonomy. It is not a direct-copy source of canonical truth for the normal future sync path.

## Models In Scope

Domain models touched by this architecture:

- `Business`
- `Store`
- `Terminal`
- `Product`
- `Sale`
- `SaleLine`
- `StockMovement`
- `CashSession`
- `CashMovement`
- `ReplenishmentSignal`
- `OutboxEvent`

## Event Ledger

`OutboxEvent` is the compatibility ledger table and now carries lifecycle/governance fields:

- `eventType`
- `idempotencyKey`
- `correlationId`
- `terminalId`
- `source`
- `schemaVersion`
- `lifecycleStatus`
- `receivedAt`
- `validatedAt`
- `acceptedAt`
- `projectedAt`
- `reconciledAt`
- `failedAt`
- `deadLetterAt`
- `conflictCode`
- `diagnosticsJson`

Migration:

`F:\repos\hitech-os\apps\terminal-de-venta-system\prisma\migrations\20260511000000_event_ledger_lifecycle\migration.sql`

## Critical Constraints

`CashSession` has a SQLite partial unique index:

`CashSession(businessId, terminalId) WHERE status = 'OPEN'`

This index enforces one open cash session per terminal but must not be used as a normal SQLite `ON CONFLICT` UPSERT target.

PC projectors check for an existing open session first, then create using Prisma Client.
The TRI-DB bridge filters partial unique indexes out of UPSERT conflict-target selection.

## Raw SQL Exceptions

Allowed:

- Prisma migrations
- SQLite-specific partial indexes and triggers
- safe local preflight/diagnostic scripts
- validation tools
- TRI-DB rescue/backfill/diagnostic bridge

Not allowed:

- normal app business projection
- React components
- Mobile snapshot business rules
- direct table-copy sync as future primary architecture

## Spreadsheet / Access Authority

Excel, CSV, XLSX, Access, `.mdb`, `.accdb`, manual sheets, pandas, and openpyxl outputs are child/support artifacts only.

They must never become source of truth and must never override Prisma-governed canonical state silently.
