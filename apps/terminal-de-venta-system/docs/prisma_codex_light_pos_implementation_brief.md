# PRISMA_CODEX_LIGHT_POS_IMPLEMENTATION_BRIEF.md

**Project:** PRISMA POS / Terminal de Venta System  
**Repo root:** `F:\repos\hitech-os`  
**System root:** `F:\repos\hitech-os\apps\terminal-de-venta-system`  
**Target document path:** `F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_CODEX_LIGHT_POS_IMPLEMENTATION_BRIEF.md`  
**Audience:** Codex / implementation agent  
**Status:** `READY_FOR_CODEX_EXECUTION`  
**Primary goal:** implement the premium white PRISMA Light visual system across the Tablet operational surfaces with the existing theme selector, starting with POS/Vender but not stopping there, without breaking PRISMA Dark POS.

---

# 0. Executive instruction for Codex

Implement **PRISMA Light POS** as the premium white/frosted/blue visual skin for the POS interface while preserving the existing **PRISMA Dark POS** skin and keeping the selector.

This is a **visual skin implementation**, not a product redesign.

Do **not** change POS layout, sales logic, backend, Prisma schema, sync contracts, PC Backoffice behavior, or Mobile behavior unless a tiny non-visual compatibility change is absolutely required and explicitly reported.

The correct implementation model is:

```text
one POS component system
+ semantic tokens
+ data-prisma-skin="light|dark"
+ data-prisma-surface="pos"
+ selector runtime
+ screenshot QA
```

The wrong implementation model is:

```text
duplicate Light/Dark components
hardcoded blue/gold values
layout rewrite
PC/Mobile implementation creep
white flat repaint
```

---

# 1. Source-of-truth docs to read first

Read these docs before editing code. Treat this brief as the execution priority order.

## 1.1 Primary implementation docs

```text
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_TWO_SKIN_VISUAL_CONTRACT.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_SKIN_TOKEN_UNIFICATION_MAP.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_SKIN_SELECTOR_RUNTIME_SPEC.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_COMPONENT_SKIN_BINDING_GUIDE.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_VISUAL_QA_TWO_SKINS_CHECKLIST.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_TWO_SKIN_IMPLEMENTATION_RISK_REGISTER.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_TWO_SKIN_DOCS_MANIFEST.json
```

## 1.2 White reference docs

```text
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_LIGHT_POS_REFERENCE.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_LIGHT_UI_KIT.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_LIGHT_VISUAL_GUIDELINES.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_LIGHT_DESIGN_SYSTEM.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_LIGHT_POS_GOLDEN_VISUAL_SPECS.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_LIGHT_CANONICAL_STATUS.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_LIGHT_DOCS_MANIFEST.json
```

## 1.3 Dark preservation docs

```text
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_DARK_POS_GOLDEN_VISUAL_SPECS.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_DARK_DESIGN_SYSTEM.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_DARK_UI_KIT.md
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\PRISMA_VISUAL_GUIDELINES.md
```

## 1.4 Architecture boundary doc

```text
F:\repos\hitech-os\apps\terminal-de-venta-system\docs\architecture\PRISMA_ARQUITECTURA_FINAL_PC_TABLET.md
```

Use this only to avoid scope creep. Do not convert PC into POS. Do not make Tablet depend on PC.

---

# 2. Codex prior assessment integrated into this brief

The prior Codex assessment is accepted with caveats:

## 2.1 Accepted findings

- The current docs are enough to build a premium white POS skin, especially for Tablet/POS.
- The implementation should not be treated as a simple white repaint.
- The project already has the correct ingredients:
  - token contract;
  - selector runtime;
  - anti-FOUC guidance;
  - component binding guide;
  - Light specs;
  - Dark specs;
  - QA checklist.
- `PRISMA_LIGHT_POS_GOLDEN_VISUAL_SPECS.md` is the strongest document for visual fidelity.
- `PRISMA_SKIN_TOKEN_UNIFICATION_MAP.md` is enough to start, but needs optical tokens for blur/glow/inner highlight.
- `PRISMA_SKIN_SELECTOR_RUNTIME_SPEC.md` is implementable as `Apariencia` with `Oscuro / Claro / Sistema`.
- `PRISMA_COMPONENT_SKIN_BINDING_GUIDE.md` is the correct component strategy: one UI, semantic tokens, no duplicated dark/light component trees.

## 2.2 Accepted caveat

The two-skin docs currently scope the work to:

```text
Dark POS + Light POS only
```

They do **not** implement PC Backoffice or Mobile. That remains true for this execution.

## 2.3 Accepted improvement

Add a scoped surface attribute now:

