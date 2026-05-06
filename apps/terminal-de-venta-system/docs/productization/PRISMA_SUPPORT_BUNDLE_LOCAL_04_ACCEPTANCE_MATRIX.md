# PRISMA Support Bundle Local 04 — Acceptance Matrix


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


| Área | Acepta si | Bloquea si |
| --- | --- | --- |
| consentimiento | estados definidos | genera sin autorización |
| allowlist | solo datos permitidos | lee fuera de lista |
| denylist | secretos redactados | token sin redacción |
| manifest | bundle futuro tiene manifest | bundle sin inventario |
| DB | estado superficial | dump de datos |
| logs | filtrados y limitados | log crudo con secreto |
| messages | conteos por defecto | body completo sin permiso |
| Centro UI | diagnóstico read-only/consent | botón generar sin contrato |
