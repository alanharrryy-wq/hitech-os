# File Ownership

1. `products/tablet/app/app/pos/page.tsx`: entrada de `/pos`; monta `PosScreen`.
2. `products/tablet/app/components/pos/pos-screen.tsx`: estado, productos, carrito, categorias, busqueda y layout.
3. `products/tablet/app/components/pos/pos-product-search.tsx`: buscador y acciones de resolver/limpiar.
4. `products/tablet/app/components/pos/pos-product-list.tsx`: grid y cards de producto.
5. `products/tablet/app/components/pos/pos-ticket-panel.tsx`: ticket, cantidades, total y checkout link.
6. `products/tablet/app/components/pos/pos-packshots.ts`: contrato visual de packshots.
7. `products/tablet/app/components/pos/pos-error-banner.tsx`: error state.
8. `products/tablet/app/components/pos/pos.module.css`: visual POS real, cards, ticket, botones y estados.
9. `products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx`: shell Tablet, sidebar y header.
10. `products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css`: fondo, sidebar, header, atmosfera.
11. `products/tablet/app/app/layout.tsx`: layout global y tema.
12. `products/tablet/app/app/globals.css`: base global, alto riesgo por blast radius.
