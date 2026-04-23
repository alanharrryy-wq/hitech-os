# GOLDEN SPEC UI SHELL V1
Project: `apps/external_interaction_template`  
Version: `v1.0`  
Status: `APPROVED`  
Effective date: `2026-04-13`  
Primary intent: lock a single visual and functional contract across all routes and all canonical themes, with explicit priority on persistent side panels and ultra-minimal chrome bar.

---

## 1) Scope

This specification governs:

1. Global shell composition and route composition grammar.
2. Sidebar behavior and proportions.
3. Chrome bar minimization rules.
4. Main workbench and contextual side stack behavior.
5. Theme consistency across `aurora`, `solstice`, `neon`.
6. Motion, accessibility, and performance constraints.
7. Acceptance criteria to prevent visual drift.

This specification does not redefine business rules, schema logic, API contracts, or route paths.

---

## 2) Non-negotiable visual philosophy

The product must read as:

1. Operational workspace.
2. Persistent shell-first UI.
3. Task-first main viewport.
4. Premium layered chrome with controlled glow.
5. Atmospheric motion that supports readability.

The product must not read as:

1. Hero landing page.
2. Marketing page inside app routes.
3. Horizontal-primary-nav workspace.
4. Theme-specific app rewrites.

---

## 3) Ownership boundaries

1. `components/layout/app-shell.tsx` owns shell composition only.
2. Route-level layout belongs to route modules/components.
3. `FlowRunner` or equivalent engines own interaction/business state, not shell grammar.
4. `src/lib/ui/theme-system/*` owns tokens and backdrop descriptors.
5. `app/globals.css` owns reusable recipes and class contracts.
6. `shell-system` registries/manifests remain source of truth for nav/actions/widgets.

No route-specific hacks are allowed in shell core.

---

## 4) Global shell contract

### 4.1 Desktop composition

Required shell structure:

1. Persistent left rail.
2. Main column with minimal chrome bar and task viewport.
3. Optional right context panel by shell model.

Layout rhythm:

1. Shell frame visible at all times.
2. Main viewport always visually dominant.
3. Context information must stay secondary.

### 4.2 Width and spacing contract

Desktop targets:

1. Sidebar expanded width: `240-256px`.
2. Sidebar collapsed width: `72-88px`.
3. Route context stack width: `300-340px`.
4. Primary gap cadence: `8, 12, 16, 24`.

### 4.3 Responsive contract

1. Desktop: persistent sidebar and compact chrome bar.
2. Tablet: sidebar remains available with controlled density.
3. Mobile: sidebar becomes drawer, but shell grammar remains unchanged.

---

## 5) Sidebar rail contract (highest priority)

### 5.1 Required sections

Top-to-bottom order:

1. Brand cluster.
2. Workspace cluster.
3. Primary navigation.
4. Secondary navigation.
5. Quick actions.
6. Utility actions.
7. Footer controls.

### 5.2 Interaction requirements

1. Active item must have unmistakable state.
2. Hover/focus/active states must remain theme-consistent.
3. Collapsed mode must preserve icon clarity and tooltips.
4. Keyboard navigation must support full reachability.

### 5.3 Visual requirements

1. Rail is glassy but not blurry to the point of illegibility.
2. Edge keylines and subtle depth are required.
3. Noise/glow must not compete with active nav affordances.
4. Section groups must feel structured, not stacked random cards.

### 5.4 Forbidden patterns

1. Sidebar hidden on desktop.
2. Replacing sidebar with top horizontal primary nav.
3. Hero sections above sidebar that dominate first read.

---

## 6) Chrome bar minimal contract (highest priority)

### 6.1 Hard cap

Chrome bar is a utility strip, not a page header.

1. Height target: `44-48px`.
2. Single row only.
3. Content density must stay compact and scannable.

### 6.2 Allowed controls

Allowed controls:

1. Search.
2. Language switch.
3. Theme switch.
4. Utility trigger(s).
5. Profile/avatar.

### 6.3 Forbidden controls

1. Large title blocks.
2. Hero copy/subtitle stacks.
3. Chip clouds dominating row.
4. Route-specific promotional messaging.

### 6.4 Functional behavior

1. Search remains first utility.
2. Locale/theme changes are immediate and persistent.
3. Utilities remain reachable without shifting layout.

---

## 7) Main viewport and workbench contract

### 7.1 Reading order

Required route reading order:

1. Shell orientation.
2. Compact route summary strip.
3. Primary work surface.
4. Context side stack.

