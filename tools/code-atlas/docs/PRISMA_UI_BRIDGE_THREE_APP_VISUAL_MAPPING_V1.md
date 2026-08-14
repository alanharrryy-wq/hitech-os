# PRISMA UI Bridge · Three-App Visual Mapping Closure V1

Status: `SOURCE_ONLY / GENERIC_PRODUCT_APPLICATION_DISABLED`

## Purpose

This extension closes the missing orchestration between the existing PRISMA visual
authorities. It does **not** create a second visual governor.

Canonical flow:

```text
Atlasfin / VISREC2 canonical visual meaning
→ neutralMeaningId
→ current UIMAP exact full-chain records
→ existing surface adapter
→ existing UI Bridge exact-target resolver
→ exhaustive Tablet / PC / Mobile target set
→ per-target source-only semantic plan + diff
→ binding promotion candidates / explicit gaps
→ consistency gate
→ future exact-target Authority Mesh
→ separately authorized product application
```

The three core runtime aliases are:

- `tb` → `ADP.TB.TOUCH.V2`
- `pc` → `ADP.PC.ADMIN.V2`
- `mb` → `ADP.MB.TOUCH.V2`

Those adapter IDs come from the canonical UIMAP contract. Atlasfin's
`PRISMA_SURFACE_ADAPTER_REGISTRY_V2` must publish all three or the consistency
audit blocks.

## New commands

### Refresh the current three-app source map

```powershell
$env:PYTHONPATH='F:\repos\hitech-os\tools\code-atlas\src'
$env:PRISMA_PRODUCT_ROOT='F:\repos\hitech-os'
$env:PRISMA_GOVERNOR_ROOT='F:\repos\hitech-os-prisma-html\prisma-html'
$env:CODE_ATLAS_OUTPUT_ROOT='F:\descargasf\prisma-three-app-map'

python -m code_atlas.cli.main ui-bridge refresh-three-app-map `
  --profile F:\repos\hitech-os\tools\code-atlas\profiles\prisma-ui-bridge.v1.json `
  --pilot-contract F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\docs\visual-pilots\PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1.contract.json
```

This regenerates UIMAP read-only and writes:

- `PRISMA_THREE_APP_VISUAL_MAPPING_REFRESH.json`
- `PRISMA_THREE_APP_VISUAL_MAPPING_READINESS.json`
- `PRISMA_UI_BRIDGE_BINDING_PROMOTION.json`
- `PRISMA_UI_BRIDGE_BINDING_GAP_MATRIX.json`
- `PRISMA_UI_BRIDGE_VISUAL_AUTHORITY_CONSISTENCY.json`
- the normal UIMAP evidence tree under `uimap/`

A source gap is an explicit result, not a failure to report. The command never
fills missing owner, route, region, slot, component, binding or layer coordinates.

### Plan one visual meaning across all three apps

```powershell
python -m code_atlas.cli.main ui-bridge plan-multisurface `
  F:\descargasf\prisma-three-app-map\uimap\batches `
  --profile F:\repos\hitech-os\tools\code-atlas\profiles\prisma-ui-bridge.v1.json `
  --neutral-meaning-id ACT.sale.checkout `
  --output-root F:\descargasf\prisma-three-app-plan
```

The default target-set rule is exhaustive across `tb`, `pc` and `mb`. If any
requested surface has no exact UIMAP match for the neutral meaning, the plan is
`PLAN_BLOCKED`. The planner never substitutes a similar component or samples one
target from a one-to-many set.

### Inspect safe binding-promotion candidates

```powershell
python -m code_atlas.cli.main ui-bridge binding-promotion `
  F:\descargasf\prisma-three-app-map\uimap\batches `
  --profile F:\repos\hitech-os\tools\code-atlas\profiles\prisma-ui-bridge.v1.json `
  --pilot-contract F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\docs\visual-pilots\PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1.contract.json `
  --output-root F:\descargasf\prisma-binding-promotion
```

Pilot contracts are cross-check evidence only. They do not fill missing UIMAP
coordinates. A promotion candidate requires the complete exact source chain,
high confidence, confirmed NDC meaning, source hashes, exact visual targets and
`ELIGIBLE_FOR_AUTHORITY_PREFLIGHT`.

### Audit visual-authority consistency

```powershell
python -m code_atlas.cli.main ui-bridge audit-visual-authority `
  --profile F:\repos\hitech-os\tools\code-atlas\profiles\prisma-ui-bridge.v1.json `
  --output-root F:\descargasf\prisma-visual-consistency
```

The audit fails closed on contradictions such as a resolved Cobrar layer in the
current element-binding registry while a stale contract still says that layer is
missing. It also verifies that VISREC2 publishes the canonical UIMAP adapters and
prevents PC/Mobile from claiming binding-ready status while required map sources
are absent.

## Safety contract

All commands in this extension are source-only.

- generic product application stays disabled;
- runtime mutation stays disabled;
- no database or Prisma mutation;
- no process or port operations;
- no generated coordinate inference;
- no `!important` or priority override mechanism;
- a future visual application still requires a fresh exact-target Authority Mesh,
  before evidence, bounded patch, gates, after evidence and rollback.

The existing exact Cobrar transaction remains separate. This extension does not
broaden `apply-cobrar` into a generic writer.
