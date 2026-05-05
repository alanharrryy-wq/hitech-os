---
title: PRISMA License UI Policy
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
scope: local-license-entitlements-mock
---

# PRISMA License UI Policy

## 1. Proposito

Definir como Tablet y PC deben mostrar licencia sin estorbar venta.

## 2. Tablet

Tablet es caja. Debe mostrar lo minimo:

- estado de licencia si hay problema;
- banner no invasivo para admin;
- soporte disponible;
- bloqueo claro si una feature no esta incluida;
- nunca popup comercial durante checkout.

## 3. PC Backoffice

PC puede mostrar mas detalle:

- Mi plan;
- Licencia;
- Plugins;
- Novedades;
- Soporte;
- Actualizaciones;
- Diagnostico;
- Dispositivos.

## 4. Mensajes recomendados

| Caso | Texto sugerido |
|---|---|
| feature no incluida | Esta funcion no esta incluida en tu plan actual. |
| plugin pendiente | La activacion fue solicitada y esta pendiente. |
| offline grace | No se pudo validar licencia. PRISMA seguira operando temporalmente. |
| suspended | Tu licencia requiere revision. Puedes exportar y respaldar tus datos. |
| revoked | La licencia fue revocada. Contacta soporte para reactivacion. |

## 5. Regla de tono

Ser claro, no amenazante. El cliente ya tiene negocio encima; no necesita que la app le hable como cobrador con hambre.

## Guardrails operativos

- Esta capa es local-first: la ausencia de internet no debe convertir la caja en ladrillo caro.
- Esta capa no procesa pagos bancarios, no valida transferencias, no toma tarjetas y no custodia dinero.
- Una licencia puede habilitar o limitar funciones, pero no debe borrar datos del cliente.
- Cualquier suspension debe ser gradual, auditable y compatible con exportacion/respaldo.
- Los cambios de licencia deben escribirse como evento administrativo cuando exista event log operacional.
- El mock no es seguridad final: solo define contrato, rutas, estados y ejemplos para la siguiente implementacion.
- El flujo debe poder verificarse sin GitHub, sin red y sin depender del directorio actual.
- Si la UI de licencia toca permisos, plugins, ventas, soporte o datos, debe declarar feature key y razon de bloqueo.

## Reglas anti-caos

1. No leer licencias desde archivos commiteados.
2. No esconder features hardcodeadas en componentes UI.
3. No usar strings sueltos para planes si ya existe catalogo de plan.
4. No bloquear exportacion ni backup aunque el plan este suspendido.
5. No confundir licencia de producto con metodo de pago del ticket.
6. No meter Remote Ops como requisito para cerrar una venta local.
7. No aceptar comandos remotos arbitrarios como parte de refresco de licencia.
8. No instalar plugins solo por estar listados; deben venir por entitlement activo.
