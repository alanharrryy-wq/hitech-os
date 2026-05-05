# PRISMA Support Bundle Local 04 — Data Allowlist


> Paquete: `PRISMA_CENTRO_PRISMA_UI_SHELL_03`  
> Versión documental: `1.1.0`  
> Fecha: `2026-04-28`  
> Incluye documentación consolidada para iteraciones `03`, `04` y `05`.  
> Alcance: docs, schemas, examples, test-cases, manifest y checksums.  
> Restricción: no instala runtime, no crea rutas Next, no toca DB, no toca `.env`, no ejecuta sync remoto y no procesa pagos.

## Base que no se contradice

Este paquete asume que ya existen y quedan como piso:

- `PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00`: contratos base de customer operations, remote ops, updates, soporte, plugins, licencias y frontera de no procesamiento bancario.
- `PRISMA_RUNTIME_CONFIG_BOUNDARY_01`: separación repo / release / runtime cliente, reglas de `ProgramData`, logs, backups, config y prohibición de depender de `cwd`.
- `PRISMA_LICENSE_LOCAL_MOCK_02`: planes, feature flags mock, entitlements, offline grace y contrato local de licencia.

Nada de este paquete invalida lo anterior. Esto no viene a patear la mesa, viene a poner mantel, cubiertos y letrero de “no meter los dedos al enchufe”.


## Allowlist

| Grupo | Campos permitidos | Redacción |
| --- | --- | --- |
| version | appVersion, packageIds, buildChannel | no |
| runtime | runtimeMode, runtimeRoot, logsRoot, backupRoot | sí en rutas sensibles |
| license | plan, status, featureKeys, graceState | sí ids |
| database | exists, sizeBytes, lastModifiedAt, integrityStatus | no contenido |
| logs | últimas N líneas filtradas | sí |
| outbox | pending, sent, failed, acked, conflict | sin payload |
| plugins | pluginId, version, status, manifestHash | config redactada |
| messages | counts, categories, lastActivityAt | sin body por defecto |

## Denylist dura

| Patrón | Acción |
| --- | --- |
| password | redactar/excluir |
| token | redactar/excluir |
| secret | redactar/excluir |
| apiKey | redactar/excluir |
| DATABASE_URL | redactar credenciales |
| .env | excluir contenido |
| Authorization | redactar |
| Cookie | redactar |
| private_key | excluir |
| access_token | redactar |
| refresh_token | redactar |
| customer PII | redactar salvo autorización explícita |

## Límites de tamaño

| Elemento | Límite sugerido |
| --- | --- |
| logs por archivo | últimas 500 líneas |
| bundle completo | máximo configurable |
| preview | resumen, no contenido crudo |
| mensajes | conteos por defecto |
| outbox | conteos por defecto |
