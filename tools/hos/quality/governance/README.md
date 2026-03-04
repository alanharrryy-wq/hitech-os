# Pitch Engine Governance Gate

`pitch_engine_gate.mjs` enforces the local/CI guardrail for UI-affecting pitch changes.

## Rule

`no proof, no ship`

If the git working tree touches UI-affecting paths:

- `apps/keystone/app/pitch/**`
- `apps/keystone/components/pitch/**`
- `apps/keystone/app/dev/pitch-engine/**`
- `apps/keystone/app/dev/scene-studio/**`

Then the gate requires both:

1. Claim file: `docs/quality/IMPROVEMENT_CLAIMS/<RUN_ID>.md`
2. Artifact proof path present or referenced (`artifacts/keystone-pitch-engine/*` or acceptance doc reference)

## Run

```bash
node tools/hos/quality/governance/pitch_engine_gate.mjs --run-id 20260304_061005_61C9
```

Strict mode (missing run id fails):

```bash
node tools/hos/quality/governance/pitch_engine_gate.mjs --fail-if-no-run-id --run-id 20260304_061005_61C9
```

## Output

- `PASS` or `FAIL` summary line
- JSON report with changed paths, UI touch detection, claim/proof details
- exit code `0` on PASS, `1` on FAIL

This gate is lightweight and does not run the full test suite.
