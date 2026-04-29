---
title: PRISMA Customer Operations Acceptance Matrix
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---

# PRISMA Customer Operations Acceptance Matrix

## Área: licencia

| Caso | Dado | Cuando | Entonces | Evidencia |
|---|---|---|---|---|
| licencia-01 | cliente activo | abre Centro PRISMA | ve estado claro | screenshot o smoke |
| licencia-02 | sin internet | intenta operar local | no bloquea venta básica | smoke offline |
| licencia-03 | config inválida | corre verify | falla con mensaje útil | log único |
| licencia-04 | acción sensible | se ejecuta | queda auditada | audit log |
| licencia-05 | usuario sin rol | intenta acceder | queda bloqueado | UI state |
| licencia-06 | paquete corrupto | se aplica | se rechaza | checksum |
| licencia-07 | rollback requerido | falla verify | restaura backup | rollback log |
| licencia-08 | datos sensibles | genera diagnóstico | son excluidos | manifest bundle |

Regla de salida para licencia: no puede pasar a implementación si no tiene verify, rollback y límite explícito.

## Área: entitlements

| Caso | Dado | Cuando | Entonces | Evidencia |
|---|---|---|---|---|
| entitlements-01 | cliente activo | abre Centro PRISMA | ve estado claro | screenshot o smoke |
| entitlements-02 | sin internet | intenta operar local | no bloquea venta básica | smoke offline |
| entitlements-03 | config inválida | corre verify | falla con mensaje útil | log único |
| entitlements-04 | acción sensible | se ejecuta | queda auditada | audit log |
| entitlements-05 | usuario sin rol | intenta acceder | queda bloqueado | UI state |
| entitlements-06 | paquete corrupto | se aplica | se rechaza | checksum |
| entitlements-07 | rollback requerido | falla verify | restaura backup | rollback log |
| entitlements-08 | datos sensibles | genera diagnóstico | son excluidos | manifest bundle |

Regla de salida para entitlements: no puede pasar a implementación si no tiene verify, rollback y límite explícito.

## Área: mensajes

| Caso | Dado | Cuando | Entonces | Evidencia |
|---|---|---|---|---|
| mensajes-01 | cliente activo | abre Centro PRISMA | ve estado claro | screenshot o smoke |
| mensajes-02 | sin internet | intenta operar local | no bloquea venta básica | smoke offline |
| mensajes-03 | config inválida | corre verify | falla con mensaje útil | log único |
| mensajes-04 | acción sensible | se ejecuta | queda auditada | audit log |
| mensajes-05 | usuario sin rol | intenta acceder | queda bloqueado | UI state |
| mensajes-06 | paquete corrupto | se aplica | se rechaza | checksum |
| mensajes-07 | rollback requerido | falla verify | restaura backup | rollback log |
| mensajes-08 | datos sensibles | genera diagnóstico | son excluidos | manifest bundle |

Regla de salida para mensajes: no puede pasar a implementación si no tiene verify, rollback y límite explícito.

## Área: announcements

| Caso | Dado | Cuando | Entonces | Evidencia |
|---|---|---|---|---|
| announcements-01 | cliente activo | abre Centro PRISMA | ve estado claro | screenshot o smoke |
| announcements-02 | sin internet | intenta operar local | no bloquea venta básica | smoke offline |
| announcements-03 | config inválida | corre verify | falla con mensaje útil | log único |
| announcements-04 | acción sensible | se ejecuta | queda auditada | audit log |
| announcements-05 | usuario sin rol | intenta acceder | queda bloqueado | UI state |
| announcements-06 | paquete corrupto | se aplica | se rechaza | checksum |
| announcements-07 | rollback requerido | falla verify | restaura backup | rollback log |
| announcements-08 | datos sensibles | genera diagnóstico | son excluidos | manifest bundle |

Regla de salida para announcements: no puede pasar a implementación si no tiene verify, rollback y límite explícito.

## Área: plugins

| Caso | Dado | Cuando | Entonces | Evidencia |
|---|---|---|---|---|
| plugins-01 | cliente activo | abre Centro PRISMA | ve estado claro | screenshot o smoke |
| plugins-02 | sin internet | intenta operar local | no bloquea venta básica | smoke offline |
| plugins-03 | config inválida | corre verify | falla con mensaje útil | log único |
| plugins-04 | acción sensible | se ejecuta | queda auditada | audit log |
| plugins-05 | usuario sin rol | intenta acceder | queda bloqueado | UI state |
| plugins-06 | paquete corrupto | se aplica | se rechaza | checksum |
| plugins-07 | rollback requerido | falla verify | restaura backup | rollback log |
| plugins-08 | datos sensibles | genera diagnóstico | son excluidos | manifest bundle |

Regla de salida para plugins: no puede pasar a implementación si no tiene verify, rollback y límite explícito.

