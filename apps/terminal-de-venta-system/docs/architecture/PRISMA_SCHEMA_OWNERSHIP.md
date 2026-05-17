# Prisma Schema Ownership

Estado: canon listo para codigo.
Idioma operativo: es-MX.
Alcance: contratos, arquitectura y criterios de implementacion; no implementa motores finales.

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

## Proposito

Define que Prisma ayuda a ordenar datos, pero no sustituye arquitectura ni contratos.


## General rule

Prisma ORM helps keep data clear, but does not replace architecture or contracts.

## Allowed schemas

### 1. Root / Backoffice canonical schema

Used for PC/backoffice, consolidation, advanced inventory, purchases, receiving, audit, and sync.

### 2. Tablet local schema

Allowed for standalone POS. Must cover only minimum local operation: `Business`, `Terminal`, `Product`, `Barcode`, `Sale`, `SaleLine`, `StockMovement`, `OutboxEvent`, `CashSession`.

Operator UI may still say "shift" or "turno", but the canonical data model name is `CashSession`.

### 3. PC local build schema

`F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\prisma\schema.prisma` is a build-local non-canonical copy only.

The source of truth remains:

`F:\repos\hitech-os\apps\terminal-de-venta-system\prisma\schema.prisma`

If PC needs local Prisma Client generation, refresh the PC copy from the root schema and keep the non-canonical header.

## Round 2 additive schema contract

PRISMA Commerce Round 2 adds these models additively to the root and Tablet schemas:

- `Brand`
- `ProductSupplier`
- `DropdownCatalog`
- `DropdownOption`
- `SalePaymentTender`
- `SaleReturnLine`
- `CashAdjustment`
- `User`
- `Role`
- `Permission`
- `AuditEvent`
- `SupportIncident`

Brand/provider storage must stay relational:

- `Product.brandId -> Brand.id`
- `ProductSupplier.productId -> Product.id`
- `ProductSupplier.supplierId -> Supplier.id`
- `ProductSupplier.isPrimary` marks primary supplier.

Do not reintroduce freeform brand/provider strings on `Product`.

## Tablet schema must not

- copy the full core without contract
- include advanced purchasing
- include advanced receiving
- include executive dashboard ownership
- include fiscal complexity unless explicitly contracted
- include deep vertical plugins
- depend on central DB to sell

## Every schema change must answer

- what module uses it
- what screen shows it
- what event affects it
- what permission protects it
- what happens offline
- what report consumes it
- what plugin needs it

## Every structural change must have

- migration
- review
- backup
- validation
- rollback
- documentation

## Important nuance

If current Tablet schema is broader than the minimum model, do not delete it blindly. Classify it as transitional local schema if needed. Document the gap and mark future cleanup criteria. Do not break current working code.
