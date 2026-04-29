---
title: PRISMA Customer Operations Roadmap
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Customer Operations Roadmap

## Decisión

Esta ruta convierte la capa Customer Operations en un sistema real sin romper Tablet ni PC. La implementación debe ir por entregas pequeñas, verificables y reversibles.

## Fase 00 - Foundation

Instala documentación, contratos, schemas, manifest y plan de instalador. No toca runtime. No toca DB. No toca UI. No toca ventas.

Criterio de salida:

- existen contratos de licencias, mensajes, anuncios, soporte, plugins, updates e IA futura;
- existen schemas JSON;
- existe manifest;
- existe plan de instalador;
- el paquete puede verificarse y revertirse.

## Fase 01 - Runtime config boundary

Define la frontera entre repo, release y runtime cliente.

Entregables:

- runtime path resolver documentado;
- config schema base;
- rutas objetivo bajo `C:\ProgramData\PRISMA`;
- no dependencia de cwd;
- lista de rutas prohibidas en runtime cliente.

## Fase 02 - Local license mock

Agrega licencia local sin servidor.

Entregables:

- `license.json` mock;
- feature flags locales;
- lectura desde config;
- pantalla o endpoint de estado;
- verify sin red.

## Fase 03 - Centro PRISMA UI shell

Crea superficies visibles para el cliente.

PC:

```text
/centro-prisma
/centro-prisma/licencia
/centro-prisma/plugins
/centro-prisma/soporte
/centro-prisma/mensajes
/centro-prisma/novedades
/centro-prisma/diagnostico
/centro-prisma/actualizaciones
```

Tablet:

```text
/centro-prisma
/centro-prisma/estado
/centro-prisma/soporte
/centro-prisma/novedades
```

## Fase 04 - Support bundle local

Genera diagnóstico local saneado. Debe excluir secretos, DB completa, datos bancarios y tokens.

## Fase 05 - Messaging local mock

Crea threads y mensajes locales para simular flujo cliente-proveedor sin servidor real.

## Fase 06 - Announcements local

Crea popups y banners controlados por rol, severidad, plan y versión.

## Fase 07 - Plugin manifest loader

Lee plugins declarativos. No ejecuta código arbitrario. Valida permisos, versión y entitlement.

## Fase 08 - Remote Ops bridge

Agrega comunicación saliente por polling. No abre puertos entrantes. No exige internet para vender.

## Fase 09 - AI-ready support context

Prepara contexto read-only para IA futura.

## Regla permanente

Cada fase debe poder entrar como ZIP + instalador `.py`, con `--dry-run`, `--apply`, `--verify` y `--rollback`.

## Anticaos

Si una fase intenta tocar ventas, DB, sync real o licencia remota antes de tener contratos y verify, se bloquea. Primero amarrar la puerta, luego meter la mercancía. Así evitamos el clásico software que parece tiendita pero por dentro es puesto de cables robados.
