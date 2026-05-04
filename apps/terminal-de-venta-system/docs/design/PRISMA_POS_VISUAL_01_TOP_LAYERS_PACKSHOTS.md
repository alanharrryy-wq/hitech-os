# PRISMA POS Visual 01 - Top Layers Packshots

## Objetivo

Primera iteracion visual top-layer-first para `/pos`.

Esta entrega empieza por las capas visibles superiores para no volver a editar a ciegas:

1. packshots de producto;
2. vitrina/stage de producto;
3. miniaturas del carrito;
4. total y `COBRAR` como climax visual.

## Capas tocadas

| Layer | Estado | Archivos |
|---|---|---|
| Z-7 Packshot real | agregado | `pos-packshots.ts`, `public/products/packshots/*` |
| Z-6 Product stage | refinado | `pos.module.css` |
| Z-8 Texto/precio/carrito | preservado | `pos-product-list.tsx`, `pos-ticket-panel.tsx` |
| Z-9 Total/COBRAR | reforzado | `pos.module.css` |

## Capas no tocadas intencionalmente

No se cambia fondo global, shell, sidebar, rutas, backend, shared-kernel ni contratos.

## Nota de assets

Los PNG incluidos se derivan de la imagen de referencia subida para sembrar la primera iteracion visual.
Son reemplazables por packshots licenciados conservando los mismos nombres.

## Criterio de aceptacion

PASS si:

- las cards muestran imagen real/fotografica cuando el producto coincide;
- el fallback sigue funcionando si no hay packshot;
- el carrito muestra miniaturas reales;
- `COBRAR` y total tienen mayor protagonismo;
- el fondo no fue modificado en esta ronda.
