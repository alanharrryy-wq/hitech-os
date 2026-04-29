# PRISMA 03-04-05 — Installer Plan Documental


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


## Instalador esperado

Nombre sugerido:

```text
install_prisma_centro_prisma_ui_shell_03_full_docs_03_04_05.py
```

## Modos obligatorios

```text
--dry-run
--apply
--verify
--rollback
--repo-root F:\repos\hitech-os
--downloads-root F:\descargasf
```

## Product root

```text
F:\repos\hitech-os\apps\terminal-de-venta-system
```

## Debe instalar

- `payload/docs/productization/*`
- `payload/tooling/productization/schemas/*`
- `payload/tooling/productization/examples/*`
- `payload/tooling/productization/test-cases/*`
- `payload/tooling/productization/manifests/*`
- `payload/tooling/productization/checklists/*`
- `payload/tooling/productization/installer-plan/*`

## Debe rechazar

- rutas fuera de `payload/`;
- path traversal;
- archivos `.env`;
- archivos `.db`;
- carpetas `.next`;
- carpetas `node_modules`;
- archivos ejecutables no esperados;
- zip anidado;
- rutas absolutas dentro del ZIP.

## Verify

- Todos los JSON parsean.
- Manifest existe.
- Checksums existen.
- Docs 03/04/05 existen.
- No hay archivos prohibidos.
- El manifest no se auto-hashea.

## Rollback

Restaurar backups de reemplazos y eliminar creaciones nuevas registradas en manifest de apply.
