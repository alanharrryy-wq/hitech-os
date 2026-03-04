# Pitch Engine Core Quality

## Scope

This document defines quality guarantees for `apps/keystone/lib/pitch-engine/**`.

The Pitch Engine core is a deterministic domain layer over Scene concepts:

- Scene Engine: route + query + viewport + profile + layers + motion.
- Pitch Program: ordered steps pointing to scene references.
- Director Sequence: timeline DSL with keyframes, markers, and deterministic rules.
- Capability Resolver: auditable requested vs applied mode (`off|lite|full|debug`).

## Contracted Guarantees

1. Contracts are versioned (`schemaVersion=1`) with explicit migration stubs.
2. Runtime validators return legible error messages with stable field paths.
3. Canonical serializers sort deterministic fields and produce stable JSON output.
4. Stable hashes are generated from canonical payloads.
5. Program/sequence roundtrips preserve semantics.
6. Capability priority is strict: `env > query > localStorage > defaults`.
7. Production hard gate forces applied capability mode to `off`.
8. Degrade rules are deterministic and auditable.
9. Reduced-motion strategy is `jumpToFinal`.
10. Perf-profile `low` degrades full/debug to lite.
11. Motion budgets are enforced via hero-motion and per-track keyframe caps.

## Reduced Motion Behavior

When reduced-motion is enabled:

- Requested `full` or `debug` is degraded to applied `lite`.
- Timeline keyframes collapse to the latest keyframe per `track:key`.
- Collapsed keyframes are assigned `tMs=0` for deterministic immediate final-state rendering.
- Marker timestamps are normalized to `0` to avoid motion-driven timeline waiting.

This provides deterministic and accessible rendering behavior while preserving semantic final states.

## Perf Profile Behavior

When performance profile is `low`:

- Requested `full` or `debug` degrades to applied `lite`.
- Motion track keyframes are removed.
- Layer intensity values are reduced by a deterministic factor of `0.5`.
- Reason codes are captured for audit (`perf-low`, `lite-drop-motion-track`, `lite-reduce-layer-intensity`).

## Motion Budget Policy

Sequence motion budget fields:

- `maxHeroMotions`
- `maxTrackKeyframes`

Enforcement rules:

- Hero motions count only keyframes where track is `motion` and key is one of `heroEntrance|parallax`.
- Per-track keyframe count must not exceed `maxTrackKeyframes`.
- Violations are emitted as structured audit records.

## Determinism Requirements

Determinism is required across:

- schema validation paths and first error message,
- serialized key ordering,
- tag/layer/marker canonical sorting,
- hash generation from canonical forms,
- capture-plan derivation timestamps.

No free-form JS execution is allowed in Sequence DSL values.

## Testing Coverage

Core tests live at:

- `apps/keystone/tests/pitch-engine-core/program-schema.test.ts`
- `apps/keystone/tests/pitch-engine-core/sequence-schema.test.ts`
- `apps/keystone/tests/pitch-engine-core/capabilities.test.ts`
- `apps/keystone/tests/pitch-engine-core/transport-reducer.test.ts`
- `apps/keystone/tests/pitch-engine-core/degrade.test.ts`
- `apps/keystone/tests/pitch-engine-core/motion-budget.test.ts`
- `apps/keystone/tests/pitch-engine-core/hash-roundtrip.test.ts`

The suite is designed to enforce contract-level invariants and deterministic behavior under mutation scenarios.
