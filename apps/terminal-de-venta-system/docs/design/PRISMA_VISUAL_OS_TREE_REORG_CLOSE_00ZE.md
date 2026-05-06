# PRISMA Visual OS Tree Reorg Close 00ZE

## Decisión

`tools/prisma-visual-os` queda como árbol gobernado con shims de compatibilidad en la raíz y ejecución real en subcarpetas.

## Alcance

- Verificadores `00X` y `00Y` reorg-aware.
- Carpetas faltantes creadas: `launchers/`, `docs/`, `_plans/`.
- Tool de cierre `prisma_visual_os_tree_reorg_close_00ze.py`.
- Índice `PRISMA_VISUAL_OS_TREE_00ZE_INDEX.md`.

## Fuera de alcance

- POS runtime.
- Tablet UI.
- CSS.
- Shared kernel.
- Migración de `tools/visual`.
- Deprecación de `tools/prisma-pos-visual-control`.

## Criterio de salida

Los verificadores 00X/00Y deben pasar leyendo la implementación en `doctors/` aunque los archivos raíz sean shims.
