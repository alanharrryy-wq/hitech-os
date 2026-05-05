---
title: PRISMA License No Payment Processing Addendum
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
scope: local-license-entitlements-mock
---

# PRISMA License No Payment Processing Addendum

## 1. Decision

La capa de licencia no procesa pagos bancarios.

## 2. Prohibido

- cobrar dentro de PRISMA;
- recibir tarjeta;
- iniciar transferencia;
- validar SPEI;
- almacenar datos bancarios;
- conciliar bancos automaticamente;
- liquidar pagos;
- custodiar dinero;
- emitir autorizaciones bancarias.

## 3. Permitido

- mostrar plan actual;
- mostrar funciones disponibles;
- permitir solicitar activacion;
- abrir ticket comercial;
- marcar estado administrativo externo;
- activar entitlement despues de gestion externa.

## 4. Lenguaje UI sugerido

```text
Solicitar activacion
Contactar soporte
Pedir informacion
Funcion no incluida en tu plan
```

Evitar:

```text
Pagar ahora
Ingresar tarjeta
Transferir desde PRISMA
Confirmar pago bancario
```

## 5. Razon tecnica

Mantener la frontera evita que el POS local se convierta en procesador financiero. PRISMA registra operacion; no mueve dinero bancario.

## Guardrails operativos

- Esta capa es local-first: la ausencia de internet no debe convertir la caja en ladrillo caro.
- Esta capa no procesa pagos bancarios, no valida transferencias, no toma tarjetas y no custodia dinero.
- Una licencia puede habilitar o limitar funciones, pero no debe borrar datos del cliente.
- Cualquier suspension debe ser gradual, auditable y compatible con exportacion/respaldo.
- Los cambios de licencia deben escribirse como evento administrativo cuando exista event log operacional.
- El mock no es seguridad final: solo define contrato, rutas, estados y ejemplos para la siguiente implementacion.
- El flujo debe poder verificarse sin GitHub, sin red y sin depender del directorio actual.
- Si la frontera de no pagos toca permisos, plugins, ventas, soporte o datos, debe declarar feature key y razon de bloqueo.

## Reglas anti-caos

1. No leer licencias desde archivos commiteados.
2. No esconder features hardcodeadas en componentes UI.
3. No usar strings sueltos para planes si ya existe catalogo de plan.
4. No bloquear exportacion ni backup aunque el plan este suspendido.
5. No confundir licencia de producto con metodo de pago del ticket.
6. No meter Remote Ops como requisito para cerrar una venta local.
7. No aceptar comandos remotos arbitrarios como parte de refresco de licencia.
8. No instalar plugins solo por estar listados; deben venir por entitlement activo.
