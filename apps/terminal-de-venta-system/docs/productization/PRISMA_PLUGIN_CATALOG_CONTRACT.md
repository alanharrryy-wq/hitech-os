---
title: PRISMA Plugin Catalog Contract
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Plugin Catalog Contract

## 1. Decisión

PRISMA puede extenderse con plugins, pero los plugins deben ser declarativos, versionados, compatibles, auditables y reversibles.

No se permite código arbitrario sin manifiesto, firma, permisos y rollback.

## 2. Plugin inicial

Un plugin debe declarar:

```text
pluginId
name
version
compatiblePrismaVersions
requiredPlan
permissions
runtimeSurfaces
dbMigrations
events
rollbackPlan
signature
```

## 3. Tipos de plugin

| Tipo | Ejemplo |
|---|---|
| commercial | promociones, fidelidad |
| operational | inventario avanzado, alertas |
| hardware | báscula, impresora |
| reporting | reportes avanzados |
| sync | multi-sucursal, rutas |
| support | diagnóstico extendido |
| ai_future | asistente de soporte |

## 4. Permisos

```text
catalog.read
catalog.write
sales.read
sales.write
inventory.read
inventory.adjust
reports.create
sync.emit
support.diagnostics
hardware.access
ui.surface.register
```

## 5. Reglas

1. Plugin debe ser compatible con versión instalada.
2. Plugin debe requerir entitlement activo.
3. Plugin que toca DB debe traer migración y rollback.
4. Plugin que toca dinero, stock o permisos debe generar evento.
5. Plugin debe poder desactivarse.
6. Plugin no debe romper venta local básica.
7. Plugin no debe procesar pagos bancarios.

## 6. Instalación

```text
validate license
validate compatibility
validate signature
backup
stage files
run migrations
verify
activate
```

## 7. Desactivación

Desactivar no siempre significa borrar datos. Preferir:

```text
disabled
```

antes de:

```text
uninstalled
```

## 8. Superficies UI

Un plugin puede pedir superficies:

```text
pc.dashboard.card
pc.settings.panel
tablet.status.badge
tablet.settings.panel
```

No debe inyectarse en checkout sin revisión explícita.

## 9. Prohibiciones

- No ejecutar scripts libres.
- No instalar dependencias externas sin manifiesto.
- No tocar archivos fuera de rutas permitidas.
- No modificar ventas históricas sin auditoría.
- No cambiar licencia.
- No abrir puertos entrantes sin contrato de seguridad.
