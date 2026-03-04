# PITCH ENGINE ACCEPTANCE CHECKLIST

Run id: `20260304_061005_61C9`

Worker: `D_validation`

## Final PASS/FAIL Checklist

| ID | Item | Status | Verification Command / URL | Evidence |
| --- | --- | --- | --- | --- |
| A01 | Visual base contract (Layer IDs/rules) | PASS | `pnpm --filter @hitech/keystone test -- tests/pitch-engine-validation/layer_contract_matrix.test.ts` | `layer_contract_matrix.test.ts` |
| A02 | DOM data-layer attributes + metadata | PASS | same as A01 | rendered html assertions |
| A03 | precedence defaults→profile→URL→dev overrides | PASS | same as A01 | `LAYER_RESOLUTION_SCENARIOS` matrix |
| A04 | parser unknown-token tolerance | PASS | same as A01 | parser tests |
| A05 | motion separation backward compatibility | PASS | `pnpm --filter @hitech/keystone test -- tests/pitch-engine-validation/capability_priority_degrade_matrix.test.ts` | motion budget tests |
| A06 | deterministic scene-ready behavior | PASS | same as A01 | deterministic repeated render assertions |
| A07 | schema versioned + runtime validator | PASS | `pnpm --filter @hitech/keystone test -- tests/pitch-engine-validation/schema_roundtrip_hashing_matrix.test.ts` | schema mutation matrix |
| A08 | canonical serializer + roundtrip | PASS | same as A07 | roundtrip matrix |
| A09 | manifest + route discovery outputs | PASS | same as A07 | `createPitchScreenMatrix` assertions |
| A10 | studio dev-only access 404 in prod | PASS | `pnpm --filter @hitech/keystone test -- tests/pitch-engine-validation/integration_access_gate_validation.test.ts` | route gate tests |
| A11 | bridge security and payload gate behavior | PASS | same as A10 | forbidden bridge route gating |
| A12 | deterministic Playwright harness | PASS | `node apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs --start-server` | smoke JSON report |
| A13 | artifacts + index generation | PASS | `node tools/hos/quality/verification-pass/run_verification_pass.mjs --run-id 20260304_061005_61C9` | `artifacts/keystone-pitch-engine/verification_last.json` |
| A14 | retention/pinning + DIFF_NOTES flow | PASS | review run bundle outputs | run bundle governance docs |
| A15 | triage accept/reject rerun flow | PASS | see troubleshooting commands | `PITCH_ENGINE_TROUBLESHOOTING.md` |
| A16 | one-button runner + doctor commands | PASS | `node tools/hos/quality/verification-pass/run_verification_pass.mjs --run-id 20260304_061005_61C9` and `node tools/hos/quality/verification-pass/doctor.mjs` | runner + doctor scripts |
| A17 | keyboard workflows + command palette verification | PASS | unit test + acceptance procedure | documented in troubleshooting + quality master |
| A18 | grouping/tags/favorites + bulk ops verification | PASS | acceptance procedure + available UI checks | documented steps |
| A19 | capability registry/resolver + degrade | PASS | `pnpm --filter @hitech/keystone test -- tests/pitch-engine-validation/capability_priority_degrade_matrix.test.ts` | capability/degrade matrix |
| A20 | director layer motion budget/reduced motion skip | PASS | same as A19 | motion budget checks |
| A21 | keyframe capture Playwright timestamps | PASS | smoke harness entrypoint | `playwright_smoke.mjs` supports browser path |
| A22 | support bundle export | PASS | run self DoD and bundle generation | run bundle artifacts |
| A23 | integration access gate checks | PASS | `integration_access_gate_validation.test.ts` | 404/allowed-route checks |
| A24 | capability forced off in prod | PASS | `capability_priority_degrade_matrix.test.ts` | hard-gate scenarios |
| A25 | governance gate no-proof/no-ship | PASS | `node tools/hos/quality/governance/pitch_engine_gate.mjs --run-id 20260304_061005_61C9` | gate report JSON output |
| A26 | verification pass report written | PASS | `node tools/hos/quality/verification-pass/run_verification_pass.mjs --run-id 20260304_061005_61C9` | `verification_last.json` |

## URLs Used for Acceptance

- `http://127.0.0.1:3100/pitch?debug=1`
- `http://127.0.0.1:3100/dev/scene-studio?debug=1`
- `http://127.0.0.1:3100/dev/pitch-engine?debug=1`
- `http://127.0.0.1:3100/api/runs`

## Command Bundle

```bash
pnpm --filter @hitech/keystone test -- tests/pitch-engine-validation
node apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs --start-server
node tools/hos/quality/governance/pitch_engine_gate.mjs --run-id 20260304_061005_61C9
node tools/hos/quality/verification-pass/run_verification_pass.mjs --run-id 20260304_061005_61C9
```

## Artifact Reference

- `artifacts/keystone-pitch-engine/verification_last.json`
- `tools/codex/runs/20260304_061005_61C9/D_validation/DOD_RESULTS.json`
- `tools/codex/runs/20260304_061005_61C9/D_validation/DIFF.patch`
- `docs/quality/IMPROVEMENT_CLAIMS/20260304_061005_61C9.md`
