# Selection Store + InspectorTarget Wiring Pack v1

## Purpose

This package turns the already-defined Selection / Inspector contract into a concrete next-step bundle for **Live Scene Composer**.

It is intentionally bigger than a one-file patch.
It includes:

- canonical follow-up docs
- a real TypeScript selection contract surface
- a reference Selection Store implementation
- InspectorTarget derivation logic
- surface synchronization helpers
- fixtures and example usage
- lightweight tests
- installer and zip-runner scripts
- manifest and installation summaries

## Why this pack exists

The project already established that:

- the authoring model is `Scene -> Layout -> Slots -> Widgets`
- selection is transient but high-value state
- inspector target must be derived from selection
- draft / baseline / preview meanings must remain distinct
- write-capable mutations must not depend on implicit selection
- runtime writes must remain governed by `runtime-mutation-bridge`

This pack converts those truths into a concrete working seam that can be staged or installed into the repo without guessing from scratch.

## Package shape

### Canonical docs

- `11_SELECTION_STORE_CONTRACT.md`
- `12_INSPECTOR_TARGET_DERIVATION.md`
- `13_SELECTION_SURFACE_SYNC_MATRIX.md`
- `14_SELECTION_STALENESS_AND_RECOVERY.md`
- `15_SELECTION_MUTATION_INTENT_BOUNDARY.md`
- `16_SELECTION_IMPLEMENTATION_SEQUENCE.md`
- `17_SELECTION_TEST_PLAN.md`
- `18_SELECTION_PACKAGE_DECISIONS.md`

### Reference source

- `source/selection/contracts.ts`
- `source/selection/selection-store.ts`
- `source/selection/inspector-target.ts`
- `source/selection/selection-sync.ts`
- `source/selection/selection-fixtures.ts`
- `source/selection/index.ts`
- `source/selection/README.md`

### Tests

- `source/selection/__tests__/selection-store.spec.ts`
- `source/selection/__tests__/inspector-target.spec.ts`
- `source/selection/__tests__/selection-sync.spec.ts`

### Delivery assets

- `install_live_scene_composer_selection_store_inspector_target_wiring_v1.ps1`
- `run_live_scene_composer_selection_store_inspector_target_wiring_v1_from_zip.ps1`
- `05_PACKAGE_MANIFEST.json`

## Delivery posture

This is a **reference implementation pack**.
It is designed to be:

- installable into docs immediately
- installable into a staging directory safely
- installable into a detected composer source root when one can be inferred with confidence
- explicit about what is staged vs what is auto-wired

That means the package gives you useful forward motion even if the exact source root layout differs slightly across branches.

## Added in the expanded pack

- repo integration playbook
- field manual
- 40 scenario matrix
- selectors, hooks, mutation-intent helpers, surface adapters
- example demo script
- multiple high-entropy scene fixtures for testing and review
