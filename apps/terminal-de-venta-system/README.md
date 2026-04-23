# Terminal de Venta System

Professional twin-product repository for Terminal de Venta.

## Real Structure
- `products/pc/app`: real PC product source (Next.js + TypeScript + Prisma integration layer).
- `products/tablet/app`: real Tablet product source (Next.js + TypeScript + Prisma integration layer).
- `shared/twin-kernel`: real shared twin contract code used by both products.
- `architecture/prisma-lab`: exploratory Prisma architecture material only.
- `tooling/scripts`: repository-level operational scripts.
- `docs`: repository documentation and structural diagrams.
- `out`: local temporary area only (`tmp`, `archive`), not canonical source.

## Launcher
Use:
`F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta.cmd`

## Cleanup Guarantees
- No zip artifacts inside this repository tree.
- No delivery/package folders pretending to be source-of-truth.
- Canonical source is directly visible under `products/*/app`.
