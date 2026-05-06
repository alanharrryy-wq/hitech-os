---
title: PRISMA Feature Keys Catalog
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
scope: local-license-entitlements-mock
---

# PRISMA Feature Keys Catalog

## 1. Proposito

Crear un vocabulario tecnico estable para features. Sin esto, la UI termina preguntando `isPro`, `hasPlus`, `canDoMagic` y otras tragedias de barrio con TypeScript.

## 2. Convencion

```text
dominio.modulo.accion
```

Ejemplos:

```text
pos.sales.complete
pos.returns.create
inventory.local.adjust
dashboard.kpis
sync.managed
plugin.remote.activate
support.remote
ai.support.readonly.future
```

## 3. Dominios permitidos iniciales

- `pos`
- `inventory`
- `catalog`
- `shift`
- `report`
- `export`
- `backup`
- `sync`
- `dashboard`
- `support`
- `license`
- `plugin`
- `announcement`
- `message`
- `ai`

## 4. Reglas

- Una feature key debe ser estable.
- No usar labels visibles como keys.
- No meter precios en keys.
- No usar keys por cliente.
- No usar nombres de botones como contrato.
- Las features futuras de IA deben iniciar como read-only.

## 5. Feature keys iniciales

```text
pos.sales.complete
pos.ticket.local
pos.sale.cancel
pos.returns.create
inventory.local.decrement
inventory.local.adjust
report.today.basic
export.local.basic
export.local.advanced
event.outbox.view
shift.open
shift.close
backup.local.scheduled
catalog.write
inventory.backoffice.view
inventory.backoffice.adjust
purchase.write
receiving.write
audit.view
dashboard.kpis
sync.ingest
sync.managed
sync.conflict.resolve
catalog.snapshot.publish
support.basic
support.advanced
support.remote
license.local.read
license.remote.refresh
plugin.local.enable
plugin.remote.activate
announcement.view
message.customer.channel
ai.support.readonly.future
```

## Guardrails operativos

- Esta capa es local-first: la ausencia de internet no debe convertir la caja en ladrillo caro.
- Esta capa no procesa pagos bancarios, no valida transferencias, no toma tarjetas y no custodia dinero.
- Una licencia puede habilitar o limitar funciones, pero no debe borrar datos del cliente.
- Cualquier suspension debe ser gradual, auditable y compatible con exportacion/respaldo.
- Los cambios de licencia deben escribirse como evento administrativo cuando exista event log operacional.
- El mock no es seguridad final: solo define contrato, rutas, estados y ejemplos para la siguiente implementacion.
- El flujo debe poder verificarse sin GitHub, sin red y sin depender del directorio actual.
- Si las feature keys toca permisos, plugins, ventas, soporte o datos, debe declarar feature key y razon de bloqueo.

## Reglas anti-caos

1. No leer licencias desde archivos commiteados.
2. No esconder features hardcodeadas en componentes UI.
3. No usar strings sueltos para planes si ya existe catalogo de plan.
4. No bloquear exportacion ni backup aunque el plan este suspendido.
5. No confundir licencia de producto con metodo de pago del ticket.
6. No meter Remote Ops como requisito para cerrar una venta local.
7. No aceptar comandos remotos arbitrarios como parte de refresco de licencia.
8. No instalar plugins solo por estar listados; deben venir por entitlement activo.
