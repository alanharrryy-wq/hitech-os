# GVAE V1 post-merge audit — corrective reclassification evidence

Status: `FIX_REQUIRED`
Canonical base audited: `1f73a677ffb076e4787099177f71470785f1f611`
Source PR: #521
Fresh task-exact Authority Mesh: run `33836037189`, artifact `9923318865`, digest `sha256:62eaaaeaf737d202fd6c7c71c05387f9175d614ba25f01abd639cb4c6315463e`
Authority request digest: `9569a92d7c4d58a18d2732b16a79d4db0daa73595353094b3141ece2d2cac382`
Authority result: `PASS_COMPOSED_AUTHORITY_MESH`, 100% required authority coverage in both lanes, zero missing authority, Layer Map present.
Evidence classification: source/static audit only. This document does not certify browser rendering, runtime visuals, production or deployment.

## Decision

PR #521 correctly established a fail-closed SOURCE_STATIC_ONLY boundary and passed its declared 54-test suite, but a deeper adversarial post-merge review found implementation defects not covered by that suite. The canonical capability must therefore move from `DONE / SOURCE_READY` to `FIX / VERIFY_REQUIRED` before source correction. This is a bounded correction of the existing GVAE V1 capability, not a rebuild.

## Proven defects / hardening failures

1. **Exact-target scope escape in CSS requests.** Preflight validates target authority IDs but does not bind each CSS operation path to the target's certified selector. A request authorized for one selector can patch another selector in the same canonical source file.
2. **JSON operation scope is not bound to the governed target.** The engine ignores the operation `path` for JSON and accepts arbitrary JSON Pointer keys from `values`, allowing mutation outside the intended exact target unless additional authority exists.
3. **Rollback is not two-phase atomic.** Rollback validates and restores rows in one pass. A later tampered backup or newer-work conflict can be discovered after earlier files have already been restored, leaving a partial rollback.
4. **Rollback can overwrite/delete newer work when recorded `afterSha256` is null.** The current guard skips mismatch validation in that state.
5. **Transaction metadata is not integrity/containment validated.** Caller-controlled transaction IDs and transaction JSON paths are not constrained strongly enough against traversal/tampering before rollback.
6. **Idempotent APPLY can leave projection drift unrepaired.** If canonical source bytes already equal desired bytes, APPLY returns immediately without proving generated projection parity or visual-source-manifest hash correctness.
7. **Target-index authority checks are incomplete.** Manifest matching can resolve by suffix without requiring manifest surface equality; adapter existence is checked globally rather than compatibility with target surface; certified layer existence/source/selector compatibility is not proven before APPLY_READY.
8. **JSON Pointer array indexing accepts Python negative/non-canonical indices.** Values such as `-1` can mutate an array element despite not being an authorized canonical array index.
9. **CSS declaration parsing is not fully lexical.** The declaration regex can misinterpret semicolons or declaration-looking text inside strings/comments, risking corruption or false ambiguity.
10. **Exact-byte-copy projection write is not atomic and symlink/containment protections are insufficiently explicit.**
11. **Python request validation is weaker than the published JSON Schema.** Several field formats/types/uniqueness constraints are not enforced consistently by the runtime loader.
12. **CLI error semantics are not fully fail-closed.** Invalid JSON, missing files and some unsupported-mode paths can escape the structured GVAE error result; ROLLBACK bypasses the normal request contract path.
13. **Rollback evidence can be misattributed.** Target identity is supplied again by the rollback caller rather than being bound into the transaction record.
14. **The exact 54-test CI count omits these adversarial cases.** Existing green therefore proves the declared suite, not these uncovered negative paths.

## Required corrective gate

Before touching GVAE source:
- keep `doNotRebuild=true`;
- classify the capability as `FIX / VERIFY_REQUIRED`;
- obtain current-head task-exact Authority Mesh + Layer Map;
- obtain a fresh Factory Ledger MUTATION decision for requestedAction `FIX`;
- patch only the existing GVAE V1 authority/tooling scope;
- add native negative/adversarial tests for every corrected defect;
- require deterministic CI and no fake green;
- return to `DONE / SOURCE_READY` only after exact-head evidence proves the corrected source/static engine.

## Boundaries preserved

Code Atlas UI Bridge remains read-only. Cobrar historical evidence remains frozen. No arbitrary Tablet/PC/Mobile/Web/Chart Lab/Control Center/Shared UI product-source mutation is authorized. No DB, Prisma, API, business logic, routing, licensing, sync, deploy, process or port changes are authorized. Runtime/browser visual certification remains a separate target-specific gate.
