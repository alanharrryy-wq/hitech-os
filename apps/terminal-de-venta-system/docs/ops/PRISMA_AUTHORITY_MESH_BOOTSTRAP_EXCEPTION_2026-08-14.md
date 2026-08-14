# PRISMA Authority Mesh one-time bootstrap exception

- Date: `2026-08-14`
- Status: `AUTHORIZED_ONE_TIME_BOOTSTRAP_EXCEPTION`
- Classification: `BUILD / governance-tooling bootstrap`
- Authorized by: repository owner/user in the active PRISMA working session
- Base repository: `prismahitech/hitech-os`
- Base branch: `main`
- Base SHA at authorization: `bf4c61d16ab71a09d5f84de81be3d4e1b8c58134`

## Why this exception exists

Normal PRISMA policy requires a fresh, task-exact Authority Mesh before any repository change. The current remote access can read and write GitHub, but it cannot invoke an arbitrary `workflow_dispatch` with a task payload, while the execution sandbox cannot reach GitHub to clone the repository. This creates a bootstrap deadlock: the repository already contains the read-only AutoMesh engines, but there is no remotely triggerable bridge that can execute them and publish their result ZIP as a GitHub Actions artifact.

The owner explicitly authorized a one-time exception to break only that bootstrap deadlock.

## Exact authorized scope

This exception authorizes only the following repository changes:

1. Add this exception record.
2. Add one GitHub Actions workflow that can execute the existing Code Atlas AutoMesh tooling remotely for the exact `code-atlas-phase0-v1` profile.

No other source, product, runtime, database, schema, generated projection, visual surface, application feature, license flow, deployment, process, port, Prisma client, Factory Ledger capability status, or existing Authority Mesh output is authorized to change under this exception.

## Safety constraints

The bootstrap workflow MUST:

- use `permissions: contents: read`;
- run against a fresh GitHub Actions checkout with `fetch-depth: 0`;
- accept only the exact command `/prisma-automesh code-atlas-phase0-v1`;
- accept the command only from `chatgpt-codex-connector[bot]` or `alanharrryy-wq`;
- invoke existing read-only AutoMesh tooling only;
- use the parallel supervisor so repository drift and child provenance are validated;
- preserve the global 18-worker budget;
- require the existing child evidence contract, including `AUTHORITY_READSET.lock.json`, app impact matrix, contract/gate matrix, unmapped risk, prompt envelope, Authority Mesh report, and both Layer Map files;
- upload the final result/fail ZIP as a GitHub Actions artifact;
- fail closed if AutoMesh fails;
- never push, commit, merge, deploy, write secrets, mutate databases, regenerate Prisma, start/stop processes, or free ports.

## Exception lifecycle

This is an exception to the *pre-change Authority Mesh requirement for installing the remote bridge only*. It is not a waiver for Code Atlas implementation work.

Once the bootstrap workflow is merged, the exception is considered **CONSUMED**. The workflow may be executed read-only as many times as necessary to obtain the first valid task-exact `code-atlas-phase0-v1` PASS artifact, but no additional repository mutation is covered by this exception.

After a valid Phase 0 Authority Mesh exists, all subsequent Code Atlas work returns immediately to normal PRISMA governance. Any modification, including broadening or replacing the remote runner, requires the fresh task-exact Mesh and Factory Ledger classification applicable at that time.

## Factory Ledger handling

The Factory Ledger is intentionally not modified by this bootstrap exception because this change does not certify or advance a product capability. The existing Agent Gate was consulted. Ledger/evidence-index updates, if appropriate, are deferred until the generated Phase 0 Mesh classifies the remote runner and the 50 Code Atlas capabilities with evidence. This avoids manufacturing a `DONE` or `SOURCE_READY` claim before the required authority evidence exists.

## Rollback

Rollback is the Git-native inverse of this isolated bootstrap change: revert/remove the new workflow and this exception record. No product/runtime rollback is expected because the authorized files are governance/tooling only and the workflow has read-only repository permissions.

## Does not prove

This exception record does **not** prove that Code Atlas Phase 0 passed, that any of the 50 capabilities are production-ready, or that the existing placeholders may be implemented. Those claims require the generated task-exact Authority Mesh artifact and subsequent evidence review.
