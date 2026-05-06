# Plan de cierre 00ZE

## Objetivo

Cerrar la migración de Visual OS corrigiendo verificadores que todavía leían shims raíz como si fueran implementación completa.

## Cambios

1. Hacer reorg-aware los verificadores `00X` y `00Y`.
2. Crear carpetas faltantes del contrato de árbol.
3. Declarar la raíz como capa de compatibilidad.
4. Validar gates existentes sin tocar runtime POS ni UI.

## Límites

- `tools/visual` queda separado por ahora como utilería de referencia visual `01H`.
- `tools/prisma-pos-visual-control` queda como legado pendiente de decisión.
- No se mueven launchers `.cmd` todavía para no romper hábitos/atajos existentes.
