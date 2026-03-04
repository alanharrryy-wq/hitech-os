# PITCH ENGINE GOVERNANCE

## Governance Objective

Prevent unproven UI-affecting changes from shipping.

Policy name: `no proof, no ship`.

## Enforcement Script

- `tools/hos/quality/governance/pitch_engine_gate.mjs`

## Triggered Scope

UI-affecting paths:

- `apps/keystone/app/pitch/**`
- `apps/keystone/components/pitch/**`
- `apps/keystone/app/dev/pitch-engine/**`
- `apps/keystone/app/dev/scene-studio/**`

## Required Proof When Triggered

1. Claim file exists:
- `docs/quality/IMPROVEMENT_CLAIMS/<RUN_ID>.md`

2. Artifact reference exists in one of:
- `artifacts/keystone-pitch-engine/index.json`
- `artifacts/keystone-pitch-engine/verification_last.json`
- `docs/quality/PITCH_ENGINE_ACCEPTANCE.md`

## PASS/FAIL Semantics

PASS:

- no UI-affecting files changed, OR
- UI-affecting files changed and both claim + proof conditions are met.

FAIL:

- UI-affecting files changed and either claim/proof condition is missing.

## Local and CI Usage

Local:

```bash
node tools/hos/quality/governance/pitch_engine_gate.mjs --run-id 20260304_061005_61C9
```

CI (strict run-id required):

```bash
node tools/hos/quality/governance/pitch_engine_gate.mjs --fail-if-no-run-id --run-id $RUN_ID
```

## Output Contract

The script prints:

- concise PASS/FAIL line
- deterministic JSON payload with changed paths and policy decision

Exit code:

- `0` PASS
- `1` FAIL

## Governance Attestation for This Run

Claim file:

- `docs/quality/IMPROVEMENT_CLAIMS/20260304_061005_61C9.md`

Expected verification artifact:

- `artifacts/keystone-pitch-engine/verification_last.json`

Run bundle index outputs:

- `tools/codex/runs/20260304_061005_61C9/D_validation/LOGS/INDEX.json`
- `tools/codex/runs/20260304_061005_61C9/D_validation/FILES_CHANGED.json`
