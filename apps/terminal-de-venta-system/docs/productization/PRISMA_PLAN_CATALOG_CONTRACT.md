---
title: PRISMA Plan Catalog Contract
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
scope: licensing-entitlements-and-commercial-pricing
---

# PRISMA Plan Catalog Contract

## 1. Proposito

Definir los planes comerciales como catalogo tecnico de capacidades y como contrato economico de lista. Un plan no debe ser solo texto bonito: debe mapear a feature keys, permisos, limites y una condicion comercial verificable.

La autoridad machine-readable para planes vendibles, limites y precio de lista es:

`shared/licensing/plan-catalog.canonical.json`

Los consumidores administrativos y de productizacion deben derivar de esa autoridad. No deben crear listas de precios paralelas ni hardcodear montos en UI, Cloud Center, Customer Setup, PC, Tablet o Mobile.

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

Describe capacidades de backoffice, pero no es un SKU vendible independiente mientras `plan-catalog.canonical.json` no lo marque como plan vendible.

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

## 3. Precio comercial canonico

Version de precio: `2026-08-14.v1`.

Mercado inicial: Mexico.
Moneda: MXN.
Impuestos: precios de lista antes de IVA; se agrega el IVA aplicable.
Alcance de cobro: por asignacion de licencia, respetando los limites tecnicos del plan.

| Plan vendible | Mensual | Trimestral | Semestral | Anual |
|---|---:|---:|---:|---:|
| `TABLET_SOLO` | $399 | $1,149 | $2,199 | $3,999 |
| `TABLET_PRO` | $599 | $1,699 | $3,299 | $5,999 |
| `TABLET_PC_MANAGED` | $999 | $2,849 | $5,499 | $9,999 |

Reglas:

1. Estos son precios de lista canonicos de PRISMA, no precios de productos vendidos por los comercios clientes.
2. El owner de precios de mercancia/promociones/impuestos del negocio (`pricing-policy`) es otra capacidad y no debe consumir ni mutar este catalogo de licencias.
3. Un contrato firmado existente conserva su precio contratado hasta renovacion; no se reescribe retroactivamente.
4. No se debe inferir el precio historico del primer cliente a partir de esta tabla.
5. `DEVELOPMENT` no es vendible y no tiene precio comercial.
6. Los descuentos por periodicidad estan expresados directamente en los montos canonicos; ningun consumidor debe recalcularlos con formulas propias.
7. Cualquier cambio futuro de precio debe cambiar la version de precio y actualizar la autoridad machine-readable, el verificador y la evidencia correspondiente.

## 4. Mobile y combinacion de superficies

Customer Setup reconoce slots Tablet, PC y Mobile. Sin embargo, mientras no exista un entitlement Mobile canonico y vendible en `plan-catalog.canonical.json`, Mobile no tiene SKU ni precio independiente.

Regla comercial actual:

`DO_NOT_PRICE_SEPARATELY_UNTIL_EXPLICIT_CANONICAL_MOBILE_ENTITLEMENT_EXISTS`

No se debe inventar `TABLET_PC_MOBILE`, `MOBILE_PRO` ni ningun SKU equivalente desde UI, documentacion, ventas o Cloud Center sin pasar por contrato de licensing y governance.

## 5. Posicionamiento visual

PRISMA se posiciona como experiencia operativa premium y coherente entre superficies. La calidad visual, el lenguaje de componentes, la claridad operacional y la consistencia multi-surface forman parte del valor comercial del producto.

Esa ventaja visual:

- si forma parte del posicionamiento y de la justificacion economica;
- no crea feature keys por si sola;
- no altera permisos ni limites;
- no permite inventar un plan adicional;
- no sustituye soporte, continuidad, seguridad, offline/local-first ni evidencia operacional;
- debe respetar Visual OS, governors, layer maps y contratos visuales cuando exista una modificacion real de interfaz.

Esta homologacion de pricing no autoriza por si misma ningun cambio visual en Tablet, PC o Mobile.

## 6. Politica de downgrade

Si un cliente baja de plan:

- no borrar datos historicos;
- conservar lectura de registros existentes;
- bloquear nuevas acciones premium;
- mantener exportacion;
- auditar el cambio;
- desactivar plugins no cubiertos sin destruir datos propios del plugin.

## 7. Politica de upgrade

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
- El flujo debe poder verificarse sin GitHub, sin red y sin depender del directorio actual.
- Si el catalogo de planes toca permisos, plugins, ventas, soporte o datos, debe declarar feature key y razon de bloqueo.
- Precio comercial y entitlement tecnico comparten `plan`, pero son dimensiones distintas del mismo contrato.

## Reglas anti-caos

1. No leer licencias activas desde archivos commiteados; el catalogo commiteado define contrato, no estado vivo del cliente.
2. No esconder features hardcodeadas en componentes UI.
3. No usar strings sueltos para planes si ya existe catalogo de plan.
4. No hardcodear precios de licencia fuera de `plan-catalog.canonical.json`.
5. No bloquear exportacion ni backup aunque el plan este suspendido.
6. No confundir licencia de producto con metodo de pago del ticket.
7. No confundir pricing de licencia PRISMA con pricing de mercancia del comercio.
8. No meter Remote Ops como requisito para cerrar una venta local.
9. No aceptar comandos remotos arbitrarios como parte de refresco de licencia.
10. No instalar plugins solo por estar listados; deben venir por entitlement activo.
