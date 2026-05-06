# PRISMA POS Visual 02 - Packshot Repair Normalized

## Objetivo

Reparar la primera capa visual superior del POS: imagen del producto en card y miniatura del carrito.

## Alcance

- Agrega `public/pos-packshots/*.png` con 8 packshots normalizados.
- Agrega `components/pos/pos-packshots.ts` como mapeo visual producto -> asset.
- Actualiza `pos-product-list.tsx` para renderizar packshot en el stage si existe.
- Actualiza `pos-ticket-panel.tsx` para renderizar miniatura real en ticket.
- Agrega CSS marcado con `PRISMA_POS_VISUAL_02_PACKSHOT_REPAIR_NORMALIZED`.

## Layer policy

Esta iteración toca únicamente capas superiores:

1. packshot de producto;
2. stage interno de card;
3. thumbnail de carrito.

No modifica fondo global, shell, sidebar, header, backend, DB, rutas ni shared-kernel.

## Nota de producción

Los assets incluidos son packshots visuales normalizados para UI. Para uso comercial con marcas reales, reemplazar los PNG por assets licenciados manteniendo los mismos nombres de archivo.
