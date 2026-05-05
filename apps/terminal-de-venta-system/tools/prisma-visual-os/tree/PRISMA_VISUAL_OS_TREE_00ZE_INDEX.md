# PRISMA Visual OS Tree Reorg Close 00ZE

**Paquete:** `PRISMA_VISUAL_OS_TREE_REORG_CLOSE_00ZE_20260505_v02`  
**Estado:** cierre de migración de árbol Visual OS.  
**Regla:** la raíz de `tools/prisma-visual-os` conserva shims de compatibilidad; la implementación vive en subcarpetas gobernadas.

## Qué cierra

- `verify_prisma_show_pos_doctor_00x.mjs` ahora resuelve implementación real en `doctors/` cuando la raíz es shim.
- `verify_prisma_show_pos_ai_doctor_00y.mjs` ahora resuelve implementación real en `doctors/` cuando la raíz es shim.
- Se crean las carpetas esperadas por el contrato de árbol: `launchers/`, `docs/` y `_plans/`.
- Se deja herramienta de cierre `tree/prisma_visual_os_tree_reorg_close_00ze.py` para validar el estado.

## Qué no hace

- No mueve launchers `.cmd` todavía.
- No toca POS runtime.
- No toca Tablet UI.
- No toca CSS operativo.
- No toca `shared-kernel`.
- No elimina `tools/visual` ni `tools/prisma-pos-visual-control`.

## Comandos esperados

```cmd
tools\prisma-visual-os
un_prisma_visual_os_tree_reorg_close_00ze.cmd --verify
```

También puede ejecutarse directo:

```cmd
py tools\prisma-visual-os	ree\prisma_visual_os_tree_reorg_close_00ze.py --target-root F:
epos\hitech-os --out-dir F:\descargasf --verify
```