## Área: diagnostics

| Caso | Dado | Cuando | Entonces | Evidencia |
|---|---|---|---|---|
| diagnostics-01 | cliente activo | abre Centro PRISMA | ve estado claro | screenshot o smoke |
| diagnostics-02 | sin internet | intenta operar local | no bloquea venta básica | smoke offline |
| diagnostics-03 | config inválida | corre verify | falla con mensaje útil | log único |
| diagnostics-04 | acción sensible | se ejecuta | queda auditada | audit log |
| diagnostics-05 | usuario sin rol | intenta acceder | queda bloqueado | UI state |
| diagnostics-06 | paquete corrupto | se aplica | se rechaza | checksum |
| diagnostics-07 | rollback requerido | falla verify | restaura backup | rollback log |
| diagnostics-08 | datos sensibles | genera diagnóstico | son excluidos | manifest bundle |

Regla de salida para diagnostics: no puede pasar a implementación si no tiene verify, rollback y límite explícito.

## Área: updates

| Caso | Dado | Cuando | Entonces | Evidencia |
|---|---|---|---|---|
| updates-01 | cliente activo | abre Centro PRISMA | ve estado claro | screenshot o smoke |
| updates-02 | sin internet | intenta operar local | no bloquea venta básica | smoke offline |
| updates-03 | config inválida | corre verify | falla con mensaje útil | log único |
| updates-04 | acción sensible | se ejecuta | queda auditada | audit log |
| updates-05 | usuario sin rol | intenta acceder | queda bloqueado | UI state |
| updates-06 | paquete corrupto | se aplica | se rechaza | checksum |
| updates-07 | rollback requerido | falla verify | restaura backup | rollback log |
| updates-08 | datos sensibles | genera diagnóstico | son excluidos | manifest bundle |

Regla de salida para updates: no puede pasar a implementación si no tiene verify, rollback y límite explícito.

## Área: remote_commands

| Caso | Dado | Cuando | Entonces | Evidencia |
|---|---|---|---|---|
| remote_commands-01 | cliente activo | abre Centro PRISMA | ve estado claro | screenshot o smoke |
| remote_commands-02 | sin internet | intenta operar local | no bloquea venta básica | smoke offline |
| remote_commands-03 | config inválida | corre verify | falla con mensaje útil | log único |
| remote_commands-04 | acción sensible | se ejecuta | queda auditada | audit log |
| remote_commands-05 | usuario sin rol | intenta acceder | queda bloqueado | UI state |
| remote_commands-06 | paquete corrupto | se aplica | se rechaza | checksum |
| remote_commands-07 | rollback requerido | falla verify | restaura backup | rollback log |
| remote_commands-08 | datos sensibles | genera diagnóstico | son excluidos | manifest bundle |

Regla de salida para remote_commands: no puede pasar a implementación si no tiene verify, rollback y límite explícito.

## Área: ai_ready

| Caso | Dado | Cuando | Entonces | Evidencia |
|---|---|---|---|---|
| ai_ready-01 | cliente activo | abre Centro PRISMA | ve estado claro | screenshot o smoke |
| ai_ready-02 | sin internet | intenta operar local | no bloquea venta básica | smoke offline |
| ai_ready-03 | config inválida | corre verify | falla con mensaje útil | log único |
| ai_ready-04 | acción sensible | se ejecuta | queda auditada | audit log |
| ai_ready-05 | usuario sin rol | intenta acceder | queda bloqueado | UI state |
| ai_ready-06 | paquete corrupto | se aplica | se rechaza | checksum |
| ai_ready-07 | rollback requerido | falla verify | restaura backup | rollback log |
| ai_ready-08 | datos sensibles | genera diagnóstico | son excluidos | manifest bundle |

Regla de salida para ai_ready: no puede pasar a implementación si no tiene verify, rollback y límite explícito.

## Área: no_payments

| Caso | Dado | Cuando | Entonces | Evidencia |
|---|---|---|---|---|
| no_payments-01 | cliente activo | abre Centro PRISMA | ve estado claro | screenshot o smoke |
| no_payments-02 | sin internet | intenta operar local | no bloquea venta básica | smoke offline |
| no_payments-03 | config inválida | corre verify | falla con mensaje útil | log único |
| no_payments-04 | acción sensible | se ejecuta | queda auditada | audit log |
| no_payments-05 | usuario sin rol | intenta acceder | queda bloqueado | UI state |
| no_payments-06 | paquete corrupto | se aplica | se rechaza | checksum |
| no_payments-07 | rollback requerido | falla verify | restaura backup | rollback log |
| no_payments-08 | datos sensibles | genera diagnóstico | son excluidos | manifest bundle |

Regla de salida para no_payments: no puede pasar a implementación si no tiene verify, rollback y límite explícito.

