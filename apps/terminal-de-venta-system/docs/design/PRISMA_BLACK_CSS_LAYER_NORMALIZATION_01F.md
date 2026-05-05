# PRISMA Black CSS Layer Normalization 01F

**Package:** `PRISMA_BLACK_CSS_LAYER_NORMALIZATION_01F`  
**Scope:** CSS governance normalization, markers, documentation, contract and checker.  
**Visual intent:** no intentional redesign.  
**Rule:** preserve current UI while making layer ownership explicit.

## 1. Purpose

This pass does not try to make PRISMA Black prettier. It makes the current CSS easier to govern before the next premium visual pass.

The current visual stack already has haze, glass, glow and blend effects. Adding more effects now would make the layers harder to reason about. 01F therefore adds ownership markers and validation instead of new decoration.

## 2. Governance source used

This pass adapts the governance ideas from the uploaded transparency package:

- derive, do not invent;
- semantics over decoration;
- bounded motion hierarchy;
- blur and glow budgets;
- deterministic layer ownership;
- URL/debug layer concepts are treated as conceptual governance only, not implemented in PRISMA in this pass.

The Keystone layer IDs are mapped conceptually to PRISMA ownership zones:

| Governance concept | PRISMA 01F zone |
|---|---|
| `stage.haze`, `stage.vignette`, `stage.noise`, `stage.horizon` | background |
| `card.blur`, `card.innerStroke`, `card.specular`, `card.shadowAmbient` | panel/card |
| `motion.enabled` | motion |
| semantic accent budget | CTA/active/status |

## 3. Layer ownership model

| PRISMA layer | Owner | Rule |
|---|---|---|
| Background | theme/shared components/global shells | one scene per screen |
| Panel | app shell, sidebar, hero, ticket/catalog panels | interprets the background with glass |
| Card | product/KPI/module/status cards | frames content; does not create weather |
| Product stage | POS product/pedestal areas | allowed local glow island |
| CTA | checkout/add/primary action | semantic emphasis only |
| Active state | nav/current/selected states | semantic emphasis only |
| Motion | background or micro interactions | no new hero motion in 01F |

## 4. Inventory snapshot

| File | Role | Lines | radial-gradient | mix-blend-mode | backdrop-filter | box-shadow |
|---|---:|---:|---:|---:|---:|---:|
| `products/shared-ui/prisma/tokens/prisma-theme.css` | `tokens` | 417 | 62 | 0 | 0 | 0 |
| `products/shared-ui/prisma/components/prisma-components.css` | `shared-components` | 677 | 14 | 11 | 24 | 15 |
| `products/tablet/app/components/pos/pos.module.css` | `tablet-pos` | 1399 | 18 | 5 | 32 | 30 |
| `products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css` | `tablet-shell` | 658 | 3 | 3 | 16 | 13 |
| `products/pc/app/app/globals.css` | `pc-globals` | 1207 | 12 | 3 | 18 | 15 |
| `products/tablet/app/app/globals.css` | `tablet-globals` | 484 | 0 | 0 | 2 | 7 |

## 5. What changed

- Added 01F ownership markers to the six active CSS files.
- Added this design note.
- Added a QA checklist for 01F.
- Added a JSON contract for CSS layer normalization.
- Added `verify_prisma_black_css_layer_normalization_01f.mjs`.
- Added a manifest for the package.

## 6. What did not change

- No layout changes.
- No TS/TSX changes.
- No route changes.
- No data changes.
- No new motion.
- No new background.
- No stronger glass.
- No aggressive dedupe of gradients or blend modes.

## 7. Explicit deferrals to 01G

These items are intentionally deferred because changing them can alter visual output:

1. Reducing `radial-gradient` count in `prisma-theme.css`.
2. Replacing `mix-blend-mode` usage in `prisma-components.css`.
3. Collapsing duplicate haze/glow values into fewer material recipes.
4. Introducing runtime layer toggles or debug URL flags.
5. Making the final premium aesthetic pass.

## 8. Acceptance

01F is accepted when:

- all six CSS files contain the 01F marker;
- the 01F contract exists;
- the 01F checker runs;
- the 01E checker still runs;
- no functional or layout files are touched.
