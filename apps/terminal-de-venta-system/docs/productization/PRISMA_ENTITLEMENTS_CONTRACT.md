---
title: PRISMA Entitlements Contract
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
scope: local-license-entitlements-mock
---

# PRISMA Entitlements Contract

## 1. Proposito

Un entitlement es la autorizacion concreta para usar una feature o plugin. El plan sugiere, el entitlement manda.

## 2. Estructura conceptual

```json
{
  "entitlementId": "ent_demo_pos_sales",
  "businessId": "biz_demo_store",
  "featureKey": "pos.sales.complete",
  "status": "active",
  "source": "plan",
  "expiresAt": null
}
```

## 3. Fuentes permitidas

| Source | Uso |
|---|---|
| plan | viene incluido por plan |
| plugin | viene por plugin activo |
| trial | habilitado temporalmente |
| override | habilitacion manual desde Remote Ops futuro |
| dev | desarrollo |

## 4. Estados

| Estado | Uso |
|---|---|
| active | habilitado |
| inactive | no habilitado |
| pending_activation | solicitado, no activo |
| suspended | bloqueado temporalmente |
| expired | vencido |

## 5. Resolucion

Para saber si una feature esta habilitada:

1. leer licencia local;
2. validar businessId/deviceId;
3. revisar status de licencia;
4. resolver plan;
5. cargar entitlements;
6. aplicar expiraciones;
7. aplicar overrides;
8. devolver `allowed`, `reason`, `source`.

## 6. Resultado esperado

```json
{
  "featureKey": "pos.returns.create",
  "allowed": true,
  "reason": "ENTITLED_BY_PLAN",
  "source": "plan"
}
```

Si no esta permitido:

```json
{
  "featureKey": "dashboard.kpis",
  "allowed": false,
  "reason": "FEATURE_NOT_INCLUDED_IN_PLAN",
  "source": "plan"
}
```

## Guardrails operativos

- Esta capa es local-first: la ausencia de internet no debe convertir la caja en ladrillo caro.
- Esta capa no procesa pagos bancarios, no valida transferencias, no toma tarjetas y no custodia dinero.
- Una licencia puede habilitar o limitar funciones, pero no debe borrar datos del cliente.
- Cualquier suspension debe ser gradual, auditable y compatible con exportacion/respaldo.
- Los cambios de licencia deben escribirse como evento administrativo cuando exista event log operacional.
- El mock no es seguridad final: solo define contrato, rutas, estados y ejemplos para la siguiente implementacion.
- El flujo debe poder verificarse sin GitHub, sin red y sin depender del directorio actual.
- Si los entitlements toca permisos, plugins, ventas, soporte o datos, debe declarar feature key y razon de bloqueo.

## Reglas anti-caos

1. No leer licencias desde archivos commiteados.
2. No esconder features hardcodeadas en componentes UI.
3. No usar strings sueltos para planes si ya existe catalogo de plan.
4. No bloquear exportacion ni backup aunque el plan este suspendido.
5. No confundir licencia de producto con metodo de pago del ticket.
6. No meter Remote Ops como requisito para cerrar una venta local.
7. No aceptar comandos remotos arbitrarios como parte de refresco de licencia.
8. No instalar plugins solo por estar listados; deben venir por entitlement activo.
