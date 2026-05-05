---
title: PRISMA Data Outside Repo Policy
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---

# PRISMA Data Outside Repo Policy

## 1. Decision

Todo dato runtime de cliente debe vivir fuera del repositorio.

## 2. Permitido en repo

- codigo fuente;
- fixtures demo;
- schemas;
- migraciones;
- documentacion;
- tests;
- manifests de paquete;
- scripts de tooling.

## 3. Prohibido en repo para cliente

- DB real;
- tickets reales;
- ventas reales;
- backups cliente;
- logs cliente;
- licencias activas cliente;
- tokens;
- secretos;
- support bundles con datos reales.

## 4. Riesgo actual reconocido

En desarrollo puede existir:

```text
products\tablet\app\data\tablet-pos.db
```

Eso debe tratarse como DB de desarrollo, no como patron de instalacion cliente.

## 5. Regla de instalacion

El instalador de cliente debe crear o seleccionar:

```text
C:\ProgramData\PRISMA\businesses\<businessId>\tablet\data\tablet-pos.db
```

## 6. Verificacion futura

Antes de empaquetar release, un gate debe fallar si detecta:

- `.db` dentro del bundle;
- `.log` dentro del bundle;
- `.env` dentro del bundle;
- `.next/cache` dentro del bundle;
- `node_modules` dentro del bundle;
- `.prisma_integration_backups` dentro del bundle cliente.
