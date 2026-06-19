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

High-volume ownership output is compacted in Git. The repo keeps counts,
profiles, samples, and lookup indexes needed to plan future visual edits.
Fully expanded slot/layer detail belongs in the external result evidence zip
when a certification run needs that forensic payload.

The compact repo indexes intentionally cap expanded slot, owner, layer and
asset detail. If a future certification needs full forensic payloads, generate
that payload into the task evidence folder under `F:\descargasf\...result.zip`
instead of committing multi-megabyte JSON dumps.

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
