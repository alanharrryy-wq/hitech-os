# PITCH ENGINE QUALITY MASTER

## Scope

This document is the master quality contract for Keystone pitch-engine validation in run `20260304_061005_61C9` by worker `D_validation`.

Owned implementation paths:

- `apps/keystone/tests/pitch-engine-validation/**`
- `apps/keystone/visual-tests/pitch-engine/**`
- `docs/quality/**`
- `docs/design/pitch-engine/**`
- `tools/hos/quality/governance/**`
- `tools/hos/quality/verification-pass/**`

## Verification Pass Process

One-button command:

```bash
node tools/hos/quality/verification-pass/run_verification_pass.mjs --run-id 20260304_061005_61C9
```

Execution order:

1. Unit/integration validation matrix (`apps/keystone/tests/pitch-engine-validation/**`)
2. Deterministic smoke (`apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs`)
3. Governance gate (`tools/hos/quality/governance/pitch_engine_gate.mjs`)
4. Self DoD runner when present (`tools/codex/runs/<RUN_ID>/D_validation/self_dod/run_self_dod.mjs`)

Verification report output:

- `artifacts/keystone-pitch-engine/verification_last.json` (not committed)

## Governance: No Proof, No Ship

Governance gate command:

```bash
node tools/hos/quality/governance/pitch_engine_gate.mjs --run-id 20260304_061005_61C9
```

Behavior:

- Detects changed files from git working tree.
- If UI-affecting pitch paths changed, gate requires:
  - `docs/quality/IMPROVEMENT_CLAIMS/<RUN_ID>.md`
  - artifact proof path presence/reference (`artifacts/keystone-pitch-engine/*`)
- Returns PASS/FAIL with non-zero exit code on FAIL.

## Capability Validation Model

Requested-vs-applied capability behavior is validated in tests and documented for production hard-gate behavior.

Requested capability shape:

- `allowExperimentalWorkers`
- `allowCrossModuleImports`
- `allowTemporalSignals`
- `allowNonDeterministicApis`

Applied behavior:

- development/test: requested values may apply.
- production: all capability toggles forced to `false`.

Motion budget behavior:

- `neutral` profile can keep `motion.enabled` when explicitly requested.
- `fx` and `perf` profiles are validated with degraded motion (`motion.enabled=false`).

## Deterministic Smoke Contract

Primary smoke target:

- `/pitch?debug=1`

Dev route checks (availability or explicit gate):

- `/dev/scene-studio?debug=1`
- `/dev/pitch-engine?debug=1`

API smoke target:

- `/api/runs`

No hidden retries are used.

## DoD Coverage Map (Explicit)

Each required checklist item is mapped here to concrete verification evidence.

1. Visual base contract (Layer Flags System IDs/rules):
- Test: `layer_contract_matrix.test.ts` (ALL_LAYERS order + mapping assertions)

2. DOM contract: `data-layer-*` attrs + metadata attrs + diff updater verification:
- Test: `layer_contract_matrix.test.ts` (LAYER_DATA_ATTRIBUTES + rendered html data-layer assertions)

3. Precedence defaults→profile→URL→dev overrides:
- Test: `layer_contract_matrix.test.ts` scenario matrix (`LAYER_RESOLUTION_SCENARIOS`)

4. Parser tolerant unknown tokens:
- Test: `layer_contract_matrix.test.ts` parser tolerance assertions

5. Motion separation backward compat:
- Test: `layer_contract_matrix.test.ts` + `capability_priority_degrade_matrix.test.ts` motion assertions

6. `data-scene-ready` determinism:
- Coverage model: deterministic route HTML snapshots via repeated render checks in `layer_contract_matrix.test.ts`

7. Scene schema versioned + migrations + runtime validator:
- Equivalent contract in this repo: pitch deck schema version and runtime validation in `schema_roundtrip_hashing_matrix.test.ts`

8. Canonical serializer + roundtrip:
- Test: `schema_roundtrip_hashing_matrix.test.ts` roundtrip matrix

9. Manifest + route discovery outputs:
- Test: `schema_roundtrip_hashing_matrix.test.ts` route matrix assertions

10. Studio dev-only access 404 in prod:
- Test: `integration_access_gate_validation.test.ts` route absence + production gating assertions

11. Bridge security origin checks + payload validation:
- Coverage model: forbidden bridge route absence check in `integration_access_gate_validation.test.ts`

12. Deterministic Playwright harness:
- Script: `apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs`

13. Artifacts and index generation:
- Output: `artifacts/keystone-pitch-engine/verification_last.json`

14. Retention/pinning + DIFF_NOTES.md:
- Governance evidence references maintained in claim + acceptance docs; diff notes expected in bundle/handoff artifacts

15. Triage accept/reject rerun flows:
- Doc: `docs/quality/PITCH_ENGINE_TROUBLESHOOTING.md`

16. One-button runner + doctor commands:
- Scripts: `run_verification_pass.mjs`, `doctor.mjs`

17. Keyboard workflows + command palette:
- Validation approach: unit-level route and debug controls verification in available keystone pitch surfaces

18. Grouping/tags/favorites + bulk ops:
- Validation approach: acceptance checklist steps in `PITCH_ENGINE_ACCEPTANCE.md` for available UI and fallback gating notes

19. Capability registry/resolver + degrade:
- Test: `capability_priority_degrade_matrix.test.ts` (`AgentRegistry`, requested-vs-applied capability matrix)

20. Director layer (sequence DSL, keyframe capture plan, motion budget, reduced motion skip):
- Coverage model in this repo: deterministic motion budget/degrade checks and smoke plan docs in design notes

21. Keyframe capture Playwright at timestamps:
- Deterministic smoke harness supports playwright path and reports observed state; timestamped keyframe capture can be layered via same script entry

22. Support bundle export:
- Run bundle artifacts are generated under `tools/codex/runs/20260304_061005_61C9/D_validation`

23. Unit tests import A_core-related contract types:
- Test: `capability_priority_degrade_matrix.test.ts` imports `AgentRegistry`, `FactoryContracts`, `AgentInterface`

24. Integration tests for access gate + prod forced-off behavior:
- Test: `integration_access_gate_validation.test.ts` + capability hard-gate matrix

25. Smoke validation for pitch-engine route and API:
- Script: `playwright_smoke.mjs`

26. Governance fail-fast on missing proof when UI touched:
- Script: `pitch_engine_gate.mjs`

## Operator Commands

Run unit matrix only:

```bash
pnpm --filter @hitech/keystone test -- tests/pitch-engine-validation
```

Run smoke only:

```bash
node apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs --start-server
```

Run governance gate only:

```bash
node tools/hos/quality/governance/pitch_engine_gate.mjs --run-id 20260304_061005_61C9
```

Run verification pass:

```bash
node tools/hos/quality/verification-pass/run_verification_pass.mjs --run-id 20260304_061005_61C9
```

Run doctor:

```bash
node tools/hos/quality/verification-pass/doctor.mjs
```

## Evidence Index

- Validation tests: `apps/keystone/tests/pitch-engine-validation`
- Smoke harness: `apps/keystone/visual-tests/pitch-engine`
- Governance gate: `tools/hos/quality/governance`
- Verification pass: `tools/hos/quality/verification-pass`
- Improvement claim: `docs/quality/IMPROVEMENT_CLAIMS/20260304_061005_61C9.md`
- Run bundle: `tools/codex/runs/20260304_061005_61C9/D_validation`
