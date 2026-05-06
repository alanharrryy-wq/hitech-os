---
title: PRISMA License State Machine
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
scope: local-license-entitlements-mock
---

# PRISMA License State Machine

## 1. Proposito

Definir transiciones permitidas para licencias locales sin depender de un servidor remoto en tiempo real.

## 2. Estados

```text
dev -> trial -> active -> offline_grace -> active
active -> past_due_external -> active
active -> suspended -> active
active -> expired -> offline_grace -> expired
active -> revoked
trial -> expired
```

## 3. Transiciones permitidas

| Desde | Hacia | Permitido por | Comentario |
|---|---|---|---|
| dev | active | config local dev | solo desarrollo |
| trial | active | refresh remoto futuro | alta comercial externa |
| active | offline_grace | reloj local + fallo remoto | no internet, conserva operacion |
| offline_grace | active | refresh remoto valido | recupera normalidad |
| active | past_due_external | Remote Ops futuro | pendiente administrativo externo |
| past_due_external | active | Remote Ops futuro | regularizado |
| active | suspended | Remote Ops futuro | suspension gradual |
| suspended | active | Remote Ops futuro | reactivacion |
| active | expired | reloj local | vencimiento |
| expired | active | Remote Ops futuro | renovacion |
| active | revoked | Remote Ops futuro | revocacion fuerte |

## 4. Acciones por estado

| Estado | Accion UI | Accion runtime |
|---|---|---|
| active | mostrar plan activo | habilitar entitlements |
| offline_grace | banner discreto a admin | conservar feature set anterior temporal |
| past_due_external | aviso a owner/admin | bloquear upsells y premium si politica lo dice |
| suspended | aviso persistente | bloquear premium, proteger export/backups |
| revoked | aviso critico | bloquear nuevas operaciones comerciales tras grace |
| expired | aviso de vencimiento | aplicar grace si existe |

## 5. Politica de continuidad

La venta local basica no debe depender de validacion remota inmediata. Si se decide bloquear nueva venta por licencia revocada, debe existir:

- aviso previo;
- periodo de gracia;
- exportacion permitida;
- backups permitidos;
- soporte permitido;
- auditoria del cambio.

## 6. Errores canonicos

```text
LICENSE_FILE_NOT_FOUND
LICENSE_FILE_INVALID_JSON
LICENSE_SIGNATURE_INVALID_FUTURE
LICENSE_EXPIRED
LICENSE_SUSPENDED
LICENSE_REVOKED
FEATURE_NOT_ENTITLED
PLUGIN_NOT_ENTITLED
OFFLINE_GRACE_EXPIRED
DEVICE_NOT_ALLOWED
BUSINESS_MISMATCH
```

## Guardrails operativos

- Esta capa es local-first: la ausencia de internet no debe convertir la caja en ladrillo caro.
- Esta capa no procesa pagos bancarios, no valida transferencias, no toma tarjetas y no custodia dinero.
- Una licencia puede habilitar o limitar funciones, pero no debe borrar datos del cliente.
- Cualquier suspension debe ser gradual, auditable y compatible con exportacion/respaldo.
- Los cambios de licencia deben escribirse como evento administrativo cuando exista event log operacional.
- El mock no es seguridad final: solo define contrato, rutas, estados y ejemplos para la siguiente implementacion.
- El flujo debe poder verificarse sin GitHub, sin red y sin depender del directorio actual.
- Si la maquina de estados toca permisos, plugins, ventas, soporte o datos, debe declarar feature key y razon de bloqueo.

## Reglas anti-caos

1. No leer licencias desde archivos commiteados.
2. No esconder features hardcodeadas en componentes UI.
3. No usar strings sueltos para planes si ya existe catalogo de plan.
4. No bloquear exportacion ni backup aunque el plan este suspendido.
5. No confundir licencia de producto con metodo de pago del ticket.
6. No meter Remote Ops como requisito para cerrar una venta local.
7. No aceptar comandos remotos arbitrarios como parte de refresco de licencia.
8. No instalar plugins solo por estar listados; deben venir por entitlement activo.
