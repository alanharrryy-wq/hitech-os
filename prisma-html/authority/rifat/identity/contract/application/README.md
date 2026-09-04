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