```html
<html data-prisma-skin="light" data-prisma-surface="pos">
```

This does **not** mean implementing PC/Mobile skins now. It only prevents POS skin CSS from leaking into future PC/Mobile surfaces.

---

# 3. Scope

## 3.1 In scope

Implement the visual skin system for the Tablet operational UI, beginning with the POS/Vender surface but covering the other existing Tablet pages that share the same operational shell.

Core runtime scope:

```text
data-prisma-skin="light|dark"
data-prisma-surface="tablet-pos"
selector: Apariencia -> Oscuro / Claro / Sistema
semantic token mapping
optical token mapping
component token binding
Light visual polish across Tablet pages
Dark preservation across Tablet pages
screenshot QA per page family
```

Important: `tablet-pos` is the surface profile name for the whole Tablet operational experience. The page `/pos` or `Vender` is the first and most important screen, but not the only screen that must look polished.

## 3.2 Out of scope

Do not implement:

```text
PC Backoffice visual skin
Mobile visual skin
Slate skin
new product layout
new POS flow
backend changes
Prisma schema changes
sales logic changes
sync contract changes
shared-kernel changes
routing redesign
data model changes
```

## 3.3 Allowed tiny exceptions

A tiny compatibility edit is allowed only if required to mount attributes, import CSS, or prevent FOUC. If used, report it clearly.

Examples of allowed tiny exceptions:

```text
- setting html/body data attributes in layout
- importing a theme CSS file in an app shell/layout
- adding a tiny inline pre-hydration resolver
- adding a selector component to an existing top control area
```

---

# 4. Desired final visual result

## 4.1 Light POS must feel like this

```text
premium white POS
frosted panels
navy text
blue primary action
soft depth
clean product cards
right cart premium
large product imagery
dominant COBRAR button
same layout as POS reference
```

Light must **not** feel like:

```text
flat white dashboard
generic fintech UI
green checkout app
mobile-first stack
admin table UI
cheap SaaS repaint
```

## 4.2 Dark POS must remain protected

Dark POS must retain:

```text
dark premium glass
warm gold accent
large product cards
right cart
COBRAR dominant
gold active states
dark reference fidelity
```

Do not degrade Dark while implementing Light.

---

# 5. Runtime attributes

## 5.1 Required attributes

The final mounted POS UI should expose:

```html
<html
  data-prisma-skin="light"
  data-prisma-surface="pos"
>
```

or:

```html
<html
  data-prisma-skin="dark"
  data-prisma-surface="pos"
>
```

## 5.2 Legacy compatibility

If existing code uses:

```html
data-theme="prisma-light"
data-theme="prisma-dark"
```

keep compatibility during this implementation. Do not remove legacy selectors until migration is complete.

Recommended mapping:

```text
data-theme="prisma-light" -> data-prisma-skin="light"
data-theme="prisma-dark"  -> data-prisma-skin="dark"
```

---

# 6. Selector requirements

## 6.1 Visible label

Use:

```text
Apariencia
```

## 6.2 Options

```text
Claro
Oscuro
Sistema
```

Internal values:

```text
light
dark
system
```

## 6.3 Storage key

Use:

```text
prisma.pos.skin
```

Allowed stored values:

```text
light
dark
system
```

Invalid value fallback:

```text
light
```

## 6.4 Resolution order

```text
1. forced config/env if present
2. user localStorage preference
3. system preference if user selected system
4. app default
5. safe fallback = light
```

## 6.5 Anti-FOUC requirement

The skin must be applied before or at the earliest possible paint.

Avoid this failure:

```text
loads dark -> flashes -> changes to light after hydration
```

Use a minimal pre-hydration resolver if needed.

## 6.6 Selector placement

The selector must not interfere with selling.

Preferred placement:

```text
top-right controls / settings-like popover / compact appearance button
```

Hard rule:

```text
never cover or visually compete with COBRAR
never move cart
never move product grid
```

---

# 7. Token architecture

## 7.1 Components must consume semantic tokens

Correct:

```css
background: var(--prisma-surface-card);
color: var(--prisma-text-primary);
border-color: var(--prisma-border-soft);
box-shadow: var(--prisma-shadow-sm);
```

Wrong:

```css
background: #1557ff;
background: #e8bd67;
color: white;
```

## 7.2 Required semantic tokens

Ensure the implementation has usable values for both skins:

