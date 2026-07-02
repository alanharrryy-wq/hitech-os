# TABREST_NON_POS Initial Status

Date: 2026-07-02
Repo: `F:\repos\hitech-os`
Scope: PRISMA Tablet remaining non-POS surfaces.

## Current Base

- Branch status before TABREST exploration was clean on `main...origin/main`.
- A later user correction asked to restore the cobro surface to light colors before continuing. That produced three intentional dirty files listed in `TABREST_NON_POS_PREEXISTING_DIRTY_FILES.md`.
- No TABREST non-POS source patch has been applied yet.
- No dev server was started.
- No process was killed.
- No commit or push was made for TABREST.

## Required Docs Read

- `F:\descargasf\PRISMA_PRODUCT_SURFACE_SPEC_CODEX_0207.md`
- `F:\descargasf\PRISMA_TABLET_VISUAL_PREMIUM_SPEC_CODEX_0207.md`
- Repo AGENTS instructions supplied in the chat for `F:\repos\hitech-os`.

## Relevant Existing Authority

- `apps/terminal-de-venta-system/products/tablet/app/src/navigation/tablet-page-contracts.ts`
- `apps/terminal-de-venta-system/products/tablet/app/src/navigation/tablet-product-navigation.manifest.json`
- `apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/tablet-nav.ts`
- `apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx`

## Initial Route Findings

- Final nav routes are `/pos`, `/shift`, `/stock`, `/sales/today`, `/returns`, `/sync`, and `/settings/license`.
- Secondary routes include `/catalog`, `/existencias`, `/inventory/low-stock`, `/sales/history`, `/offline`, and `/settings/export`.
- Internal/support candidates include `/events/outbox` and `/prisma-pulse`; they must not appear as final navigation or home-first actions.
- `/settings/data` redirects to `/settings/license`.
- `/checkout` is a sale step and remains outside TABREST non-POS polish.

## Initial UI Findings

- Home is too dense for a one-glance Tablet start surface and still includes runtime/support-style language.
- Shift shows open and close panels with similar weight and includes informal copy that should be replaced.
- Stock/catalog has a strong foundation but keeps filters/export controls more visible than the final spec wants.
- Sales today/history are functional, but export actions are too prominent by default.
- Returns are mostly human-readable, but confirmation/reason flow can be made clearer.
- Sync/offline surfaces mix operator actions with diagnostics/export details too early.
- License is mostly readonly and human-friendly, but support detail must stay secondary.
- `/events/outbox` is currently a legacy support route with technical labels such as event/topic/ACK.
- `/prisma-pulse` is visibly branded/technical and should be hidden or renamed if kept.

## Validation Already Run In This Turn

These were for the user-requested cobro correction before returning to TABREST:

- `pnpm run verify:tablet-cobro-light-amounts-0207` from `products/tablet/app`: PASS.
- `pnpm run verify:zero-important` from `products/tablet/app`: PASS.

TABREST-specific validation has not been run yet because no non-POS source patch has been applied.
