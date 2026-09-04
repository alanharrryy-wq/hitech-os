# PRISMA Visual Control System v1

PRISMA Visual Control System v1 is the repo-native control layer for future visual changes across the governed PRISMA product surfaces. It does not redesign the UI. It maps which files own a screen, region, layer, style, asset, and editable visual slot before any visual patch is attempted.

## Scope

The system covers the currently governed surfaces registered by UI Certainty:

- Chart Lab
- PRISMA Web/Edit
- PRISMA Tablet Core
- PRISMA PC Backoffice
- PRISMA Mobile Adder
- Control Center
- Shared UI / tooling when ownership is real

The authoritative inputs are:

- `.prisma-ui/registry.json`
- `.prisma-ui/surfaces.json`
- `.prisma-ui/routes.json`
- `.prisma-ui/panels/*.json`
- `.governance/current/AUTHORITY_READSET.lock.json`
- `docs/visual-layer-map/layer-map.json`
- `config/prisma-visual*`
- `tools/quality/ui-certainty.mjs`

## Outputs

Generated registry outputs live under `.prisma-ui/visual-control/`:

- `registry.json`
- `surfaces.json`
- `routes.json`
- `components.json`
- `editable-slots.json`
- `owners.json`
- `layers.json`
- `risks.json`
- `reuse-report.json`

Generated report outputs live under `.prisma-ui/current/`:

- `UI_VISUAL_CONTROL_REPORT.json`
- `UI_VISUAL_CONTROL_REPORT.md`
- `UI_EDITABLE_SLOTS_REPORT.json`
- `UI_EDITABLE_SLOTS_REPORT.md`
- `UI_VISUAL_CONTROL_LAYERS_REPORT.json`
- `UI_VISUAL_CONTROL_OWNERS_REPORT.json`
- `UI_VISUAL_CONTROL_REUSE_REPORT.json`
- `UI_VISUAL_CONTROL_CERT_REPORT.json`

Human-facing Visual Control summaries remain compact, but the governed machine layer now preserves full deterministic detail needed for exact-target compilation.

- Surface-scoped runs are isolated under `.prisma-ui/surface-runs/<surface>/` by default and **must not** overwrite the all-surface registry.
- A no-`--surface` run is the only canonical all-surface census source.
- Full machine detail is emitted as deterministic JSONL shards under `visual-control/expanded/<surface>/`.
- Canonical promoted shards live under `prisma-html/authority/rifat/prisma-ui/visual-control/expanded/`.
- Human reports may still use bounded samples; GVAE and Identity consume promoted machine detail instead of inferring from samples.
- External result ZIPs remain useful forensic evidence, but they are no longer the only place where exact machine coordinates can exist.

The distinction is deliberate: compact summaries are for people; expanded governed shards are for deterministic compilers and target resolution.

## Canonical all-surface promotion

The canonical chain is:

`fresh all-surface census -> fail-closed promotion -> RIFAT visual-control authority -> Identity bindings/adapters -> compiled Identity -> GVAE Visual Target Index`

Promotion is performed by `prisma-html/tools/promote_visual_control_all_surfaces.py`. It accepts only `CERTIFIED`, `ALL_SURFACES_CANONICAL` input containing all seven governed surfaces and complete expanded shards. A surface-scoped run is rejected for global promotion.

The PR workflow `.github/workflows/gvae-all-surface-authority.yml` proves scoped-run isolation, generates a fresh all-surface candidate, promotes it in an ephemeral checkout, recompiles Identity and GVAE, checks deterministic files and materializes changed canonical authority on the PR branch.

A physical census coordinate is not semantic application permission. GVAE publishes census coordinates as `VISUAL_CONTROL_CENSUS_TARGET / DISCOVERY_ONLY / BLOCKED` until exact semantic meaning, recipe, binding, layer application policy and target-specific authority are proven.

## Commands

Use the package scripts from `apps/terminal-de-venta-system`:

```bash
pnpm run ui:visual-control:inventory
pnpm run ui:visual-control:owners
pnpm run ui:visual-control:slots
pnpm run ui:visual-control:layers
pnpm run ui:visual-control:report
pnpm run ui:visual-control:certify
```

Equivalent direct commands:

```bash
node tools/quality/ui-certainty.mjs visual-control:inventory --strict
node tools/quality/ui-certainty.mjs visual-control:owners --strict
node tools/quality/ui-certainty.mjs visual-control:slots --strict
node tools/quality/ui-certainty.mjs visual-control:layers --strict
node tools/quality/ui-certainty.mjs visual-control:report --strict
node tools/quality/ui-certainty.mjs visual-control:certify --strict
```

## Safety Classes

- `safeVisualOnly`: visual-only slot controlled by a local owner.
- `visualWithFunctionalRisk`: visual slot that may affect layout, layering, hit targets, route readability, or background ownership.
- `functionalControl`: buttons/action zones where removal or movement can change behavior.
- `sharedGlobalRisk`: shared UI, tokens, recipes, themes, or global styling that can affect multiple surfaces.
- `generatedEvidenceOnly`: generated reports, runtime snapshots, and evidence files.
- `docsOnly`: documentation-only evidence.
- `fixtureOnly`: fixtures and samples.
- `inactiveArchive`: archived or backup material excluded from active ownership.

## Certification

`ui:visual-control:certify` passes only when:

- target surfaces are registered;
- active routes have owners;
- active visual regions have an owner or explicit non-blocking risk;
- editable slots are classified;
- active runtime files contain no `!important`;
- active CSS layer owners are not ambiguous;
- docs, fixtures, generated evidence, and archives are not treated as active runtime owners;
- reports are generated under `.prisma-ui/current/`.

## Future Usage Examples

For "make the Tablet POS payment panel taller", inspect `futureUsageExamples.tabletPaymentPanelTaller` in `UI_VISUAL_CONTROL_REPORT.json`. It identifies the surface, route, visual unit, owner component, owner CSS, safe slots, risk class, gates, and excluded surfaces.

For "change the background on PC dashboard", inspect `futureUsageExamples.pcDashboardBackground`. It identifies the PC route, background or atmospheric owner CSS, asset owners, layer level, risk class, and gates.

For "remove this button on Mobile", inspect `futureUsageExamples.mobileRemoveButton`. It classifies the control as functional when source signals show event handlers, forms, navigation, permissions, or guarded state. Removal is unsafe unless a follow-up task explicitly reviews behavior.

## Non-goals

- No visual redesign.
- No CSS hotfixes.
- No broad shared UI edits.
- No route, Prisma, DB, sync, auth, or POS behavior changes.
- No port rewrites, process kills, port freeing, or Prisma generate.
  Existing dev servers may be reused, and missing dev servers may be started
  when runtime evidence, route probing, or certification requires them.

## Reuse Rule

This system extends UI Certainty and the existing PRISMA governance mesh. It does not replace `.prisma-ui`, `ui-certainty`, Authority Mesh, runtime/page certification, Visual OS, Surface Visual Governor, token registries, or layer-map evidence.