```text
--prisma-bg-app
--prisma-bg-canvas
--prisma-surface-sidebar
--prisma-surface-panel
--prisma-surface-card
--prisma-surface-cart
--prisma-surface-input

--prisma-text-primary
--prisma-text-secondary
--prisma-text-muted
--prisma-text-faint
--prisma-text-on-primary

--prisma-action-primary
--prisma-action-primary-hover
--prisma-action-primary-deep
--prisma-action-primary-soft
--prisma-action-primary-ring

--prisma-border-soft
--prisma-border-medium
--prisma-border-primary

--prisma-shadow-xs
--prisma-shadow-sm
--prisma-shadow-md
--prisma-shadow-lg
--prisma-shadow-primary

--prisma-radius-sm
--prisma-radius-md
--prisma-radius-lg
--prisma-radius-xl
--prisma-radius-pill

--prisma-state-success
--prisma-state-warning
--prisma-state-danger
--prisma-state-info
```

## 7.3 Required optical tokens

Add or normalize these because the white reference depends on material quality, not just color:

```text
--prisma-optical-panel-blur
--prisma-optical-panel-saturation
--prisma-optical-frost-opacity
--prisma-optical-card-inner-highlight
--prisma-optical-card-lift-shadow
--prisma-optical-primary-glow
--prisma-optical-primary-glow-soft
--prisma-optical-product-glow-opacity
--prisma-optical-product-glow-blur
--prisma-optical-product-pedestal-opacity
--prisma-optical-divider-opacity
--prisma-optical-focus-ring-width
--prisma-optical-focus-ring-alpha
```

## 7.4 Light skin optical target

Light POS should use:

```text
soft radial blue background
frosted white panels
subtle inner highlights
soft card lift shadows
blue primary glow
lower product glow intensity than dark
high contrast navy text
visible but delicate borders
```

## 7.5 Dark skin optical target

Dark POS should preserve:

```text
dark glass panels
warm gold accents
cinematic depth
stronger glow than light
cream text
gold CTA energy
```

---

# 8. Component binding targets

Codex must inspect the repo and map the real component names, but these conceptual components are critical.

Prioritize migration/binding in this order:

1. `PrismaAppShell`
2. `PrismaSidebar`
3. `PrismaNavItem`
4. `TopActionBar`
5. `SearchProductInput`
6. `ScanButton`
7. `CategoryRail`
8. `CategoryCircleItem`
9. `ProductGrid`
10. `ProductCard`
11. `ProductImageStage`
12. `CartPanel`
13. `CartLineItem`
14. `QuantityStepper`
15. `TotalsSummary`
16. `PayButton`
17. `SecondaryActionCard`
18. `StatusBadge`
19. `ShortcutHint`
20. `SkinSelector` / `AppearanceSelector`

## 8.1 Binding rule

Each component should have one implementation and read token values.

Avoid:

```text
LightProductCard
DarkProductCard
LightCartPanel
DarkCartPanel
```

Prefer:

```text
ProductCard + semantic tokens
CartPanel + semantic tokens
PayButton + semantic tokens
```

## 8.2 Exception rule

Skin-specific CSS overrides are allowed only when they are:

```text
small
scoped
visual-only
backed by a reference doc
```

Example scope:

```css
html[data-prisma-surface="pos"][data-prisma-skin="light"] [data-prisma-component="ProductCard"] { ... }
```

Do not use global selectors like:

```css
button { ... }
.card { ... }
aside { ... }
```

---

# 9. File discovery instructions

Before editing, inspect the repo to find the actual implementation points.

Likely areas to inspect:

```text
F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app
F:\repos\hitech-os\apps\terminal-de-venta-system\products\shared-ui
F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\app
F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\components
F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\src
```

Search for:

```text
data-theme
prisma-dark
prisma-light
data-prisma
data-prisma-component
ProductCard
CartPanel
PayButton
COBRAR
Apariencia
localStorage
```

Do not assume paths. Report actual files touched.

---

# 10. Implementation plan

## Phase -1 — Screen inventory before styling

Before styling, Codex must inventory the Tablet pages that exist and classify them by visual family.

Known page families from current screenshots and repo context:

```text
Vender / POS catalog + ticket
Ventas de hoy / sales report and ticket list
Inicio / operational dashboard and shift preparation
Turno / shift state and shift actions, if present
Other Tablet shell pages discovered in routes/navigation
```

For each discovered page, report:

```text
route/path
main component
shell component
CSS/module files
page family
critical visual components
needs Light pass: yes/no
needs Dark regression check: yes/no
```

Do not implement only the first page and claim the skin is complete.

## Phase 0 — Preflight and repo mapping

Produce a short mapping before editing:

```text
- POS route/path found
- shell/layout file found
- theme CSS file(s) found
- selector existing/not existing
- current skin mechanism found
- critical components found
- dark tokens found
- light tokens found
```

If the POS surface cannot be found, stop.

## Phase 1 — Runtime skin attributes

