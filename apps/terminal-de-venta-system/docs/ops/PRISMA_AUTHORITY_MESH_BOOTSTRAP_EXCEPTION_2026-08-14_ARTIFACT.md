# PRISMA Authority Mesh artifact-retrieval bootstrap exception

- Date: `2026-08-14`
- Status: `AUTHORIZED_ONE_TIME_ARTIFACT_RECOVERY_EXCEPTION`
- Classification: `FIX / governance-tooling artifact publication`
- Authorized by: repository owner/user in the active PRISMA working session
- Base repository: `prismahitech/hitech-os`
- Base branch: `main`
- Base SHA at authorization: `b8cd13d93118b7d7fb73145143ee7b2aa095fd50`

## Why this exception exists

The first one-time bootstrap exception successfully installed the read-only remote AutoMesh runner and the first remote `code-atlas-phase0-v1` execution completed the task-exact parallel Authority Mesh with all ten lanes, mandatory Layer Maps, child provenance, repo drift verification and final result ZIP generation.

The run then failed only in the GitHub Actions artifact publication step because the staged evidence directory was named `.remote-automesh-artifacts`, while `actions/upload-artifact@v7` was running with hidden files/directories excluded. GitHub therefore reported no files found even though staging had already listed the result ZIP and task-spec JSON.

The generated runner workspace is ephemeral, so the successful Phase 0 evidence cannot be recovered after job cleanup. A second read-only run is required solely to reproduce and publish the same evidence.

## Exact authorized scope

This exception authorizes only:

1. Add this exception record.
2. Change the remote AutoMesh staging directory from `.remote-automesh-artifacts` to `remote-automesh-artifacts` and update the matching upload path.
3. Re-run the exact `/prisma-automesh code-atlas-phase0-v1` profile to reproduce the same read-only Authority Mesh and publish its artifact.

No Code Atlas capability implementation, product source, runtime, database, schema, Prisma generation, deployment, process, port, visual surface, license flow, Factory Ledger capability promotion or existing Authority Mesh output may be changed under this exception.

## Evidence from the failed publication run

GitHub Actions run `31790277134` showed:

- `smart_allmesh_automesh.py --self-test`: PASS;
- exact Phase 0 task-spec creation: PASS;
- `Run task-exact parallel Authority Mesh`: PASS;
- ten child AutoMesh lanes completed;
- final repository snapshot and drift check completed;
- final supervisor certification: `AutoMesh paralelo v2 certificado`;
- final result ZIP created as `allmesh-par_1408 095821_230066008c8f_result.zip`;
- staging listed both `code-atlas-phase0-v1.tasks.json` and the result ZIP;
- only `actions/upload-artifact@v7` failed with `No files were found with the provided path: .remote-automesh-artifacts/**`.

## Safety constraints

The workflow MUST retain:

- `permissions: contents: read`;
- exact command `/prisma-automesh code-atlas-phase0-v1`;
- actor restriction to `chatgpt-codex-connector[bot]` or `alanharrryy-wq`;
- existing task-spec contents;
- existing parallel AutoMesh supervisor;
- global 18-worker budget;
- mandatory child Authority Readset/matrices/Layer Maps;
- child provenance validation;
- repository drift validation;
- result/fail publication and fail-closed behavior.

## Exception lifecycle

This exception is consumed when the artifact-path correction is merged. It allows the same read-only Phase 0 profile to be re-run only to obtain the retrievable PASS/fail artifact needed to review authority evidence.

Once a retrievable Phase 0 artifact exists, no further repository mutation is covered by this exception. Subsequent Code Atlas work returns to normal fresh task-exact Authority Mesh governance.

## Factory Ledger handling

No Factory Ledger capability is promoted or reclassified under this exception. The first recovered Phase 0 artifact must be reviewed before any capability status is changed.

## Rollback

Rollback is Git-native: revert the workflow path correction and this exception record. No product/runtime rollback is expected because this change is governance/tooling-only and repository permissions remain read-only.

## Does not prove

This exception does not itself prove that Code Atlas capabilities are complete or production-ready. It only authorizes recovery of the Authority Mesh evidence required to make those decisions.
