# PRISMA Tablet Packshot Engine 03

Visual-only patch for Tablet POS packshots.

## What changed

- The default first category is now `Más vendidos`, not `Todas`.
- The featured shelf interleaves product families so the first page shows variety instead of a water-bottle parade.
- Water packshots have a dedicated CSS size/crop tune to avoid looking tiny inside the product card.
- Water aliases are more specific: Bonafont, Ciel, Cristal, mineral, con gas, tónica, natural and purificada no longer collapse into the same slug when enough clues exist.

## Safety boundary

This patch touches only Tablet POS UI files:

- `components/pos/pos-screen.tsx`
- `components/pos/pos-packshots.ts`
- `components/pos/pos.module.css`

It does not modify POS sale logic, checkout, stock, sync, DB, API routes, PC, shared-kernel or migrations.

## QA checklist

1. Open `http://127.0.0.1:3120/`.
2. Confirm the first chip says `Más vendidos`.
3. Confirm the first page shows mixed product families: aceite, agua, leche/pan/huevo/botana/dulce/limpieza when present.
4. Confirm water packshots no longer look like tiny bottles lost in a white postage stamp.
5. Add one product to the ticket and confirm the cart thumbnail still renders.
6. Confirm COBRAR still opens checkout.
