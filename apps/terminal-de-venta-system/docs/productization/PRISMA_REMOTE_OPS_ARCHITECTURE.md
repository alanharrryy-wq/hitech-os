---
title: PRISMA Remote Ops Architecture
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Remote Ops Architecture

## 1. Decisión

PRISMA Remote Ops es la capa del proveedor para administrar clientes, negocios, dispositivos, licencias, mensajes, soporte, anuncios, plugins, releases, diagnósticos y futura asistencia con IA.

No es una dependencia crítica para cerrar ventas locales. Tablet debe seguir vendiendo aunque Remote Ops no responda. PC puede gobernar cuando existe. Sync reconcilia cuando hay conexión. Los eventos sostienen la verdad operacional.

## 2. Principios

1. **Local-first:** el cliente puede operar localmente.
2. **Remote-managed:** el proveedor puede administrar estado, licencia, mensajes y updates.
3. **No payment processing:** PRISMA no procesa tarjetas, transferencias ni pagos bancarios.
4. **Consentimiento operativo:** soporte remoto y diagnósticos requieren autorización visible.
5. **Allowlist sobre ejecución libre:** Remote Ops solo envía comandos predefinidos.
6. **Rollback primero:** ningún update o plugin se aplica sin plan de reversión.
7. **Auditoría permanente:** cambios sensibles generan eventos o logs trazables.

## 3. Componentes

```text
PRISMA Remote Ops
  Customers
  Businesses
  Devices
  Licenses
  Entitlements
  Messages
  Announcements
  Support Tickets
  Diagnostic Bundles
  Releases
  Plugins
  Remote Commands
  Audit Log
```

```text
PRISMA Customer Runtime
  Tablet POS
  PC Backoffice
  Local Agent
  Runtime Config
  Local DBs
  Logs
  Backups
  Exports
  Support Bundles
```

## 4. Remote Ops no debe hacer

- No debe autorizar cada venta.
- No debe bloquear venta básica por caída de internet.
- No debe ejecutar PowerShell remoto arbitrario.
- No debe borrar datos cliente.
- No debe tocar DB directamente sin auditoría y backup.
- No debe procesar pagos bancarios.
- No debe instalar plugins sin firma, compatibilidad y rollback.

## 5. Local Agent

El Local Agent será el puente local. Puede empezar como módulo de PC o tooling interno y luego volverse producto propio.

Responsabilidades:

| Área | Responsabilidad |
|---|---|
| Licencia | refrescar licencia y validar grace offline |
| Updates | descargar, verificar, stagear y aplicar releases |
| Plugins | instalar, desactivar y verificar módulos |
| Diagnostics | generar support bundles |
| Health | reportar versión, estado y errores resumidos |
| Messaging | sincronizar mensajes y tickets |
| Announcements | cachear novedades y popups |
| Security | validar firmas y allowlist de comandos |

## 6. Flujo base de heartbeat

```text
Local Agent -> Remote Ops: device heartbeat
Remote Ops -> Local Agent: license status, pending messages, announcements, allowed commands, update metadata
Local Agent -> Local Runtime: cache local y notificación a Tablet/PC
```

## 7. Polling seguro

La arquitectura inicial debe preferir polling saliente desde el cliente, no puertos entrantes.

Razón: evita configuración de router, NAT, firewall y soporte infernal de módem de tienda, ese objeto mitológico que nadie sabe administrar.

## 8. Canales

| Canal | Propósito |
|---|---|
| stable | clientes normales |
| pilot | clientes controlados |
| hotfix | correcciones urgentes |
| internal | pruebas internas |

## 9. Evolución por fases

1. Contratos y schemas.
2. Licencia local mock.
3. Centro PRISMA UI.
4. Support bundle local.
5. Messaging local mock.
6. Announcements controlados.
7. Plugin manifest loader.
8. Remote Ops bridge.
9. IA read-only para soporte.

## 10. Criterio de aceptación

Remote Ops está bien diseñado si el cliente puede vender sin internet, el proveedor puede administrar sin invadir, y cualquier intervención deja rastro, validación y rollback.
