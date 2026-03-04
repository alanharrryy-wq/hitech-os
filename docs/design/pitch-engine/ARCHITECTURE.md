# Pitch Engine Design Notes

## Goal

Define deterministic validation, governance, and verification-pass architecture for Keystone pitch-engine quality gates.

## Design Constraints

- Determinism first.
- No silent passes.
- Local-first execution.
- No mutation of core pitch-engine libraries in this worker scope.

## Validation Topology

### Unit Matrix Layer

Path: `apps/keystone/tests/pitch-engine-validation`

Suites:

1. `layer_contract_matrix.test.ts`
- validates layer IDs, data-layer attribute contract, parser tolerance, precedence matrix.

2. `schema_roundtrip_hashing_matrix.test.ts`
- validates schema mutation handling, roundtrip serializer behavior, deterministic hashing.

3. `capability_priority_degrade_matrix.test.ts`
- validates `A_core` registry ordering, capability hard gate, requested-vs-applied degrade visibility, motion budget.

4. `integration_access_gate_validation.test.ts`
- validates route/API access gates and production debug-tooling suppression.

### Visual Smoke Layer

Path: `apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs`

Behavior:

- optional server bootstrap
- playwright checks when available
- deterministic fetch fallback when unavailable
- API smoke request

### Governance Layer

Path: `tools/hos/quality/governance/pitch_engine_gate.mjs`

Behavior:

- diff inspection from git status
- UI touch detection
- claim + proof enforcement

### Verification Orchestrator Layer

Path: `tools/hos/quality/verification-pass/run_verification_pass.mjs`

Behavior:

- composes unit + smoke + governance + self DoD
- writes deterministic report JSON

## Requested vs Applied Capability Model

Model contract:

- requested capabilities are recorded at input.
- applied capabilities may be degraded by environment policy.
- in production, hard gate forces all dev tooling capabilities off.

This is encoded as matrix tests and acceptance evidence.

## Deterministic Data Contracts

- Scenario fixtures are generated and sorted deterministically.
- Hashing uses canonical JSON serialization and stable order.
- Route matrix and layer IDs are asserted by canonical ordering.

## Acceptance Decision Model

- PASS only when all verification steps pass and artifacts are written.
- FAIL on any non-zero step or governance proof failure.

## Extension Points

1. Add timestamped keyframe capture to smoke harness when target routes expose timeline/player controls.
2. Add bridge origin and payload policy tests when bridge route is introduced.
3. Add support-bundle artifact index schema check when bundle exporter lands.
