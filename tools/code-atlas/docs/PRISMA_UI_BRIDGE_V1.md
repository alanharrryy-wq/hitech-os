# PRISMA UI Bridge V1

Status: SOURCE_ONLY. Application is intentionally disabled.

Canonical flow:

```text
componentUiId / componentId
→ UIMAP batches and Code Atlas
→ exact source target
→ NDC neutral meaning
→ binding and layer
→ compatible recipe
→ canonical surface adapter
→ deterministic plan and semantic diff
→ future exact-target Authority Mesh
→ authorized application outside V1
```

The Bridge does not discover product UI and does not replace UIMAP, NDC, Code Atlas App Map, Surface Target Atlas, IDRECIPE1, UI Certainty Supreme, or Authority Mesh. It consumes their outputs and refuses to invent missing owners, targets, meanings, bindings, layers, hashes, states, or recipes.

UIMAP owns the component and immutable batch schemas. The Bridge imports
`code_atlas.app_map.uimap.contracts` and keeps only its plan schema locally, so
the consumer cannot drift into a second component or batch contract.

## Commands

```powershell
$env:PYTHONPATH='F:\repos\hitech-os\tools\code-atlas\src'
$env:PRISMA_PRODUCT_ROOT='F:\repos\hitech-os'
$env:PRISMA_GOVERNOR_ROOT='F:\repos\hitech-os-prisma-html\prisma-html'
$env:CODE_ATLAS_OUTPUT_ROOT='F:\descargasf'
python -m code_atlas.ui_bridge selftest
python -m code_atlas.ui_bridge validate F:\descargasf\uimap_batches
python -m code_atlas.ui_bridge resolve F:\descargasf\uimap_batches --component TB-POS-PAY-COBRAR-BTN-01 --profile profiles\prisma-ui-bridge.v1.json
python -m code_atlas.ui_bridge plan F:\descargasf\uimap_batches --component TB-POS-PAY-COBRAR-BTN-01 --profile profiles\prisma-ui-bridge.v1.json
python -m code_atlas.ui_bridge apply-status
```

The same commands are available from the canonical Code Atlas CLI through
`python -m code_atlas.cli.main ui-bridge ...`. When a batches directory is
provided, the Bridge ingests only the current numbered batches; immutable
`batches/history` entries remain preserved but are not mixed into the active
contract set.

`apply` always returns `APPLICATION_DISABLED_SOURCE_ONLY_V1` in this version.
