# PRISMA Authority Mesh Report

- Status: `PASS_COMPOSED_AUTHORITY_MESH`
- Task: `PRISMA Mobile interface specification canon consolidation`
- Repo head locked: `72637e9702ad0d9bbfa9dc523ef09a56c910ecd1`
- Surface: `mobile`
- Mutation class: `documentation_governance_only`
- Visual implementation mutation: `false`
- Required authority coverage: `100%`
- Blockers: `0`
- Request digest: `da186efdb0b1599d5eeafb4a30cbf3d600abda511b61f05e7dd41366acae9fa6`
- Artifact digest: `bc4a7839d68bb5ebe77e9a7c805947017fe1fdc69f51c6dbc1b159468b20f0a9`
- Layer Map: `present`

## Factory Ledger classification

Canonical capability: `mobile.secure_projection_gateway_phase1`

- Ledger classification: `VERIFY`
- Status: `LOCAL_VERIFIED`
- Requested action: `ADVANCE`
- This task advances the Mobile read-model/product-interface authority only.
- It does not enable Mobile mutations and does not claim runtime signed-session E2E.

## Authority decision

The task is authorized to:

1. establish one aspirational Mobile product-interface canon;
2. delete superseded competing Mobile interface specification files with an explicit migration note;
3. reduce legacy spec files required by active technical verifiers to non-authoritative compatibility pointers;
4. align commercial wording so it no longer creates a competing interface hierarchy;
5. write task-exact governance evidence.

The task is not authorized to modify application source, runtime, APIs, data contracts, sync, licensing/auth, PWA behavior, verifier code, Tablet, PC, Shared UI, Shared Core, Chart Lab, Control Center, DB/schema/migrations or deployment.

## Canon result

Primary product hierarchy:

`Inicio / Pulso -> Ventas -> Caja -> Inventario -> Mando -> Sistema`

Mando consolidates Command Center, Action Inbox, Daily Brief, Decision Ledger, Pulse Timeline, Health Radar and compact owner analytics. MultiSucursal becomes global context. Alerts become actionable signals. Reports become Daily Brief/contextual evidence. Sync, licensing, devices, setup/install and diagnostics belong to Sistema.

## Compatibility finding

`products/mobile/app/package.json` keeps legacy iteration verifiers in `check:all`. Several verifier scripts require old documentation paths to exist, so those paths are retained as compatibility pointers only. Their previous normative content is removed.

## Current-directory notice

For this task, the authoritative `.governance/current` artifacts are:

- `AUTHORITY_READSET.lock.json`
- `APP_IMPACT_MATRIX.md`
- `CONTRACT_AND_GATE_MATRIX.json`
- `MISSING_OR_UNMAPPED_RISK.md`
- `AGENT_PROMPT_ENVELOPE.md`
- `AUTHORITY_MESH_REPORT.md`
- `LAYERS_MAP.md`
- `LAYERS_MAP.json`
- `ANTI_REWORK_REQUEST.json`
- `ANTI_REWORK_DECISION.json`

Other generated files already present in `.governance/current` may belong to an older task and do not authorize additional mutation for this Mobile documentation task.
