---
title: PRISMA License Local Mock Index
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
scope: local-license-entitlements-mock
---

# PRISMA License Local Mock 02 - Índice corregido

## Archivos principales

| Archivo | Rol |
|---|---|
| PRISMA_LICENSE_LOCAL_MOCK_02.md | decisión madre |
| PRISMA_LICENSE_STATE_MACHINE.md | estados y transiciones |
| PRISMA_PLAN_CATALOG_CONTRACT.md | planes y capacidades |
| PRISMA_FEATURE_KEYS_CATALOG.md | vocabulario estable de features |
| PRISMA_ENTITLEMENTS_CONTRACT.md | autorizaciones concretas |
| PRISMA_LOCAL_LICENSE_STORE_CONTRACT.md | rutas y store local |
| PRISMA_LICENSE_UI_POLICY.md | reglas de UI Tablet/PC |
| PRISMA_OFFLINE_GRACE_POLICY.md | continuidad sin internet |
| PRISMA_LICENSE_NO_PAYMENT_PROCESSING_ADDENDUM.md | frontera anti pagos bancarios |
| PRISMA_LICENSE_OPERATION_MATRIX.md | matriz de operación por estado |
| PRISMA_LICENSE_AUDIT_EVENT_CATALOG.md | eventos esperados de licencia |
| PRISMA_FEATURE_GATE_ATLAS.md | mapa de gates por superficie |
| PRISMA_LICENSE_LOCAL_IMPLEMENTATION_BACKLOG.md | siguiente implementación |

## Decision notes corregidas

| Nota | Decisión |
|---|---|
| PRISMA_LICENSE_LOCAL_MOCK_02_DECISION_NOTE_01.md | state machine |
| PRISMA_LICENSE_LOCAL_MOCK_02_DECISION_NOTE_02.md | feature resolution |
| PRISMA_LICENSE_LOCAL_MOCK_02_DECISION_NOTE_03.md | plan catalog |
| PRISMA_LICENSE_LOCAL_MOCK_02_DECISION_NOTE_04.md | offline grace |
| PRISMA_LICENSE_LOCAL_MOCK_02_DECISION_NOTE_05.md | UI policy |
| PRISMA_LICENSE_LOCAL_MOCK_02_DECISION_NOTE_06.md | no payment boundary |
| PRISMA_LICENSE_LOCAL_MOCK_02_DECISION_NOTE_07.md | audit events |
| PRISMA_LICENSE_LOCAL_MOCK_02_DECISION_NOTE_08.md | runtime handoff |

## Reglas de lectura

Este paquete debe leerse junto con:

- `PRISMA_CUSTOMER_OPERATIONS_LAYER.md`;
- `PRISMA_RUNTIME_CONFIG_BOUNDARY_01.md`;
- `PRISMA_NO_PAYMENT_PROCESSING_BOUNDARY.md`;
- `PRISMA_PLUGIN_CATALOG_CONTRACT.md`.

## Guardrails operativos

- Esta capa es local-first: la ausencia de internet no debe convertir la caja en ladrillo caro.
- Esta capa no procesa pagos bancarios, no valida transferencias, no toma tarjetas y no custodia dinero.
- Una licencia puede habilitar o limitar funciones, pero no debe borrar datos del cliente.
- Cualquier suspensión debe ser gradual, auditable y compatible con exportación/respaldo.
- Los cambios de licencia deben escribirse como evento administrativo cuando exista event log operacional.
- El mock no es seguridad final: define contrato, rutas, estados y ejemplos para la siguiente implementación.
- El flujo debe poder verificarse sin GitHub, sin red y sin depender del directorio actual.
