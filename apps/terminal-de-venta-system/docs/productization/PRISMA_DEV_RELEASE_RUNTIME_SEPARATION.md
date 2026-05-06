---
title: PRISMA Dev Release Runtime Separation
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---

# PRISMA Dev Release Runtime Separation

## 1. Tres mundos

```text
Development repo
Release bundle
Customer runtime
```

## 2. Development repo

Vive en:

```text
F:\repos\hitech-os
```

Contiene codigo, docs, tooling, tests, fixtures y scripts.

## 3. Release bundle

Contiene artefactos limpios, manifiesto, migraciones y templates.

No contiene datos cliente ni basura de build.

## 4. Customer runtime

Vive en:

```text
C:\ProgramData\PRISMA
```

Contiene la vida operativa del cliente.

## 5. Build gate futuro

Todo release debe pasar un gate que responda:

- que se empaqueta;
- que se excluye;
- donde se instala;
- como se verifica;
- como se revierte;
- que datos quedan fuera del repo.

## 6. Anti patron

No hacer:

```text
copiar apps\terminal-de-venta-system completo al cliente
```

Eso no es producto, es mudanza con cucarachas incluidas.
