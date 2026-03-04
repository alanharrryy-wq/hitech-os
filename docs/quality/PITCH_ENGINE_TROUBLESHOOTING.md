# PITCH ENGINE TROUBLESHOOTING

## Triage Flow

1. Run doctor:

```bash
node tools/hos/quality/verification-pass/doctor.mjs
```

2. Run unit matrix only:

```bash
pnpm --filter @hitech/keystone test -- tests/pitch-engine-validation
```

3. Run governance gate:

```bash
node tools/hos/quality/governance/pitch_engine_gate.mjs --run-id 20260304_061005_61C9
```

4. Run smoke harness:

```bash
node apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs --start-server
```

5. Run full verification pass:

```bash
node tools/hos/quality/verification-pass/run_verification_pass.mjs --run-id 20260304_061005_61C9
```

## Failure Modes and Fixes

### 1. Governance gate FAIL due missing claim

Symptom:

- `FAIL pitch_engine_gate` and missing claim file note.

Fix:

- create/update `docs/quality/IMPROVEMENT_CLAIMS/<RUN_ID>.md`
- include `artifacts/keystone-pitch-engine/*` proof reference.

### 2. Governance gate FAIL due missing artifact proof

Symptom:

- gate identifies UI touches but cannot find artifact index/report reference.

Fix:

- run verification pass to generate `verification_last.json`
- ensure claim or acceptance doc references artifact path.

### 3. Unit tests fail in matrix suites

Symptom:

- failure in one of:
  - `layer_contract_matrix.test.ts`
  - `schema_roundtrip_hashing_matrix.test.ts`
  - `capability_priority_degrade_matrix.test.ts`
  - `integration_access_gate_validation.test.ts`

Fix:

- inspect failing scenario id in test output
- map scenario to fixture row in `apps/keystone/tests/pitch-engine-validation/fixtures`
- update source contract (if intentional) or fixture expectation (if stale) with deterministic rationale.

### 4. Smoke harness fails because server not reachable

Symptom:

- `Server did not become ready` message.

Fix:

- confirm port `3100` is free
- run `pnpm --filter @hitech/keystone dev`
- rerun smoke without `--start-server` if server already running:

```bash
node apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs --base-url http://127.0.0.1:3100
```

### 5. Playwright unavailable

Symptom:

- smoke output reports `playwright_unavailable` fallback.

Fix:

- install playwright in environment, or accept fallback deterministic fetch mode for local CI-light runs.

### 6. Production hard-gate assertions fail

Symptom:

- capability matrix expects forced-off but receives true.

Fix:

- validate production env hard gate model in test harness
- ensure no dev capability override bypasses production path.

### 7. Access-gate checks fail

Symptom:

- integration test finds unexpected dev route files present.

Fix:

- confirm route path ownership and intended policy
- if route intentionally added, add governance claim and proof.

## Accept / Reject / Rerun Protocol

Accept when:

- verification pass exits `0`
- governance gate PASS
- acceptance checklist is all PASS
- report exists at `artifacts/keystone-pitch-engine/verification_last.json`

Reject when:

- any step returns non-zero
- governance gate FAIL on proof requirement
- checklist item lacks evidence link

Rerun sequence:

```bash
node tools/hos/quality/verification-pass/doctor.mjs
pnpm --filter @hitech/keystone test -- tests/pitch-engine-validation
node apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs --start-server
node tools/hos/quality/governance/pitch_engine_gate.mjs --run-id 20260304_061005_61C9
node tools/hos/quality/verification-pass/run_verification_pass.mjs --run-id 20260304_061005_61C9
```

## Artifact Inspection

Primary run artifacts:

- `artifacts/keystone-pitch-engine/verification_last.json`
- `tools/codex/runs/20260304_061005_61C9/D_validation/STATUS.json`
- `tools/codex/runs/20260304_061005_61C9/D_validation/SUMMARY.md`
- `tools/codex/runs/20260304_061005_61C9/D_validation/DOD_RESULTS.json`

If a rerun changes outcomes, update:

- `SELF_CORRECTION_LOG.jsonl`
- `SANCTION_SCORE.json`
- `SELF_EVAL_REPORT.json`
