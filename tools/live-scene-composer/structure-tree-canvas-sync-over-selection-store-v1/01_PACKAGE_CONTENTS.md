
# Package Contents

## Main docs

22. Structure Tree + Canvas sync contract
23. Structure Tree projection contract
24. Canvas viewmodel and overlay contract
25. Surface coordination flow
26. Pointer and keyboard selection rules
27. Reconciliation and stale recovery rules
28. Mutation-intent entrypoints
29. Test plan
30. Package decisions
31. Event scenarios
32. Repo integration playbook
33. Field manual

## Main source areas

- `contracts.ts`: shared types, commands, projections, diagnostics records
- `structure-tree-projection.ts`: builds tree nodes from scene graph inputs
- `canvas-viewmodel.ts`: derives overlays, focus frames, ghost states, and hints
- `surface-coordinator.ts`: orchestrates surface events against the selection store seam
- `pointer-hit-selection.ts`: converts pointer hit payloads into typed target requests
- `keyboard-navigation.ts`: deterministic structure-tree navigation rules
- `mutation-intent-entrypoints.ts`: bridge-safe mutation-intent request builders
- `stale-reconciliation.ts`: revision and missing-entity reconciliation helpers
- `integration-adapters.ts`: low-coupling adapter factory helpers
- `react-hooks.ts`: ergonomic wrappers for React usage

## Artifact payloads

- `artifacts/fixtures/*.json`
- `artifacts/traces/*.jsonl`
- `artifacts/matrices/*.csv`
- `artifacts/reviews/*.md`
