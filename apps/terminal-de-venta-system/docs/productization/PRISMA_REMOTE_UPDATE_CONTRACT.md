---
title: PRISMA Remote Update Contract
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Remote Update Contract

## 1. Decisión

PRISMA debe poder actualizarse de forma local o remota, siempre con staging, backup, verificación y rollback.

Updates no deben depender de GitHub, cwd ni intervención manual larga.

## 2. Release bundle

```text
PRISMA_<PACKAGE>_<VERSION>.zip
release-manifest.json
installer.py
```

## 3. Canales

```text
stable
pilot
hotfix
internal
```

## 4. Flujo

```text
check update
validate license
validate compatibility
download bundle
verify checksum/signature
create backup
stage payload
apply
run migrations
verify
activate version
cleanup staging
```

Si falla verify:

```text
automatic rollback
```

## 5. Regla de operación

No actualizar si:

- hay venta abierta,
- hay migración pendiente,
- falta espacio en disco,
- no puede crear backup,
- checksum falla,
- versión no es compatible,
- rollback plan no existe.

## 6. Logs

Install/update debe generar un log único por operación.

Durante desarrollo:

```text
F:\descargasf
```

En cliente:

```text
C:\ProgramData\PRISMA\logs\install```

## 7. Rollback

Debe restaurar:

- archivos app,
- config modificada,
- DB pre-migration si aplica,
- manifest activo,
- plugin state si aplica.

## 8. Manifest mínimo

```text
releaseId
packageName
packageVersion
channel
compatibleVersions
files
checksums
migrations
verifyChecks
rollbackPlan
signature
```

## 9. No debe incluir

- node_modules,
- .git,
- .next cache,
- DB cliente,
- logs,
- backups,
- secrets,
- temp,
- screenshots pesados.
