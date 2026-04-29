---
title: PRISMA License Local Implementation Backlog
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
scope: local-license-entitlements-mock
---

# PRISMA License Local Implementation Backlog

## 1. Objetivo de la siguiente etapa

Crear una lectura local real, no invasiva, que determine si una feature esta habilitada.

## 2. Orden recomendado

### 02A. Loader read-only

- leer `license.json` desde ruta explicita;
- validar JSON;
- normalizar fechas;
- exponer status;
- no bloquear nada todavia.

### 02B. Feature resolver

- resolver plan;
- resolver entitlements;
- devolver `allowed/reason/source`;
- agregar tests.

### 02C. UI mock en PC

- ruta Mi Plan;
- mostrar license summary;
- mostrar features incluidas;
- mostrar plugins permitidos.

### 02D. UI ligera en Tablet

- estado de licencia;
- soporte;
- warning si grace;
- no popup comercial durante venta.

### 02E. Grace evaluator

- calcular offlineGraceUntil;
- alertas;
- razones de bloqueo.

### 02F. Remote refresh futuro

- placeholder para Remote Ops;
- polling seguro;
- no puertos entrantes;
- no comandos arbitrarios.

## 3. Tests minimos futuros

- licencia active permite feature;
- feature no incluida regresa falso;
- suspended bloquea premium;
- offline grace conserva venta local;
- expired permite export/backups;
- revoked no borra datos;
- JSON invalido no tira la app sin mensaje.

## Guardrails operativos

- Esta capa es local-first: la ausencia de internet no debe convertir la caja en ladrillo caro.
- Esta capa no procesa pagos bancarios, no valida transferencias, no toma tarjetas y no custodia dinero.
- Una licencia puede habilitar o limitar funciones, pero no debe borrar datos del cliente.
- Cualquier suspension debe ser gradual, auditable y compatible con exportacion/respaldo.
- Los cambios de licencia deben escribirse como evento administrativo cuando exista event log operacional.
- El mock no es seguridad final: solo define contrato, rutas, estados y ejemplos para la siguiente implementacion.
- El flujo debe poder verificarse sin GitHub, sin red y sin depender del directorio actual.
- Si el backlog de implementacion toca permisos, plugins, ventas, soporte o datos, debe declarar feature key y razon de bloqueo.

## Reglas anti-caos

1. No leer licencias desde archivos commiteados.
2. No esconder features hardcodeadas en componentes UI.
3. No usar strings sueltos para planes si ya existe catalogo de plan.
4. No bloquear exportacion ni backup aunque el plan este suspendido.
5. No confundir licencia de producto con metodo de pago del ticket.
6. No meter Remote Ops como requisito para cerrar una venta local.
7. No aceptar comandos remotos arbitrarios como parte de refresco de licencia.
8. No instalar plugins solo por estar listados; deben venir por entitlement activo.
