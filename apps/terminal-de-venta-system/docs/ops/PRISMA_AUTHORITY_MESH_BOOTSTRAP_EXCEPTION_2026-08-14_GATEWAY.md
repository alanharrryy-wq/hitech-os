# PRISMA Authority Mesh remote gateway finalization exception

- Date: `2026-08-14`
- Status: `AUTHORIZED_ONE_TIME_REMOTE_GATEWAY_FINALIZATION_EXCEPTION`
- Classification: `FIX / governance-tooling bootstrap finalization`
- Authorized by: repository owner/user in the active PRISMA working session with instruction to proceed with whatever is necessary
- Base repository: `prismahitech/hitech-os`
- Base branch: `main`
- Base SHA at authorization: `a60534c8bfb2e570478a343c935d7efeed23996e`

## Why this exception exists

The first two bootstrap exceptions established and repaired a read-only GitHub Actions bridge for the fixed `code-atlas-phase0-v1` profile. The resulting Phase 0 Authority Mesh completed successfully and its artifact was recovered with verified repository stability, child provenance, mandatory authority matrices/readsets and Layer Maps.

That bridge is still hard-coded to one fixed profile. Any subsequent task-exact Authority Mesh would otherwise require editing the workflow again before the Mesh could be generated, recreating the same bootstrap deadlock for every future change.

The owner authorized proceeding with the additional work necessary to finish this bootstrap path. This exception exists only to remove that recurring governance deadlock by making the already-read-only bridge accept a strictly validated task specification.

## Exact authorized scope

This exception authorizes only:

1. Add this exception record.
2. Generalize `.github/workflows/prisma-remote-automesh.yml` so an allowed actor may submit a validated task-spec payload to the existing read-only AutoMesh supervisor.
3. Preserve the fixed `/prisma-automesh code-atlas-phase0-v1` command for backward compatibility.
4. Validate the generalized gateway through the repository's normal pull-request checks.
5. After merge, use the gateway to generate fresh task-exact Authority Mesh artifacts before any subsequent Code Atlas repository mutation.

No Code Atlas capability implementation, runtime, database, schema, Prisma generation, deployment, process, port, visual surface, license flow, Factory Ledger promotion or production-certification claim is authorized by this exception.

## Gateway security contract

The generalized workflow MUST:

- retain `permissions: contents: read`;
- run only from pull-request conversation comments;
- accept only actors `chatgpt-codex-connector[bot]` and `alanharrryy-wq`;
- support only the fixed legacy command or `/prisma-automesh task <base64url-json>`;
- decode payload as UTF-8 JSON without `eval`, shell interpolation or executable fields;
- reject unknown top-level and task keys;
- require 2 to 12 tasks;
- require unique task IDs matching a strict lowercase/dash pattern;
- restrict surfaces to the explicit allowlist used by AutoMesh;
- limit each task text and the aggregate task text size;
- derive a deterministic request ID from canonical task JSON;
- invoke only the existing `smart_allmesh_parallel.py` supervisor;
- keep the global worker budget at 18, shards at 54 and parallel lanes bounded;
- preserve mandatory child Authority Readset, matrices, Layer Maps, provenance checks and repository drift verification provided by the existing supervisor;
- upload result/fail ZIP evidence as a GitHub Actions artifact;
- fail closed when the AutoMesh execution does not pass;
- never push, commit, merge, deploy, mutate databases, regenerate Prisma, start/stop processes, free ports, access secrets, or execute caller-supplied shell commands.

## Exception lifecycle

This exception is consumed when the gateway finalization change is merged after repository checks pass.

After consumption, the gateway itself is not a waiver. It is the mechanism used to satisfy normal governance. Every future repository mutation must first receive a fresh task-exact Authority Mesh produced through this read-only gateway or another duly authorized source.

Any later change to the gateway itself requires its own fresh authority decision unless a new bootstrap deadlock is explicitly authorized by the owner.

## Factory Ledger handling

No Factory Ledger capability is promoted by this exception. The gateway is governance infrastructure. Capability classifications remain subject to the recovered Phase 0 evidence and future task-exact Mesh results.

## Rollback

Rollback is Git-native: revert the gateway-generalization commit and this exception record. No product/runtime rollback is expected because the workflow retains read-only repository permissions and this exception authorizes no product mutation.

## Does not prove

This exception does not prove any of the 50 Code Atlas capabilities are complete, contract-backed, runtime-certified or production-ready. It only finalizes the remote mechanism required to obtain fresh task-exact authority before future changes.