Ensure POS has:

```text
data-prisma-skin="light|dark"
data-prisma-surface="pos"
```

Keep legacy `data-theme` if needed.

## Phase 2 — Selector

Implement or normalize selector:

```text
Apariencia -> Claro / Oscuro / Sistema
storage -> prisma.pos.skin
fallback -> light
anti-FOUC -> required
```

## Phase 3 — Tokens

Create or update the token layer:

```text
semantic tokens
light values
dark values
optical tokens
legacy aliases
```

## Phase 4 — Component binding

Bind critical components to tokens.

Priority:

```text
AppShell / Sidebar / Nav active / Search / Category / ProductCard / Cart / Totals / PayButton
```

## Phase 5 — Light visual fidelity pass across page families

Polish Light first on `Vender / POS`, then apply the same visual language to the other Tablet operational pages without forcing the POS catalog layout onto them.

### 5.1 Vender / POS

```text
blue active states
frosted white panels
soft shadows
navy text
premium product cards
cart readability
dominant blue COBRAR
exact packshots where available
```

### 5.2 Ventas de hoy

```text
frosted report panels
white/light ticket list rows
navy text hierarchy
blue active navigation
soft section separators
export buttons using semantic tokens
empty/loading/error states in Light
```

### 5.3 Inicio / operational dashboard

```text
light hero panel
operational KPI cards
shift/action rows
status badges
alert cards
blue action buttons
clear hierarchy without POS product-card styling
```

### 5.4 Turno and other operational pages

```text
light shell consistency
frosted surfaces
semantic status colors
blue primary actions
clean forms/lists
no dark leftovers
no flat gray blocks
```

The goal is not to make every page identical. The goal is that every Tablet page belongs to the same premium Light system.

## Phase 6 — Dark preservation pass

Switch to dark and verify:

```text
gold active states
dark glass panels
warm total
COBRAR gold
dark product cards
same layout
```

## Phase 7 — Screenshot QA and report

Capture and report evidence.

---

# 11. Visual acceptance criteria

## 11.1 Light POS must pass

- [ ] Skin selector can select `Claro`.
- [ ] `data-prisma-skin="light"` is present.
- [ ] `data-prisma-surface="pos"` is present.
- [ ] Background is white/frosted premium, not flat white.
- [ ] Sidebar uses light/frosted treatment.
- [ ] Active nav uses blue.
- [ ] Search input is premium light, readable, high contrast.
- [ ] Category active state uses blue.
- [ ] Product cards are large, elevated, frosted/light, premium.
- [ ] Product images remain dominant.
- [ ] Cart remains fixed on the right.
- [ ] Total is visually dominant and blue.
- [ ] `COBRAR` is visually dominant and blue.
- [ ] Secondary actions remain visible but subordinate.
- [ ] No green checkout primary.
- [ ] No fintech generic look.
- [ ] No layout movement.

## 11.2 Dark POS must pass

- [ ] Skin selector can select `Oscuro`.
- [ ] `data-prisma-skin="dark"` is present.
- [ ] Dark background remains premium.
- [ ] Active nav remains gold/warm.
- [ ] Total remains gold/warm.
- [ ] `COBRAR` remains gold/warm.
- [ ] Product cards remain dark/glass.
- [ ] Cart remains fixed on the right.
- [ ] No layout movement.

## 11.3 Selector must pass

- [ ] `Claro` persists after reload.
- [ ] `Oscuro` persists after reload.
- [ ] `Sistema` resolves via OS preference.
- [ ] Invalid storage value falls back safely.
- [ ] Selector does not cover `COBRAR`.
- [ ] Selector does not move layout.
- [ ] No visible FOUC.

---

# 12. Screenshot acceptance matrix

Codex must provide screenshots or screenshot paths for every page family it touches.

| Screenshot | Required state | Purpose |
|---|---|---|
| `light-vender-full` | Light skin, Vender/POS full screen | Compare to white reference |
| `dark-vender-full` | Dark skin, Vender/POS full screen | Confirm dark POS not broken |
| `light-product-card-closeup` | Light skin | Card depth, image stage, typography |
| `light-cart-closeup` | Light skin | Cart material, total, COBRAR |
| `light-ventas-hoy-full` | Light skin, Ventas de hoy | Ensure reports/list pages are also polished |
| `dark-ventas-hoy-full` | Dark skin, Ventas de hoy | Confirm dark report page not broken |
| `light-inicio-full` | Light skin, Inicio | Ensure dashboard/shift page is also polished |
| `dark-inicio-full` | Dark skin, Inicio | Confirm dark dashboard page not broken |
| `selector-open` | Any skin | Selector placement and labels |
| `light-focus-state` | Light skin | Focus/hover/readability |

