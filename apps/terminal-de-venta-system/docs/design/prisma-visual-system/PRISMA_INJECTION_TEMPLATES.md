# PRISMA Injection Templates

Status: living structural base
Source contract: visualcat final 1006 1701
Scope: shared UI templates only

## Purpose

This directory defines safe starter templates for future PRISMA visual work. The templates are not runtime code and must not be copied directly into a production screen without a visual change manifest, route ownership, and validation evidence.

## Template Inventory

| Template | Intended Use | Status |
|---|---|---|
| `new-tablet-screen.template.md` | Plan a Tablet screen without breaking local-sale autonomy. | ready |
| `new-pc-screen.template.md` | Plan a PC/backoffice screen without turning PC into POS. | ready |
| `new-mobile-screen.template.md` | Plan a Mobile companion screen without POS takeover. | ready |
| `new-shell.template.md` | Register a shell before implementation. | ready |
| `new-card.template.md` | Register a card component before implementation. | ready |
| `new-panel.template.md` | Register a panel component before implementation. | ready |
| `new-state.template.md` | Register loading, empty, error, disabled, focus, and success states. | ready |
| `new-data-display.template.md` | Register metric/table/list display components. | ready |
| `migrate-legacy-css.template.md` | Move legacy visual rules into governed tokens and recipes. | ready |
| `split-choncho-css.template.md` | Break oversized CSS modules into owned layers. | ready |
| `add-future-component-family.template.md` | Reserve future component families without marking them live. | ready |
| `new-background-recipe.template.md` | Register background intent without adding public runtime copies. | ready |

## Required Use Rules

1. Start with the matching surface adapter in `products/shared-ui/prisma/adapters/`.
2. Register component, token, recipe, or migration intent in `config/prisma-visual-system/`.
3. Do not add global CSS background patches.
4. Do not add `!important` as the final solution.
5. Do not reference `products/0.backgrounds` as a runtime public URL.
6. Mark render evidence as `SKIPPED_NO_LIVE_SERVER` when no live server already exists.

## Validation

Run the VisualCat validators after adding or modifying any template:

```powershell
node apps/terminal-de-venta-system/tools/prisma-visual-system/validate-registries --out-dir F:\descargasf\visualcat-validation
```
