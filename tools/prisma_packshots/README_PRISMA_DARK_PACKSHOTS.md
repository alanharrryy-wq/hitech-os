# PRISMA Dark Packshots 197

- Biblioteca administrada: `tools/_local/data/terminal-de-venta-system/product-media`.
- Runtime: `/product-media/catalog/<archivo>.png`.
- Miniaturas: `/product-media/thumbnails/<archivo>.png`.
- PC y Tablet operan siempre en modo oscuro.
- `Product.mediaRef` conserva una referencia portable y el sync PC→Tablet la proyecta.
- Capacidad operativa de catálogo: 5000 productos.
- No se almacenan bytes de imagen dentro de SQLite.
