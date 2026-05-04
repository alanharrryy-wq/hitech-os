# PRISMA_TABLET_CHECKOUT_FINALIZATION_FIX_31_20260503_v01

Fixes the POS payment finalization flow where `OK, generar ticket` could stay inside the payment modal because the client sent a nested checkout object as `items` instead of the API `items[]` array.

## Scope

- Tablet POS checkout client flow only.
- No shared-kernel changes.
- No PC changes.
- No route or Prisma schema changes.

## Files

- `src/lib/pos/payment-flow.ts`: sends `checkout.items` array to `/api/pos/sales/complete`.
- `src/lib/pos/cart-state.ts`: makes API/HTTP parsing errors visible.
- `src/lib/pos/pos-visible-errors.ts`: adds user-safe messages for finalization errors.
- `components/pos/pos-payment-panel.tsx`: adds visible busy/error states.
- `components/pos/pos.module.css`: styles checkout busy/error states.
- `tools/verify_prisma_tablet_checkout_finalization_31.mjs`: static integration verifier.

## Expected flow

Cart -> Cobrar -> choose payment -> OK generar ticket -> API receives valid `items[]` -> sale closes -> modal closes -> ticket success appears.
