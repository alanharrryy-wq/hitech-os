# Prisma Canonical Status

Status: PROMOTED

As of 2026-04-25, Prisma is the single canonical database foundation for Terminal de Venta System.

## Canonical Surface

Canonical schema, migrations, seed source, and verification live under:

F:\repos\hitech-os\apps\terminal-de-venta-system\prisma

The canonical runtime database for local development is outside source trees:

F:\repos\hitech-os\tools\_local\data\terminal-de-venta-system\canonical.db

## Deprecated Transitional Surfaces

These files are intentionally retained as validator-compatible stubs only:

F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\prisma\schema.prisma
F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\prisma\schema.prisma

No models may be added there. Prisma Client generation copies the canonical schema into ignored `node_modules\.cache\hitech-prisma-canonical` folders per app.

## Runtime Flows Now Backed By Prisma

- PC catalog, barcode health, critical stock, purchasing, receiving, replenishment, outbox, and dashboard routes.
- Tablet sales, shift/cash session, returns, stock, sync, and dashboard routes.
- Repository reads use Product, Barcode, StockSnapshot, ReplenishmentSignal, PurchaseOrder, GoodsReceipt, Sale, SaleReturn, CashSession, and OutboxEvent from the canonical schema.

## Guardrails Enforced

- One default PriceList per business.
- One default TaxRate per business.
- One OPEN CashSession per business and terminal.
- Barcode ownership must match Product ownership through a composite foreign key.
- PurchaseOrder and GoodsReceipt totals are guarded by line-total triggers and validation.

## Verification

Canonical validation command:

```powershell
python F:\repos\hitech-os\apps\terminal-de-venta-system\tooling\scripts\validate_prisma_canonical.py --out F:\repos\hitech-os\tools\_local\evidence\terminal-de-venta-prisma-canonical-validation.json
```

Latest evidence:

F:\repos\hitech-os\tools\_local\evidence\terminal-de-venta-prisma-canonical-validation.json

Latest result: PASS
