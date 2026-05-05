---
title: PRISMA Runtime Config Validation Playbook
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---


# PRISMA Runtime Config Validation Playbook

Playbook para validar que PRISMA ya no viva pegado al repo como estampita en refrigerador. Cada caso define entrada, decision y evidencia esperada.

## Caso 01: runtimeRoot apunta al repo

**Decision esperada:** bloquear modo cliente.

**Codigo esperado:** `RUNTIME_ROOT_POINTS_TO_REPO`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 02: businessId vacio

**Decision esperada:** bloquear arranque.

**Codigo esperado:** `BUSINESS_ID_MISSING`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 03: deviceId cambia en cada boot

**Decision esperada:** advertir y bloquear registro remoto.

**Codigo esperado:** `DEVICE_ID_UNSTABLE`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 04: Tablet Solo sin internet

**Decision esperada:** permitir venta local.

**Codigo esperado:** `OFFLINE_ALLOWED`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 05: Managed sin PC disponible

**Decision esperada:** permitir venta Tablet y marcar degraded.

**Codigo esperado:** `DEGRADED_MANAGED`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 06: license vencida pero grace vigente

**Decision esperada:** permitir funciones base y avisar.

**Codigo esperado:** `LICENSE_OFFLINE_GRACE`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 07: license suspendida

**Decision esperada:** limitar premium, permitir export y backup.

**Codigo esperado:** `LICENSE_SUSPENDED`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 08: DB cliente dentro del repo

**Decision esperada:** bloquear verify cliente.

**Codigo esperado:** `CUSTOMER_DB_IN_REPO`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 09: logs no escribibles

**Decision esperada:** bloquear modo customer.

**Codigo esperado:** `LOGS_NOT_WRITABLE`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 10: backupRoot no escribible antes de update

**Decision esperada:** bloquear update.

**Codigo esperado:** `BACKUP_NOT_WRITABLE`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 11: plugin sin manifest

**Decision esperada:** bloquear instalacion plugin.

**Codigo esperado:** `PLUGIN_MANIFEST_MISSING`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 12: plugin pide permiso no declarado

**Decision esperada:** bloquear activacion.

**Codigo esperado:** `PLUGIN_PERMISSION_INVALID`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 13: update sin checksum

**Decision esperada:** bloquear update.

**Codigo esperado:** `UPDATE_CHECKSUM_MISSING`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 14: update falla verify

**Decision esperada:** rollback automatico.

**Codigo esperado:** `UPDATE_VERIFY_FAILED`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 15: support bundle con token visible

**Decision esperada:** bloquear envio.

**Codigo esperado:** `DIAGNOSTIC_SECRET_LEAK`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 16: announcement comercial durante checkout

**Decision esperada:** no mostrar modal.

**Codigo esperado:** `ANNOUNCEMENT_BLOCKED_DURING_CHECKOUT`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 17: Remote Ops caido

**Decision esperada:** continuar local.

**Codigo esperado:** `REMOTE_OPS_UNAVAILABLE`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 18: cwd distinto al repo

**Decision esperada:** no afectar resolucion.

**Codigo esperado:** `CWD_IGNORED`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 19: ProgramData no existe

**Decision esperada:** crear en instalacion.

**Codigo esperado:** `RUNTIME_ROOT_CREATED`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Caso 20: ruta relativa en modo cliente

**Decision esperada:** bloquear.

**Codigo esperado:** `RELATIVE_PATH_NOT_ALLOWED`.

**Evidencia minima:**

- linea en log;
- resultado ready/blocked;
- ruta o campo involucrado;
- accion sugerida para humano;
- no modificar DB durante validacion.

**Notas:**

Este caso debe poder probarse con fixture o config temporal. No debe requerir GitHub, internet ni app viva.

## Politica de severidad

| Severidad | Significado | Accion |
|---|---|---|
| info | dato util | continuar |
| warning | riesgo no bloqueante | continuar con aviso |
| blocked | contrato roto | detener |
| rollback | fallo despues de apply | restaurar |
