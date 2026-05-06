# PRISMA POS Visual Masterplan

## Decision

La pantalla real de venta es `/pos`; la ruta `prisma-dark-pos-reference` solo es referencia visual. El sistema queda gobernado por planos antes de meter mas CSS.

## Paquetes siguientes

1. `PRISMA_POS_VISUAL_CONTROL_PLANE_260503_v01`: crea tokens, schema, presets, CSS generado y tuner.
2. `PRISMA_POS_VISUAL_SURFACE_LOCK_260503_v01`: aplica tokens a cards, producto, ticket, controles y cobrar.
3. `PRISMA_POS_VISUAL_SHELL_ATMOSPHERE_LOCK_260503_v01`: pule shell, sidebar, header, fondo y atmosfera.

## Reglas

- Producto, ticket y `COBRAR` mandan antes que fondo.
- No tocar PC, Mobile, shared-kernel ni shared-ui.
- No tocar reference route salvo para inspiracion.
- Todo valor visual repetido debe migrar a token.
- Todo ZIP debe tener dry-run, apply, verify, rollback, backup y log.
