# Mutation Client + Bridge Preview/Commit Pack v2 fixed

## Purpose

This pack is the next useful layer after the Selection Store + InspectorTarget bundle and the Structure Tree + Canvas sync bundle.
It makes the write path explicit inside Live Scene Composer without violating the runtime-mutation-bridge boundary.

This is not a tiny patch.
It includes:

- canonical follow-up docs for mutation-client, preview, commit, revert, discard, diagnostics, and policy
- a complete TypeScript reference seam for building typed mutation intents and routing them through bridge-facing adapters
- preview session tracking, diffing, commit orchestration, revert planning, and diagnostics helpers
- large fixtures, traces, matrices, walkthrough artifacts, and snapshots
- tests, install scripts, runner wrapper, and manifest

## Why this pack exists

The project already established these truths:

- the composer owns authoring surfaces, but not uncontrolled runtime writes
- all write-capable runtime-facing changes must pass through `runtime-mutation-bridge`
- preview, draft, commit, revert, and discard must remain semantically distinct
- safe mode is the default authority posture
- architecture guardrails must keep boundary drift visible

The previous packs made selection and surface coordination explicit.
This pack makes those surfaces actually useful for typed write flow without collapsing into UI-driven side effects.

## What is inside

### Canonical follow-up docs

- `50_MUTATION_CLIENT_BRIDGE_CONTRACT.md`
- `51_PREVIEW_SESSION_MODEL.md`
- `52_COMMIT_REVERT_DISCARD_FLOW.md`
- `53_MUTATION_POLICY_MODE_MATRIX.md`
- `54_BRIDGE_ADAPTER_ROUTING_RULES.md`
- `55_PREVIEW_DIFF_AND_BASELINE_COMPARE.md`
- `56_MUTATION_REJECTION_AND_DIAGNOSTICS.md`
- `57_MUTATION_CLIENT_TEST_PLAN.md`
- `58_MUTATION_CLIENT_PACKAGE_DECISIONS.md`
- `59_MUTATION_CLIENT_EVENT_SCENARIOS.md`
- `60_MUTATION_CLIENT_REPO_INTEGRATION_PLAYBOOK.md`
- `61_MUTATION_CLIENT_FIELD_MANUAL.md`
- `62_MUTATION_CLIENT_MIGRATION_STEPS.md`
- `63_MUTATION_CLIENT_FAILURE_ATLAS.md`

### Reference source seam

- `source/mutation-client/contracts.ts`
- `source/mutation-client/mutation-intents.ts`
- `source/mutation-client/mode-policy.ts`
- `source/mutation-client/validation.ts`
- `source/mutation-client/preview-session.ts`
- `source/mutation-client/preview-diff.ts`
- `source/mutation-client/commit-orchestrator.ts`
- `source/mutation-client/revert-planner.ts`
- `source/mutation-client/bridge-adapter.ts`
- `source/mutation-client/bridge-client.ts`
- `source/mutation-client/diagnostics.ts`
- `source/mutation-client/history-log.ts`
- `source/mutation-client/react-hooks.ts`
- `source/mutation-client/scenario-fixtures.ts`
- `source/mutation-client/index.ts`

### Tests and artifacts

- 11 focused test files
- 4 large mutation session fixtures
- 3 preview/commit traces
- 3 policy matrices
- 2 diagnostics walkthroughs
- 3 snapshot catalogs
- telemetry and playback artifacts
- example usage and integration notes

## Delivery posture

This is a stack-on-top reference implementation pack.
It assumes the earlier selection and surface-sync bundles are already staged or at least available in the repo as reference seams.

The installer stages everything under `tools/live-scene-composer/mutation-client-bridge-preview-commit-pack-v2 fixed`.
It also copies the docs into `docs/live-scene-composer/` and, when explicitly allowed, mirrors the source seam into an inferred composer source root.

## Why the package is intentionally fat

A mutation-client seam is where accidental shortcuts become architectural debt fast.
A tiny pack here would be pure teatro.
So this one includes enough contracts, source, fixtures, diagnostics, and review artifacts to make the bridge path legible, testable, and hard to hand-wave away.


## Fix note
This v2 fixed package corrects the PowerShell installer syntax issue from the previous package generation by removing invalid trailing commas in array literals and shipping a corrected installer/runner pair.
