# PRISMA POS Visual 04 - Cart Checkout Hierarchy

## Objetivo

Refinar la capa visual del carrito de venta y el cierre de cobro sin tocar lógica, base de datos, shell, fondo global ni packshots.

## Alcance

- Panel derecho `ticketPanel` con mayor presencia visual.
- Líneas de ticket con profundidad, acento lateral y mejor lectura.
- Miniaturas de carrito con sombra y stage más controlado.
- Stepper, remover y total de línea con estados más claros.
- Breakdown, total y botón `COBRAR` con jerarquía de cierre.
- Acciones secundarias reducidas para no competir con `COBRAR`.

## Layer discipline

Esta iteración corresponde al layer de decisión y cierre:

1. Carrito confirma la compra.
2. Total enseña el golpe.
3. `COBRAR` cierra la operación.
4. Acciones secundarias quedan subordinadas.

## No toca

- No toca backend.
- No toca DB.
- No toca PC.
- No toca `shared-kernel`.
- No toca packshots.
- No toca shell/sidebar/header.
- No toca fondo atmosférico.

## Precondición

Requiere que `PRISMA_POS_VISUAL_03_STAGE_CARD_DEPTH` esté aplicado.
