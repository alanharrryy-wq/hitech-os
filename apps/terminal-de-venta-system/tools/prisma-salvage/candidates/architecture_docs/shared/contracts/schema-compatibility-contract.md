# Shared Schema Compatibility Contract

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

Allowed for standalone POS. Must cover only minimum local operation: `Business`, `Terminal`, `Product`, `Barcode`, `Sale`, `SaleLine`, `StockMovement`, `OutboxEvent`, `Shift`.

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
