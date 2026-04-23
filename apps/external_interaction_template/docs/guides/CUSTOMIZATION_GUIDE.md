# CUSTOMIZATION GUIDE
**Scope:** safe visual customization without breaking schema/business/runtime behavior.

## 0. Golden spec first

Before any customization, align with:

1. `docs/architecture/GOLDEN_SPEC_UI_SHELL_V1.md`
2. `docs/architecture/GOLDEN_SPEC_ACCEPTANCE_MATRIX_V1.md`
3. `docs/architecture/GOLDEN_SPEC_APPROVAL_RECORD_V1.md`

Customization is valid only if it keeps compliance with the approved golden spec set.

## 1. Core rule

Visual changes must stay in visual ownership layers:

- `src/lib/ui/theme-system/*`
- `app/globals.css`
- `components/ui/*`
- `components/layout/*`

Do not change API contracts, schema semantics, state machine rules, persistence behavior, or route contracts to solve appearance tasks.

---

## 2. New theme architecture (where to edit)

## A. Create/change a theme

Edit:

- `src/lib/ui/theme-system/theme-specs.ts`

Each theme has full typed sections:

- `meta`
- `color`
- `material`
- `chrome`
- `motion`
- `backdrop`
- `widgets`
- `typography`
- `dataViz`

This is the only place where theme identity should be authored.

## B. Theme IDs, fallback, selector visibility

Edit:

- `src/lib/ui/theme-system/theme-registry.ts`

Owns:

- default and fallback (`solstice`)
- selector entries
- persistence key compatibility
- reserved slot visibility (`slot_01`, `slot_02`)

Reserved slot toggles:

- `NEXT_PUBLIC_EIT_THEME_SLOT_01_VISIBLE=1`
- `NEXT_PUBLIC_EIT_THEME_SLOT_02_VISIBLE=1`

Use env flags instead of hardcoding visibility in components.

## C. DOM token application

Edit:

- `src/lib/ui/theme-system/css-vars.ts`

If you add a new token section or token key, wire it here so `applyThemeToDocument` exports it as CSS variables.

## D. Backdrop motion and particles

Edit:

- `src/lib/ui/theme-system/backdrop-descriptors.ts`
- `components/layout/ambient-backdrop.tsx`

Rules:

- keep descriptors deterministic (seeded/precomputed)
- keep animation transform/opacity-first
- keep decorative motion subtle
- preserve reduced-motion behavior

---

## 3. Global visual recipes

Edit:

- `app/globals.css`

Use this file to define reusable recipe classes that consume theme vars:

- shell/chrome recipes (`shell-*`)
- material surfaces (`surface-*`)
- primitive recipes (`ui-button*`, `ui-field`, `ui-pill`, `ui-badge`)
- feedback recipes (`ui-notice*`)
- ambient layer classes

Do not move business logic here.

---

## 4. Primitive-first customization order

When implementing broad visual changes:

1. Update typed tokens in `theme-specs.ts`.
2. Ensure vars are exported in `css-vars.ts`.
3. Update recipe classes in `globals.css`.
4. Update primitives in `components/ui/*`.
5. Touch feature screens only for composition gaps.

This order avoids per-screen hardcoded drift.

---

## 5. Shell slot model and injection

Slot contracts are defined in:

- `src/lib/ui/shell-system/types.ts`

Validation gates:

- `src/lib/ui/shell-system/validators.ts`

Composition point:

- `src/lib/ui/shell-system/composeShellModel.ts`

Runtime rendering:

- `components/layout/app-shell.tsx`
- `components/layout/shell/*`

The shell receives resolved slot payloads from registries/manifests. Customize shell content by editing client manifests and registries, not by hardcoding labels inside shell components.

### Add or edit navigation safely

1. Edit `src/lib/ui/shell-system/client/client.navigation.ts`.
2. Keep `slot`, `mobilePolicy`, `collapsedLabelPolicy`, `permissions`, and `visibility` explicit.
3. Validate route prefixes against `moduleRegistry`.

### Add or edit actions safely

1. Edit `src/lib/ui/shell-system/client/client.actions.ts`.
2. Assign to one of:
   - `quickActionSlot`
   - `contextActionSlot`
   - `utilitySlot`
3. Keep permission and visibility policies aligned with module ownership.

### Add or edit widgets safely

1. Edit `src/lib/ui/shell-system/client/client.widgets.ts`.
2. Assign to one of:
   - `contextualPanelSlot`
   - `quickFiltersSlot`
   - `pluginTraySlot`
3. Keep `componentId` stable for future renderer injection.

### Add or edit module composition safely

1. Edit `src/lib/ui/shell-system/registries/moduleRegistry.ts`.
2. Reference existing nav/action/widget IDs.
3. Keep `routePrefix` and permissions aligned with route contracts.

---

## 6. Reserved theme slots workflow

Two internal scaffolds are ready:

- `slot_01`
- `slot_02`

They are structurally complete but hidden by default. To activate safely:

1. set env visibility flag to `1`
2. update slot spec values in `theme-specs.ts`
3. verify selector behavior and persistence
4. remove placeholder labels only when theme is production-ready

---

## 7. Rollback (simple)

From repo root, rollback only this app to last committed state:

```powershell
git restore --source=HEAD --worktree --staged apps/external_interaction_template
```

Rollback only the visual system files:

```powershell
git restore --source=HEAD --worktree --staged `
  apps/external_interaction_template/app/layout.tsx `
  apps/external_interaction_template/app/globals.css `
  apps/external_interaction_template/components/layout/app-shell.tsx `
  apps/external_interaction_template/components/layout/ambient-backdrop.tsx `
  apps/external_interaction_template/src/lib/ui/theme-catalog.ts `
  apps/external_interaction_template/src/lib/ui/runtime.ts `
  apps/external_interaction_template/src/lib/ui/theme-system `
  apps/external_interaction_template/components/ui `
  apps/external_interaction_template/docs/architecture/FRONTEND_VISUAL_MAP.md `
  apps/external_interaction_template/docs/guides/CUSTOMIZATION_GUIDE.md
```

---

## 8. Validation checklist

After customization, run:

1. `pnpm -C apps/external_interaction_template run typecheck`
2. `pnpm -C apps/external_interaction_template run test`
3. `pnpm -C apps/external_interaction_template run build`

Then verify:

- `aurora`, `solstice`, `neon` still available
- default stays `solstice` unless intentionally changed
- persistence still works with existing key
- reduced motion still respected
- no business logic regressions introduced by visual edits
