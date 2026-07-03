# TABLET MAMASTROPHIC INITIAL STATUS

Date: 2026-07-03
Repo: `F:\repos\hitech-os`
App: `apps/terminal-de-venta-system/products/tablet/app`

## Authority Read

Read before source patch:

- `apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md`
- `F:\descargasf\PRISMA_PRODUCT_SURFACE_SPEC_CODEX_0207.md`
- `F:\descargasf\PRISMA_TABLET_VISUAL_PREMIUM_SPEC_CODEX_0207.md`
- `AGENTS.md`

Nested `AGENTS.md` files checked and not found under:

- `apps/terminal-de-venta-system/AGENTS.md`
- `apps/terminal-de-venta-system/products/tablet/AGENTS.md`
- `apps/terminal-de-venta-system/products/tablet/app/AGENTS.md`

## Package And Validation Notes

- Root package manager: `pnpm@9.15.0`.
- Tablet app: Next 16.1.6, React 18.3.1.
- Tablet `typecheck`, `build`, and `dev` run `prisma:generate`; do not run them hot.
- Existing safe static verifiers include Tablet-local `verify:tabrest-*`, `verify:tablet-visual-layer-cleanup`, `verify:tablet-sync-dispatcher`, and repo `verify:zero-important`.
- No dev server will be started for this pass.
- No process will be killed.
- No ports will be freed.

## Current Product Truth

- Tablet navigation source of truth is `components/tablet-shell/tablet-nav.ts`, backed by `src/navigation/tablet-page-contracts.ts` and `tablet-product-navigation.manifest.json`.
- Current dock final routes are `/pos`, `/shift`, `/stock`, `/sales/today`, `/returns`, `/sync`, `/settings/license`.
- Top navigation is already hidden by a prior `TABNP1_SHELL_CONTEXT_NAV_0207` shell patch.
- Lab routes remain declared as lab/internal and must stay hidden from final nav.
- POS already has real sale, cart, held-ticket, checkout, product search, product resolve, and product-create handoff to Catalog.
- Catalog has real product create/update through `/api/pos/products/create` and `/api/pos/products/update`.
- Shift has real open/close/current APIs.
- Returns has real contextual return creation through closed tickets.
- Sync has real panel, dispatch, retry, PC health, and catalog pull endpoints.
- Offline has real audit/export links.
- Exportaciones has real export endpoints but needs tile-by-type product treatment.
- License is server-rendered from the canonical Tablet license governor and must not duplicate license engines.

## Initial Risk Classification

- High risk: modifying POS sale/payment flow, shift open/close, return creation, sync dispatch, license service logic.
- Medium risk: adding UI wrappers/tiles around existing real routes/actions.
- Low risk: adding static verifiers and docs.

## Initial Scope Decision

Touch only:

- Tablet app components/CSS when directly needed.
- Tablet app tools/verifiers.
- Terminal product docs under `docs/product/tablet-mamastrophic`.
- Root `tools/quality` only for required repo-level verifiers if needed by the user request.

Do not touch:

- PC
- Mobile
- Web
- Control Center
- Shared UI unless a direct Tablet dependency proves unavoidable
- Prisma schema/generate/migrations