### 7.2 Primary work surface

1. One dominant work card for active task.
2. Engine content lives inside this surface.
3. No full-width hero block before work surface.

### 7.3 Context side stack

1. Sticky on desktop.
2. Hosts session, progress, schema/meta, and support context.
3. Must remain secondary in visual weight.

---

## 8) Route grammar contract

### 8.1 Flow routes (`/flow/*`)

Mandatory composition:

1. Compact summary strip.
2. Main card containing flow engine.
3. Context stack containing resume/progress/meta cards.

Flow routes must not look like landing pages.

### 8.2 Inbox routes (`/inbox`)

1. Compact route summary.
2. Queue controls strip.
3. Task cards with consistent action placement.

### 8.3 Record routes (`/record/*`)

1. Detail work surface first.
2. Operational side context second.
3. Timeline and controls maintain shell rhythm.

### 8.4 Sync routes (`/sync`)

1. Operational diagnostics first.
2. Job/event sections aligned to same spacing grammar.
3. No isolated visual language unique to sync.

---

## 9) Surface and component recipe contract

Required recipe families:

1. `surface-shell`
2. `surface-panel`
3. `surface-elevated`
4. `surface-muted`
5. `ui-notice`
6. `ui-badge`
7. `shell-chip`

Requirements:

1. Surface hierarchy must be obvious.
2. Keylines and depth must stay restrained.
3. Recipes must be reused, not cloned per route.

---

## 10) Theme contract by persona

All themes share identical layout grammar. Only visual persona changes.

### 10.1 `aurora` (Nebula Midnight)

1. Deep cool cosmic base.
2. Blue-violet restrained glow.
3. High legibility against dark surfaces.

### 10.2 `solstice` (Pearl Mist)

1. Blue mineral mist identity.
2. Never pure flat white page.
3. Soft but readable contrast.

### 10.3 `neon` (Nova Rose)

1. Warm rose-magenta premium tone.
2. Controlled bloom, no candy saturation.
3. Action contrast remains crisp.

---

## 11) Motion and atmosphere contract

### 11.1 Required motion language

1. Slow drift.
2. Subtle layered shimmer.
3. Transform/opacity-first animations.

### 11.2 Forbidden motion language

1. Chaotic particle storms.
2. Aggressive parallax.
3. High-amplitude blur pulsing.

### 11.3 Accessibility

1. `prefers-reduced-motion` must reduce decorative effects.
2. Motion must never block task readability.

---

## 12) Interaction and accessibility contract

### 12.1 State coverage

Each route must expose valid states where relevant:

1. Hover.
2. Focus visible.
3. Active.
4. Disabled.
5. Loading.
6. Empty.
7. Error.

### 12.2 Keyboard requirements

1. Sidebar and chrome controls are keyboard reachable.
2. Focus order is deterministic.
3. No hidden focus traps in drawers/panels.

---

## 13) Performance and rendering contract

1. Visual polish cannot degrade interaction responsiveness.
2. Atmosphere layers must stay lightweight.
3. Blur and shadow stacks must remain controlled.
4. No animation design that forces expensive continuous layout thrash.

---

## 14) Functional behavior contract for panel systems

### 14.1 Sidebar

1. Collapse/expand state must persist per session.
2. Current route state remains visible in collapsed mode.
3. Navigation actions must not reflow chrome bar unexpectedly.

### 14.2 Context stack

1. Sticky behavior only at desktop breakpoints.
2. On smaller viewports, stack becomes ordered below main surface.
3. Card actions remain tappable and readable.

### 14.3 Utility drawer

1. Utility drawer opens without displacing main shell.
2. Close behavior must be deterministic (button, backdrop, escape).

---

## 15) Acceptance gate (required for approval)

A route/theme slice is accepted only if all are true:

1. Shell dominance is intact.
2. Sidebar proportion and behavior match contract.
3. Chrome bar remains minimal.
4. Main work surface is first-class.
5. Context side stack is present and usable.
6. Theme persona is correct without breaking grammar.
7. Motion is alive but restrained.
8. Accessibility states are complete.

If one fails, the slice is not accepted.

---

## 16) Change control

1. Any deviation requires explicit update to this spec.
2. Spec changes must include rationale, impact, and acceptance delta.
3. Silent visual drift is treated as regression.

---

## 17) Approval statement

This `GOLDEN_SPEC_UI_SHELL_V1` is approved as the repository-level contract for UI shell behavior and visual execution for the canonical themes and route families in this app.

