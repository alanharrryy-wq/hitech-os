
# composer-sync reference seam

This folder contains a reference seam for coordinating Structure Tree and Canvas behavior on top of the Selection Store layer.

## Main modules

- `contracts.ts`
- `structure-tree-projection.ts`
- `canvas-viewmodel.ts`
- `surface-coordinator.ts`
- `pointer-hit-selection.ts`
- `keyboard-navigation.ts`
- `mutation-intent-entrypoints.ts`
- `stale-reconciliation.ts`
- `integration-adapters.ts`
- `react-hooks.ts`
- `scenario-fixtures.ts`

## Intended posture

Use this seam through adapters.
Do not let random product components each reinvent selection synchronization.
