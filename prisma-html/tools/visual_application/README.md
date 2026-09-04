# Generic Visual Application Engine V1

GVAE V1 applies only exact, already-authorized visual targets. It does not discover authority, infer adapters, expand scope, edit generated product projections directly, or certify browser/runtime visuals.

Flow:

`strict request -> generated Target Index -> exact preflight -> task-exact authority verification -> reviewed Code Atlas UI Bridge plan/diff binding -> deterministic CSS/JSON source writer -> governed projection -> hash refresh -> transaction evidence`

## APPLY authority

`APPLY` fails closed unless all of the following are machine-verified:

1. the request source hash and generated Target Index record still identify one exact target;
2. the supplied Authority Mesh artifact is hash-pinned, `PASS_COMPOSED_AUTHORITY_MESH`, current-head, 100% covered, zero-blocker, provenance-verified, repo-stable, and contains the requested lane's Layer Map;
3. the canonical Factory Ledger anti-rework verifier returns `PASS_ANTI_REWORK_GATE` in `MUTATION` mode for reuse of `visual.generic_application_engine_v1`;
4. the supplied Code Atlas UI Bridge plan and semantic diff are hash-pinned, read-only, `PLAN_READY_FOR_REVIEW` / `DIFF_READY`, and cover the exact selector and CSS properties being changed.

Code Atlas application remains disabled. GVAE consumes its reviewed planning evidence only.

## Writers and transaction safety

CSS mutation is limited to one exact governed selector and existing declarations. The lexical scanner ignores declaration-looking text in comments and string literals and blocks actual priority overrides.

JSON mutation is finite-scalar-only, uses canonical non-negative array indices, and must stay beneath the target's governed JSON Pointer root. JSON application remains blocked unless the UI Bridge gains an explicit governed JSON-root planning contract.

Transactions use contained non-symlink paths, atomic writes, transaction integrity digests, transaction-bound target identity, prevalidated backups, newer-work protection including absent-file states, and two-phase rollback with compensating restoration if execution fails.

Idempotent `APPLY` verifies generated projections and the visual-source manifest instead of returning early. Drift is repaired through a normal protected transaction.

Supported V1 projection modes are the modes already present in the canonical visual-source manifest: `exact-byte-copy` and `existing-rifat-tablet-generator`. Tablet generator mode delegates to `tools/generate_tablet_visual_runtime.py` and uses its own `collect_expected()` output set for rollback coverage.

`PREVIEW`, `APPLY`, `VERIFY`, and `ROLLBACK` remain `SOURCE_STATIC_ONLY`. None of them claims browser rendering, runtime visual certification, all-surface correctness, production readiness, or authorization beyond the exact governed target.


## Mandatory registered-target gate

GVAE is mandatory for every visual mutation that touches a canonical source or generated projection already registered by the generated Visual Target Index.

A successful `APPLY` writes a deterministic transaction-bound receipt under:

`prisma-html/authority/rifat/visual-application-receipts/<transactionId>.json`

The main repository CI and VISCORE1 both run `visual_application.mandatory_gate`. If a registered target source/projection changes without a same-change GVAE receipt chain whose before/after hashes connect the PR base to the PR head, the gate fails closed.

The receipt preserves the exact target, source/projection paths, transaction identity, before/after hashes, current Authority Mesh summary, Factory Ledger decision digest and reviewed Code Atlas UI Bridge plan/diff identity. Receipts remain `SOURCE_STATIC_ONLY` and never claim runtime/browser green.

This rule does not pretend GVAE owns visual code that is not yet registered in the Target Index. Unregistered visual scope must first obtain governed target identity, binding/layer/recipe/adapter/projection authority and Target Index coverage before GVAE can become its mutation path.

## Whole-surface changes

GVAE V1 does not authorize wildcard or broad surface mutation. A whole-surface claim is valid only when the surface has complete governed target coverage and every included target is exact, current and `APPLY_READY`.

Until a complete surface coverage contract exists, a surface redesign must be executed as bounded exact-target waves. A future Surface Batch Orchestrator may coordinate those exact targets, but it must not weaken per-target authority, receipt chains, rollback, projections, manifests, Code Atlas plan/diff binding or post-application runtime visual certification.
