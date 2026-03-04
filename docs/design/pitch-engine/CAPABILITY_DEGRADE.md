# Capability Degrade Design

## Objective

Make capability degrade explicit, testable, and auditable.

## Requested Capability Set

- `allowExperimentalWorkers`
- `allowCrossModuleImports`
- `allowTemporalSignals`
- `allowNonDeterministicApis`

## Applied Policy

- development/test: requested values can apply.
- production: hard gate maps all capability toggles to `false`.

## Visibility Requirements

Verification artifacts must expose both:

- requested capability state
- applied capability state

Current evidence path:

- unit matrix tests in `capability_priority_degrade_matrix.test.ts`
- verification report summary in `artifacts/keystone-pitch-engine/verification_last.json`

## Motion Budget Interaction

Layer/capability interaction includes motion controls:

- `neutral` profile may permit requested motion.
- `fx` and `perf` profiles degrade motion to off for budget safety.

Validated by motion budget matrix scenarios.

## Failure Semantics

Any divergence from policy expectations:

- fails unit test case
- fails verification pass
- blocks acceptance checklist
