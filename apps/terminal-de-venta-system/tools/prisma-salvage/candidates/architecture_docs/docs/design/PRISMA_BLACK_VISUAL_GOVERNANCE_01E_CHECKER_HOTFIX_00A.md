# PRISMA Black Visual Governance 01E Checker Hotfix 00A

Este hotfix corrige el verificador read-only instalado por `PRISMA_BLACK_VISUAL_GOVERNANCE_BASELINE_01E`.

## Qué corrige

- Cambia `require(...)` por imports ESM válidos en archivo `.mjs`.
- Soporta `--root <path>` como estaba documentado.
- Mantiene el checker en modo read-only.

## Qué NO toca

No modifica CSS visual, tokens, layout, componentes, datos ni rutas de la aplicación.
