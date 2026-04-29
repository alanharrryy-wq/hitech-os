---
title: PRISMA Local License Store Contract
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
scope: local-license-entitlements-mock
---

# PRISMA Local License Store Contract

## 1. Proposito

Definir donde vive la licencia local del cliente.

## 2. Ruta cliente recomendada

```text
C:\ProgramData\PRISMA\config\license.json
```

Para negocio especifico:

```text
C:\ProgramData\PRISMA\businesses\<businessId>\config\license.json
```

## 3. Ruta dev permitida

Durante desarrollo se pueden usar ejemplos bajo:

```text
apps\terminal-de-venta-system\tooling\productization\examples\license-local\
```

Pero esos ejemplos no son licencia real y no deben empaquetarse como secretos.

## 4. Precedencia futura

1. parametro explicito de arranque;
2. runtime config;
3. `PRISMA_LICENSE_FILE`;
4. ruta ProgramData;
5. ejemplo dev solo en modo dev.

## 5. Escritura

La app no debe reescribir la licencia arbitrariamente. Cambios futuros deben venir de:

- activacion local controlada;
- refresh remoto;
- instalador;
- herramienta de soporte autorizada.

## 6. Seguridad futura

La firma futura debe validar:

- payload canonico;
- businessId;
- deviceId o allowedDevices;
- plan;
- expiracion;
- features/plugins;
- version de llave publica.

## Guardrails operativos

- Esta capa es local-first: la ausencia de internet no debe convertir la caja en ladrillo caro.
- Esta capa no procesa pagos bancarios, no valida transferencias, no toma tarjetas y no custodia dinero.
- Una licencia puede habilitar o limitar funciones, pero no debe borrar datos del cliente.
- Cualquier suspension debe ser gradual, auditable y compatible con exportacion/respaldo.
- Los cambios de licencia deben escribirse como evento administrativo cuando exista event log operacional.
- El mock no es seguridad final: solo define contrato, rutas, estados y ejemplos para la siguiente implementacion.
- El flujo debe poder verificarse sin GitHub, sin red y sin depender del directorio actual.
- Si el local license store toca permisos, plugins, ventas, soporte o datos, debe declarar feature key y razon de bloqueo.

## Reglas anti-caos

1. No leer licencias desde archivos commiteados.
2. No esconder features hardcodeadas en componentes UI.
3. No usar strings sueltos para planes si ya existe catalogo de plan.
4. No bloquear exportacion ni backup aunque el plan este suspendido.
5. No confundir licencia de producto con metodo de pago del ticket.
6. No meter Remote Ops como requisito para cerrar una venta local.
7. No aceptar comandos remotos arbitrarios como parte de refresco de licencia.
8. No instalar plugins solo por estar listados; deben venir por entitlement activo.
