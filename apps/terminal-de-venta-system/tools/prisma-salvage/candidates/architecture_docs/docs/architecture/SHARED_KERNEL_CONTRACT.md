# Shared Kernel Contract

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

Evita que la capa compartida se convierta en utileria generica y la fija como contrato.


Shared Kernel is not a utility folder. Shared Kernel is contract.

## Puede contener

- real shared types
- event names
- sync contracts
- screen contracts
- plugin contracts
- shared glossary
- compatibility rules

## Must not contain

- local Tablet helpers
- local PC helpers
- specific UI
- specific queries
- backoffice logic
- touch POS logic
- temporary patches

## Sensitive zones

- `packages/shared-kernel/*`
- `shared/TWIN_CHAT_SHARED_CONTEXT_6.1.json`
- `shared/contracts/*`
- visible equivalent labels
- shared event names
- sync contracts

## Twin change rule

If shared identity, shared naming, shared events, or sync contract changes, it is a twin change. If only local Tablet or PC operation improves, it is local.
