# Verification Pass Design

## One-Button Runner

Entry:

```bash
node tools/hos/quality/verification-pass/run_verification_pass.mjs --run-id 20260304_061005_61C9
```

## Steps

1. Unit matrix (`pnpm --filter @hitech/keystone test -- tests/pitch-engine-validation`)
2. Visual smoke (`node apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs --start-server`)
3. Governance gate (`node tools/hos/quality/governance/pitch_engine_gate.mjs --run-id <RUN_ID>`)
4. Self DoD (`node tools/codex/runs/<RUN_ID>/D_validation/self_dod/run_self_dod.mjs` when available)

## Reporting

Output file:

- `artifacts/keystone-pitch-engine/verification_last.json`

Payload includes:

- step id
- command
- rc
- elapsed ms
- trimmed stdout/stderr
- global pass/fail

## Non-Flake Rules

- no hidden retries
- deterministic command order
- deterministic output structure

## Doctor Command

```bash
node tools/hos/quality/verification-pass/doctor.mjs
```

Checks basic runtime prerequisites and governance command operability.
