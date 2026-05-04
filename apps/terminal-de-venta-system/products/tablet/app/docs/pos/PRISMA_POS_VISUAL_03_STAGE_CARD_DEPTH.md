# PRISMA POS Visual 03 - Stage + Card Depth

**Package ID:** `prisma_pos_visual_03_stage_card_depth`  
**Fecha:** 2026-05-02  
**Scope:** Tablet POS visual foreground only.

## Objetivo

Esta iteración baja un nivel después del pass de packshots: refina **product stage**, **profundidad de card**, **jerarquía de precio/agregar** y **peso visual del CTA de cobro**.

No corrige transparencia de packshots ni reemplaza assets. Ese problema queda estacionado para una futura iteración de assets, porque mezclar limpieza de imagen con depth tuning sería como cambiarle llantas al taxi mientras está en segunda fila.

## Archivos tocados

- `products/tablet/app/components/pos/pos.module.css`
- `products/tablet/app/docs/pos/PRISMA_POS_VISUAL_03_STAGE_CARD_DEPTH.md`

## Layers cubiertos

| Layer | Cobertura |
|---|---|
| Z-3 Card surface | Borde, sombra, hover/focus, profundidad local |
| Z-4 Product stage | Alto, pedestal, aura, floor glow, jerarquía óptica |
| Z-7 Packshot foreground | Movimiento y sombra en hover/focus sin cambiar fuente |
| Z-8 Text/price | Mejor contraste, peso y separación |
| Z-9 CTA | Total y botón COBRAR con mayor presencia controlada |

## No toca

- Backend
- Base de datos
- PC
- `shared-kernel`
- Shell/sidebar/header
- Fondo global
- Assets de packshots

## Criterio visual de salida

- Las cards deben sentirse más profundas sin parecer casino.
- El producto debe pesar más que el fondo de la card.
- Precio y botón Agregar deben ser más legibles.
- El CTA COBRAR debe seguir mandando sobre acciones secundarias.
- El layout no debe moverse de forma estructural.
