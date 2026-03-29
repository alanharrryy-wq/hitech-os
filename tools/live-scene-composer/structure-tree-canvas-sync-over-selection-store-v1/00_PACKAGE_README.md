
# Structure Tree + Canvas Sync over Selection Store Pack v1

## Purpose

This pack is the next useful layer after the Selection Store + InspectorTarget bundle.
It wires the two highest-friction authoring surfaces, **Structure Tree** and **Canvas**, onto one explicit surface-coordination seam.

This is not a tiny patch.
It includes:

- canonical follow-up docs
- a complete TypeScript reference seam for tree/canvas synchronization
- projection builders for structure and canvas overlays
- surface coordinator logic
- pointer and keyboard interaction rules
- mutation-intent entrypoints that remain bridge-safe
- large fixtures, traces, matrices, and scenario catalogs
- tests, install scripts, runner wrapper, and manifest

## Why this pack exists

The project already established these truths:

- the composer owns authoring, including selection, structure tree, and canvas
- selection is transient interaction state, not domain truth
- write-capable mutations must remain typed and pass through `runtime-mutation-bridge`
- the authoring model remains `Scene -> Layout -> Slots -> Widgets`
- boundaries and docs/code drift must stay enforceable

The previous bundle gave the project a Selection Store and InspectorTarget derivation seam.
This pack makes those seams useful across the two surfaces that most easily drift apart in real product code.

## What is inside

### Canonical follow-up docs

- `22_STRUCTURE_TREE_CANVAS_SYNC_CONTRACT.md`
- `23_STRUCTURE_TREE_PROJECTION_CONTRACT.md`
- `24_CANVAS_VIEWMODEL_AND_OVERLAY_CONTRACT.md`
- `25_SURFACE_COORDINATION_FLOW.md`
- `26_POINTER_AND_KEYBOARD_SELECTION_RULES.md`
- `27_STRUCTURE_CANVAS_RECONCILIATION_RULES.md`
- `28_MUTATION_INTENT_ENTRYPOINTS.md`
- `29_STRUCTURE_CANVAS_TEST_PLAN.md`
- `30_STRUCTURE_CANVAS_PACKAGE_DECISIONS.md`
- `31_STRUCTURE_CANVAS_EVENT_SCENARIOS.md`
- `32_STRUCTURE_CANVAS_REPO_INTEGRATION_PLAYBOOK.md`
- `33_STRUCTURE_CANVAS_FIELD_MANUAL.md`

### Reference source seam

- `source/composer-sync/contracts.ts`
- `source/composer-sync/structure-tree-projection.ts`
- `source/composer-sync/canvas-viewmodel.ts`
- `source/composer-sync/surface-coordinator.ts`
- `source/composer-sync/pointer-hit-selection.ts`
- `source/composer-sync/keyboard-navigation.ts`
- `source/composer-sync/mutation-intent-entrypoints.ts`
- `source/composer-sync/stale-reconciliation.ts`
- `source/composer-sync/react-hooks.ts`
- `source/composer-sync/scenario-fixtures.ts`
- `source/composer-sync/integration-adapters.ts`
- `source/composer-sync/index.ts`

### Tests and artifacts

- 8 focused test files
- 4 large scene graph fixtures
- 2 event-trace JSONL files
- 2 reconciliation matrices
- diagnostics-oriented README and example usage

## Delivery posture

This is a **stack-on-top reference implementation pack**.
It assumes the Selection Store bundle was already installed or at least staged, and the launcher evidence confirms that happened on the user's repo.

The installer stages everything under `tools/live-scene-composer/structure-tree-canvas-sync-over-selection-store-v1`.
It also copies the docs into `docs/live-scene-composer/` and, when explicitly allowed, mirrors the source seam into an inferred composer source root.

## Why the package is intentionally fat

A tree/canvas seam is where accidental coupling loves to breed.
A tiny pack here would be theater.
So this one includes enough contracts, source surface, fixtures, and review artifacts to make implementation and repo integration legible instead of hand-wavy.
