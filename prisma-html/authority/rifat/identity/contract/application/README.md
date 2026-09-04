# GVAE V1 application contracts

Strict declarative contracts for exact-target source/static visual application.

`APPLY` is fail-closed and requires:
- a task-exact current Authority Mesh artifact with 100% required authority coverage, zero blockers, verified provenance, stable repo capture, and the requested lane's Layer Map;
- a current Factory Ledger `MUTATION` anti-rework PASS evaluated by the canonical verifier for reuse of `visual.generic_application_engine_v1`;
- a hash-pinned, read-only Code Atlas UI Bridge `PLAN_READY_FOR_REVIEW` plan and semantic diff whose selector/property scope matches the exact target.

`ROLLBACK` uses a minimal transaction-bound contract and never trusts a caller to redefine transaction ownership. Runtime/browser visual certification remains outside these contracts.


## Application receipts and mandatory enforcement

Every non-idempotent GVAE `APPLY` emits `prisma.visual.application.receipt.v1`. The receipt is part of the same protected transaction, so rollback removes/restores it with the governed source/projection state.

For any path already represented by the generated Visual Target Index, direct mutation without a valid receipt chain is blocked by the repository CI and VISCORE1 mandatory gate.

Receipt evidence is source/static only. It proves a governed GVAE application transition and does not prove browser rendering, runtime visual correctness, all-surface coverage or production readiness.

Whole-surface mutation is not a V1 wildcard capability. Surface-wide orchestration requires complete explicit Target Index coverage and exact target-level authorization for every included target.


## All-surface census records

The generated Visual Target Index now distinguishes exact application authority from physical census coverage.

- `EXACT_APPLICATION_TARGET / GVAE_ENFORCED` records participate in GVAE PREVIEW/APPLY/VERIFY and the mandatory receipt gate.
- `VISUAL_CONTROL_CENSUS_TARGET / DISCOVERY_ONLY` records prove a current physical CSS coordinate from the certified seven-surface Visual Control authority. They remain `BLOCKED` and cannot authorize APPLY.

A census record may carry surface, canonical source/projection, selector, layer coordinate, region and safety classification, but it deliberately leaves semantic meaning, recipe and exact binding unresolved until those authorities are proven.

Whole-surface orchestration is read-only at the planning layer. `visual_application.surface_batch` remains blocked while any discovery-only gap or blocked exact target exists. No wildcard request can weaken exact-target contracts.
