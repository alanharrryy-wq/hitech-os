---
title: PRISMA Runtime Failure Modes
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---


# PRISMA Runtime Failure Modes

Catalogo de fallos previsibles. El objetivo es que el producto falle como adulto responsable, no como impresora de oficina poseida.

## Falla 01: config faltante

**Accion correcta:** crear desde template o pedir instalador.

**Anti accion:** no inventar defaults silenciosos.

**Debe registrar:**

- timestamp;
- modo runtime;
- businessId;
- deviceId;
- ruta si aplica;
- codigo de error;
- accion sugerida;
- si requiere soporte.

## Falla 02: path relativo

**Accion correcta:** bloquear en modo cliente.

**Anti accion:** permitir solo fixture dev.

**Debe registrar:**

- timestamp;
- modo runtime;
- businessId;
- deviceId;
- ruta si aplica;
- codigo de error;
- accion sugerida;
- si requiere soporte.

## Falla 03: DB corrupta

**Accion correcta:** usar backup y soporte.

**Anti accion:** no sobrescribir.

**Debe registrar:**

- timestamp;
- modo runtime;
- businessId;
- deviceId;
- ruta si aplica;
- codigo de error;
- accion sugerida;
- si requiere soporte.

## Falla 04: licencia no validable

**Accion correcta:** activar grace.

**Anti accion:** no matar venta inmediata.

**Debe registrar:**

- timestamp;
- modo runtime;
- businessId;
- deviceId;
- ruta si aplica;
- codigo de error;
- accion sugerida;
- si requiere soporte.

## Falla 05: sync roto

**Accion correcta:** marcar outbox pendiente.

**Anti accion:** no perder eventos.

**Debe registrar:**

- timestamp;
- modo runtime;
- businessId;
- deviceId;
- ruta si aplica;
- codigo de error;
- accion sugerida;
- si requiere soporte.

## Falla 06: update interrumpido

**Accion correcta:** rollback.

**Anti accion:** no dejar version mixta.

**Debe registrar:**

- timestamp;
- modo runtime;
- businessId;
- deviceId;
- ruta si aplica;
- codigo de error;
- accion sugerida;
- si requiere soporte.

## Falla 07: plugin incompatible

**Accion correcta:** desactivar.

**Anti accion:** no cargar parcialmente.

**Debe registrar:**

- timestamp;
- modo runtime;
- businessId;
- deviceId;
- ruta si aplica;
- codigo de error;
- accion sugerida;
- si requiere soporte.

## Falla 08: support upload falla

**Accion correcta:** guardar bundle local.

**Anti accion:** no borrar evidencia.

**Debe registrar:**

- timestamp;
- modo runtime;
- businessId;
- deviceId;
- ruta si aplica;
- codigo de error;
- accion sugerida;
- si requiere soporte.

## Falla 09: disco lleno

**Accion correcta:** bloquear update/export grande.

**Anti accion:** no hacer migracion.

**Debe registrar:**

- timestamp;
- modo runtime;
- businessId;
- deviceId;
- ruta si aplica;
- codigo de error;
- accion sugerida;
- si requiere soporte.

## Falla 10: permisos insuficientes

**Accion correcta:** mensaje accionable.

**Anti accion:** no reintentar infinito.

**Debe registrar:**

- timestamp;
- modo runtime;
- businessId;
- deviceId;
- ruta si aplica;
- codigo de error;
- accion sugerida;
- si requiere soporte.
