# Visual Authority

This file defines what is allowed to guide future visual work.

## Authority states

- `core`: live source of truth.
- `core-limited`: allowed only in a narrow role.
- `recipe`: valuable source material that must be distilled before runtime use.
- `archive`: keep as history, do not use directly for new work.
- `deprecated`: do not use for new work.
- `blocked`: do not touch/use unless explicitly scoped.
- `review`: needs a human decision.

## Current decisions

| Name | Status | Kind | Action |
|---|---|---|---|
| visualcat-config | core | governance | keep and validate |
| visualcat-docs | core | documentation | keep and condense names later |
| visualcat-tools | core | tools | keep and expand |
| shared-ui-prisma-components | core | component-base | keep |
| shared-ui-prisma-effects | core | effects | keep |
| shared-ui-prisma-tokens | core | tokens | keep |
| visual-os-recipes | core | recipes | keep but align naming |
| tablet-layer-map | core | evidence | keep as audit evidence |
| tablet-visualqa | core | evidence | keep as evidence |
| radix-primitives | core | library | keep as preferred primitive source |
| ogl-effects | core-limited | library | keep limited |
| liquid-glass-docs | recipe | material | distill |
| cloudglass-docs | recipe | material | distill |
| glass-pill-capsules | recipe | component-effect | distill |
| surface-governor-pilots | archive | history | archive index |
| fuji-legacy | deprecated | background | block new references |
| soft-gray-clouds | deprecated | background | block new references |
| duplicated-logo-assets | review | brand | brand curation |
| visual-os-pulse | blocked | surface-area | block outside explicit scope |

## Hard rule

New screens should use `VisualCat + Surface Adapter + Recipe + Tokens + Layer Budget`, not historical pilot docs or local one-off CSS.
