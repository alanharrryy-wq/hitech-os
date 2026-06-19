# UI VISUAL CONTROL REUSE REPORT

- status: `CERTIFIED`

## Reused Systems

- reused - .prisma-ui/registry.json: target apps, gates, global UI scope, hard states
- reused - .prisma-ui/surfaces.json: surface roots, ports, owners, scope, runtime probe hints
- reused - .prisma-ui/routes.json: 108 route contracts and runtime/source route ownership
- reused - .prisma-ui/panels/*.json: panel owner contracts and safe panel scopes
- extended - tools/quality/ui-certainty.mjs: delegating CLI and existing certification surface
- reused - .governance/current/AUTHORITY_READSET.lock.json: fresh authority mesh readset for this task
- reused - docs/visual-layer-map/layer-map.json: baseline layer-map evidence, not live owner truth by itself
- reused - config/prisma-visual* and config/prisma-visual-os: token, recipe, layer-budget and visual recipe ownership

## Extended Systems

- tools/quality/ui-certainty.mjs
- package.json
- .prisma-ui/registry.json

## Left Untouched

- Active product UI visuals and CSS aesthetics
- Prisma schema, migrations, auth, sync and business logic
- Runtime servers and process state

## Authoritative Paths

- .prisma-ui/visual-control/registry.json
- .prisma-ui/current/UI_VISUAL_CONTROL_REPORT.json
- .prisma-ui/current/UI_EDITABLE_SLOTS_REPORT.json
