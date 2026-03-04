# Verification Pass

`run_verification_pass.mjs` executes deterministic end-to-end validation for pitch-engine scope.

## Included steps

1. Keystone unit validation suite (`tests/pitch-engine-validation`)
2. Deterministic visual smoke (`apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs`)
3. Governance gate (`tools/hos/quality/governance/pitch_engine_gate.mjs`)
4. Self DoD runner invocation when available (`tools/codex/runs/<RUN_ID>/D_validation/self_dod/run_self_dod.mjs`), otherwise local equivalent fallback

## Run

```bash
node tools/hos/quality/verification-pass/run_verification_pass.mjs --run-id 20260304_061005_61C9
```

Optional skips for local iteration:

```bash
node tools/hos/quality/verification-pass/run_verification_pass.mjs --run-id 20260304_061005_61C9 --skip-smoke
```

## Report output

Writes JSON report to:

- `artifacts/keystone-pitch-engine/verification_last.json`

Prints PASS/FAIL and returns non-zero on failure.
