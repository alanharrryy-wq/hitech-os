# Demo Script

## 1. Tablet Standalone Core

Start Tablet with the existing operator runner, not a raw framework server.

Expected story:

- Open Tablet POS.
- Show catalog/POS route.
- Complete or smoke a sale using the local Tablet engine.
- Confirm local inventory movement.
- Confirm outbox remains local and pending when sync is not available.
- Show shift/cash route smoke expectations.

Automated proof:

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system run verify:round2
```

The `tablet-standalone-sale-core` step proves sale, stock decrement, outbox, idempotency, and `pcRequiredForBasicSale: false`.

## 2. PC Adder

PC is a backoffice/control-tower adder. It is not POS and is not required for Tablet sale/checkout/cash/inventory/outbox.

Automated proof:

`pc-backoffice-route-adder` in `verify:round2` checks PC source routes for dashboard, catalog, stock, counts, purchasing, receiving, replenishment, audit, sync, and settings.

## 3. Mobile Supervisor

Mobile is a supervisor adder. It does not operate the Tablet POS core.

Automated proof:

`mobile-supervisor-release-boundary` in `verify:round2` checks the light Dashboard and Premium Navigator ownership of long supervisor surfaces.

## 4. Evidence

Use:

`F:\repos\hitech-os\apps\terminal-de-venta-system\tools\codex\runs\prisma-round2-productization\round2_smoke_results.json`

