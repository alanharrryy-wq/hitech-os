# PRISMA POS Visual Surface Lock 01

This package applies the first real surface-level visual lock for Tablet `/pos`.

It is intentionally scoped to the POS foreground:

- product cards
- product stage
- packshots and fallback
- search/catalog count surface
- category rail count
- ticket lines
- ticket thumbnails
- total and COBRAR hierarchy

It does not touch PC, Mobile, shared-kernel, shared-ui, backend APIs or `components/prisma-dark-pos/*`.

## Sequence

This ZIP follows:

1. `PRISMA_POS_VISUAL_MASTERPLAN_260503_v01`
2. `PRISMA_POS_VISUAL_CONTROL_PLANE_260503_v01`

It is self-contained enough to refresh the token files and packshots, but it assumes the visual control folder is part of the accepted architecture.

## Acceptance

Open `http://127.0.0.1:3120/pos` after apply and verify:

- product cards are more premium and less flat;
- product packshots are larger and stage-governed;
- ticket rows use the same thumbnail contract as cards;
- total and COBRAR dominate;
- catalog counts are coherent;
- add/remove/quantity/checkout still work.
