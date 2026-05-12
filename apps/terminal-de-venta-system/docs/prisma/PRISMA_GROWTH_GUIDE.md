# PRISMA Growth Guide

Run timestamp: 2026-05-11T01:55:09.6153907-06:00

## How To Add A New PRISMA Event

1. Add the event type to:
   `F:\repos\hitech-os\apps\terminal-de-venta-system\shared\contracts\sync-event-contract.v1.json`
2. Add the exported topic constant to:
   `F:\repos\hitech-os\apps\terminal-de-venta-system\shared\twin-kernel\src\sync\events.ts`
3. Add Tablet producer support only if Tablet owns the operation:
   `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\src\server\pos-engine\event-factory.ts`
4. Add PC validation support:
   `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\src\server\validators\sync-event-contract.ts`
5. Add a Prisma projector:
   `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\src\server\services\sync-projectors.service.ts`
6. Add canonical model fields in:
   `F:\repos\hitech-os\apps\terminal-de-venta-system\prisma\schema.prisma`
7. Create a forward-only migration under:
   `F:\repos\hitech-os\apps\terminal-de-venta-system\prisma\migrations`
8. Surface read-only supervision through:
   `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\app\api\mobile\snapshot\route.ts`
9. Add chart/alert/view model changes in:
   `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\lib\prisma-app\mobile-intelligence`
10. Add Control/audit trace fields without making Control a mutating business owner.

## Rules For New Modules

- Do not make Mobile a writer of business records.
- Do not make PC a POS.
- Do not make Tablet depend on PC to complete a sale.
- Do not duplicate business rules in React components.
- Do not add raw SQL to app business logic unless no Prisma-safe alternative exists and the exception is documented.
- Do not use Excel, CSV, XLSX, Access, or manual files as canonical truth.
- Keep bridge scripts as rescue/backfill/diagnostic tooling.

## Required Event Envelope

Every new event should include:

- `eventId`
- `eventType`
- `schemaVersion`
- `idempotencyKey`
- `terminalId`
- `businessId`
- `payload`
- `occurredAt`
- `source`
- `correlationId` when linking related records

## Required Lifecycle Handling

Use the canonical lifecycle:

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

Do not invent ambiguous states. If compatibility wording must remain, map it explicitly.

## Required Tests

For each new event/module, add or update deterministic validation for:

- Tablet event creation when Tablet is the producer.
- PC validation acceptance and rejection.
- PC projector idempotency.
- Conflict classification.
- Prisma schema/migration validity.
- Mobile snapshot/view model read behavior.
- Control/audit traceability.

No Playwright or screenshots are required for architecture validation.