If screenshots cannot be captured, stop and report why.

---

# 13. Validation commands

Codex must discover actual package scripts first. Prefer existing repo scripts over invented commands.

Likely validation commands include, if available:

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" --filter @hitech/tablet run typecheck
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" --filter @hitech/tablet run build
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" --filter @hitech/mobile run typecheck
```

Do not fail the task just because one guessed command does not exist. Inspect `package.json` scripts and report the exact commands used.

Minimum validation report:

```text
STATUS: DONE | READY_WITH_CAVEATS | BLOCKED
FILES_CHANGED: <count>
DIFF_SUMMARY: <short summary>
TEST_COMMANDS: <commands run>
TEST_RESULTS: <passed/failed/skipped with reason>
SCREENSHOTS: <paths>
CAVEATS: <only real caveats>
```

---

# 14. Stop conditions

Stop and report `BLOCKED` before large edits if any of these happen:

1. POS shell/route cannot be found.
2. Selector architecture is incompatible with current app shell.
3. Dark skin depends on hardcoded styles that would be broken by token migration.
4. More than 20 critical files require rewrite.
5. Any requested change would touch backend, Prisma, DB, sync contracts, or shared-kernel.
6. Screenshots cannot be produced and there is no alternative visual proof.
7. Build/typecheck fails from unrelated pre-existing errors and blocks confidence.
8. PC/Mobile implementation is required to continue.

Do not push through a messy global refactor. Stop and report.

---

# 15. Required final Codex response format

Codex must respond with:

```text
STATUS: DONE | READY_WITH_CAVEATS | BLOCKED

WHAT CHANGED
- ...

FILES CHANGED
- full path
- full path

SKIN RUNTIME
- data-prisma-skin: implemented / already existed / blocked
- data-prisma-surface="pos": implemented / already existed / blocked
- selector: implemented / updated / already existed / blocked

VISUAL RESULT
- Light: ...
- Dark: ...

VALIDATION
- command: ...
  result: ...
- command: ...
  result: ...

SCREENSHOTS
- light-full-pos: <path>
- dark-full-pos: <path>
- selector-open: <path>

CAVEATS
- ...

NEXT SAFE STEP
- one sentence
```

---

# 16. Hard no list

Do not:

- implement PC Backoffice skin;
- implement Mobile skin;
- implement Slate;
- remove Dark skin;
- remove selector;
- hardcode blue/gold into components;
- duplicate component trees for Light/Dark;
- move POS layout;
- change sales behavior;
- change Prisma schema;
- change backend/API contracts;
- change sync/shared-kernel;
- use broad global CSS selectors;
- claim visual completion without screenshots.

---

# 17. Short pasteable Codex instruction

Use this as the direct Codex task prompt if needed:

```text
Implement PRISMA Light as the premium white/frosted/blue visual system across the Tablet operational pages, while preserving PRISMA Dark and the selector.

Read first:
- docs/PRISMA_CODEX_LIGHT_POS_IMPLEMENTATION_BRIEF.md
- docs/PRISMA_TWO_SKIN_VISUAL_CONTRACT.md
- docs/PRISMA_SKIN_TOKEN_UNIFICATION_MAP.md
- docs/PRISMA_SKIN_SELECTOR_RUNTIME_SPEC.md
- docs/PRISMA_COMPONENT_SKIN_BINDING_GUIDE.md
- docs/PRISMA_VISUAL_QA_TWO_SKINS_CHECKLIST.md
- docs/PRISMA_LIGHT_POS_GOLDEN_VISUAL_SPECS.md
- docs/PRISMA_LIGHT_DESIGN_SYSTEM.md
- docs/PRISMA_DARK_POS_GOLDEN_VISUAL_SPECS.md

Scope:
- Tablet operational visual skin only.
- Start with Vender/POS, but also cover existing Tablet pages like Inicio, Ventas de hoy, Turno, and any other route in the Tablet operational shell discovered during preflight.
- Keep selector.
- Use data-prisma-skin="light|dark".
- Add/use data-prisma-surface="tablet-pos" for scoped CSS.
- Use semantic tokens and optical tokens.
- One component set, two skins.
- No PC Backoffice, no Mobile, no Slate, no backend, no Prisma, no sales logic.

Deliver:
- code changes only where needed for Tablet visual skin/runtime/selector;
- validation commands and results;
- screenshots for Light and Dark across Vender/POS, Inicio, Ventas de hoy, selector open;
- status report in the required format.

Stop if scope expands beyond POS visual skin or if screenshots cannot be produced.
```

