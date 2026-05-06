---
title: PRISMA Plan Catalog Contract
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
scope: local-license-entitlements-mock
---

# PRISMA Plan Catalog Contract

## 1. Proposito

Definir los planes comerciales como catalogo tecnico de capacidades. Un plan no debe ser solo texto bonito; debe mapear a feature keys y permisos.

## 2. Planes canonicos

### TABLET_SOLO

Incluye:

- `pos.sales.complete`
- `pos.ticket.local`
- `inventory.local.decrement`
- `report.today.basic`
- `export.local.basic`
- `support.basic`

### TABLET_PRO

Incluye todo TABLET_SOLO y ademas:

- `pos.returns.create`
- `pos.sale.cancel`
- `shift.open`
- `shift.close`
- `inventory.local.adjust`
- `event.outbox.view`
- `export.local.advanced`
- `backup.local.scheduled`

### PC_BACKOFFICE

Incluye:

- `catalog.write`
- `inventory.backoffice.view`
- `inventory.backoffice.adjust`
- `purchase.write`
- `receiving.write`
- `audit.view`
- `dashboard.kpis`
- `sync.ingest`
- `support.advanced`

### TABLET_PC_MANAGED

Incluye combinacion gobernada:

- `managed.devices`
- `sync.managed`
- `sync.conflict.resolve`
- `catalog.snapshot.publish`
- `license.remote.refresh`
- `plugin.remote.activate`
- `support.remote`

## 3. Politica de downgrade

Si un cliente baja de plan:

- no borrar datos historicos;
- conservar lectura de registros existentes;
- bloquear nuevas acciones premium;
- mantener exportacion;
- auditar el cambio;
- desactivar plugins no cubiertos sin destruir datos propios del plugin.

## 4. Politica de upgrade

Si un cliente sube de plan:

- refrescar licencia;
- habilitar entitlements;
- mostrar anuncio administrativo;
- permitir instalacion de plugins compatibles;
- no requerir reinstalar toda la app.

## Guardrails operativos

- Esta capa es local-first: la ausencia de internet no debe convertir la caja en ladrillo caro.
- Esta capa no procesa pagos bancarios, no valida transferencias, no toma tarjetas y no custodia dinero.
- Una licencia puede habilitar o limitar funciones, pero no debe borrar datos del cliente.
- Cualquier suspension debe ser gradual, auditable y compatible con exportacion/respaldo.
- Los cambios de licencia deben escribirse como evento administrativo cuando exista event log operacional.
- El mock no es seguridad final: solo define contrato, rutas, estados y ejemplos para la siguiente implementacion.
- El flujo debe poder verificarse sin GitHub, sin red y sin depender del directorio actual.
- Si el catalogo de planes toca permisos, plugins, ventas, soporte o datos, debe declarar feature key y razon de bloqueo.

## Reglas anti-caos

1. No leer licencias desde archivos commiteados.
2. No esconder features hardcodeadas en componentes UI.
3. No usar strings sueltos para planes si ya existe catalogo de plan.
4. No bloquear exportacion ni backup aunque el plan este suspendido.
5. No confundir licencia de producto con metodo de pago del ticket.
6. No meter Remote Ops como requisito para cerrar una venta local.
7. No aceptar comandos remotos arbitrarios como parte de refresco de licencia.
8. No instalar plugins solo por estar listados; deben venir por entitlement activo.
