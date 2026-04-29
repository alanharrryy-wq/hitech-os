---
title: PRISMA Offline Grace Policy
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
scope: local-license-entitlements-mock
---

# PRISMA Offline Grace Policy

## 1. Proposito

Definir como debe comportarse PRISMA cuando no puede validar licencia remotamente.

## 2. Regla central

```text
Falla de internet no debe detener venta local basica inmediatamente.
```

## 3. Grace recomendado

| Plan | Grace sugerido |
|---|---|
| TABLET_SOLO | largo |
| TABLET_PRO | medio/largo |
| PC_BACKOFFICE | medio |
| TABLET_PC_MANAGED | medio, con alertas |

## 4. Durante grace

Permitido:

- venta local basica;
- tickets;
- stock local;
- exportacion;
- backups;
- soporte;
- lectura de historial.

Limitable:

- plugins premium nuevos;
- activaciones nuevas;
- updates premium;
- funciones multi-sucursal;
- cambios avanzados de permisos.

## 5. Fin de grace

Cuando vence grace:

- mostrar aviso claro;
- bloquear features premium;
- permitir exportar y respaldar;
- permitir soporte;
- no borrar datos.

## Guardrails operativos

- Esta capa es local-first: la ausencia de internet no debe convertir la caja en ladrillo caro.
- Esta capa no procesa pagos bancarios, no valida transferencias, no toma tarjetas y no custodia dinero.
- Una licencia puede habilitar o limitar funciones, pero no debe borrar datos del cliente.
- Cualquier suspension debe ser gradual, auditable y compatible con exportacion/respaldo.
- Los cambios de licencia deben escribirse como evento administrativo cuando exista event log operacional.
- El mock no es seguridad final: solo define contrato, rutas, estados y ejemplos para la siguiente implementacion.
- El flujo debe poder verificarse sin GitHub, sin red y sin depender del directorio actual.
- Si el grace offline toca permisos, plugins, ventas, soporte o datos, debe declarar feature key y razon de bloqueo.

## Reglas anti-caos

1. No leer licencias desde archivos commiteados.
2. No esconder features hardcodeadas en componentes UI.
3. No usar strings sueltos para planes si ya existe catalogo de plan.
4. No bloquear exportacion ni backup aunque el plan este suspendido.
5. No confundir licencia de producto con metodo de pago del ticket.
6. No meter Remote Ops como requisito para cerrar una venta local.
7. No aceptar comandos remotos arbitrarios como parte de refresco de licencia.
8. No instalar plugins solo por estar listados; deben venir por entitlement activo.
