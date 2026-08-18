# PRISMA Authority Mesh run-pointer bootstrap exception

- Date: `2026-08-18`
- Status: `AUTHORIZED_ONE_TIME_RUN_POINTER_BOOTSTRAP_EXCEPTION`
- Classification: `FIX / governance-tooling observability bootstrap`
- Authorized by: repository owner/user in the active PRISMA working session with the explicit instruction to finish and perform all remaining Code Atlas rental-hardening work without using the operator PC
- Base repository: `prismahitech/hitech-os`
- Base branch: `main`
- Base SHA at authorization: `53365ed66c836fbabc77baa714bb382afd1a2b52`

## Why this exception exists

The permanent `PRISMA Remote AutoMesh` gateway already accepts task-exact payloads, executes the read-only preflight -> parallel Mesh -> compose chain, uploads result/fail evidence, and fails closed. The current connected GitHub interface can create the triggering pull-request conversation comment and can fetch/download a workflow artifact once the `run_id` / `artifact_id` is known, but it does not expose a repository-wide listing of `issue_comment` workflow runs. This creates a narrow observability deadlock: the task-exact Mesh can run successfully, yet the controlling agent cannot discover the run/artifact identifiers needed to read the mandatory composed authority evidence.

The repository already documents earlier one-time bootstrap exceptions for exactly this class of governance deadlock. The owner explicitly authorized completing all remaining work and keeping execution remote, so this exception is limited to publishing non-sensitive run pointers after the existing read-only gateway completes.

## Exact authorized scope

This exception authorizes only:

1. Add this exception record.
2. Add `.github/workflows/prisma-remote-automesh-pointer.yml`.
3. The pointer workflow may observe completed runs of workflow `PRISMA Remote AutoMesh`, read only the run/artifact metadata needed for retrieval, and post one bounded pointer comment to canonical tracker issue `#250`.
4. The pointer may publish only: AutoMesh run ID, run attempt, conclusion, head SHA, triggering actor, GitHub run URL, artifact name, artifact ID, artifact size, and expiry timestamp returned by GitHub.
5. Validate this isolated governance/tooling change through normal pull-request checks and merge it if those checks pass.
6. Re-trigger the task-exact rental-hardening Authority Mesh on the then-current `main`, recover the composed artifact through the published pointer, and immediately return to normal Authority Mesh governance before any Code Atlas product/source mutation.

No Code Atlas capability implementation, Customer Runner change, dependency resolver change, independent-evaluator asset, PR #273 `ui_bridge/**` or `app_map/uimap/**` path, PC/Tablet/Mobile/Chart Lab/Shared UI product path, database/Prisma change, licensing change, deployment, process, port, secret, or Factory Ledger capability promotion is authorized by this exception.

## Pointer workflow security contract

The new workflow MUST:

- trigger only from completed `workflow_run` events for `PRISMA Remote AutoMesh`;
- require the original run event to be `issue_comment`;
- accept only triggering actors `chatgpt-codex-connector[bot]` or `alanharrryy-wq`;
- use only `actions: read`, `contents: read`, and `issues: write` permissions;
- perform no checkout and execute no repository source;
- access no repository secrets;
- query only GitHub metadata for the completed run/artifacts;
- post only the bounded metadata allowlist above to issue `#250`;
- never download or inspect artifact contents itself;
- never push, commit, merge, deploy, mutate databases, regenerate Prisma, start/stop processes, free ports, or execute caller-supplied commands;
- fail visibly if artifact metadata cannot be obtained or the pointer comment cannot be published.

## Exception lifecycle

This exception is consumed when the pointer workflow and this record are merged after repository checks pass. It is a bootstrap observability exception only, not an implementation authority waiver.

After merge, the rental-hardening task must receive a fresh task-exact Authority Mesh bound to the current `main` SHA. No P0/P1 source mutation is authorized until the composed Mesh artifact is retrieved and reviewed.

Any later modification to the pointer workflow requires normal fresh task-exact authority unless another true bootstrap deadlock is explicitly authorized by the owner.

## Factory Ledger handling

No Factory Ledger capability is promoted or reclassified under this exception. The pointer workflow is governance observability infrastructure only. Capability status remains governed by the current Ledger and the subsequent task-exact Mesh.

## Rollback

Rollback is Git-native: revert/remove `.github/workflows/prisma-remote-automesh-pointer.yml` and this exception record. No product/runtime rollback is expected because the workflow does not execute product source or mutate product/runtime state.

## Does not prove

This exception does not prove P0 private-repository lifecycle hardening, P1 Go/Java dependency intelligence, P2 external replay, production readiness, privacy/legal/security certification, paid-pilot readiness, human usefulness, or independent-agent replication. It only restores retrievability of the mandatory Authority Mesh evidence needed before those governed steps.
