# WORKER_MODEL

## Canonical Workers

- `A_core`: core architecture and foundational implementation.
- `B_tooling`: tooling, pipelines, guardrails, and runtime automation.
- `C_features`: product/feature implementation within assigned scope.
- `D_validation`: validation, testing, policy checks, and risk controls.
- `Z_aggregator`: integration, overlap resolution, and final reporting.
- `R_reviewer`: post-run structural review synthesis over integrated artifacts.
- `E_planner`: post-run task synthesis, dedupe, and task-bank deltas.

## Compatibility Mapping

Legacy naming used in historical docs is mapped as:

- `A_worker` -> `A_core`
- `B_worker` -> `B_tooling`
- `C_worker` -> `C_features`
- `D_worker` -> `D_validation`
- `Z_integrator` -> `Z_aggregator`
- `R_worker` -> `R_reviewer`
- `E_worker` -> `E_planner`

## Required Worker Bundle Artifacts

- `FILES/`
- `DIFF.patch`
- `FILES_CHANGED.json`
- `SUMMARY.md`
- `STATUS.json`
- `SUGGESTIONS.md`
- `SCOPE_LOCK.json`
- `HANDOFF_NOTE.json`
- `LOGS/INDEX.json`
- `DONE.marker`

## Post-Run Required Artifacts

`R_reviewer`:

- `REVIEW_REPORT.json`
- `REVIEW_FINDINGS.json`
- `REVIEW_RECOMMENDATIONS.json`
- `ARCH_REVIEW_SUMMARY.md`

`E_planner`:

- `TASK_BANK_DELTA.json`
- `TASK_BANK_INGEST_REPORT.json`
- `PLANNER_RECOMMENDATIONS.json`
- `PLANNER_SUMMARY.md`

## Rework Transport

Reworks use file-queue (not UI automation):

- Inbox: `tools/codex/runs/<RUN_ID>/_queue/rework/inbox/`
- Outbox: `tools/codex/runs/<RUN_ID>/_queue/rework/outbox/`

Workers must ACK rework completion by writing an outbox done payload before final `DONE.marker` validation.

## Mandatory Worker Reads

Every worker prompt must require reading:

- `KERNEL_CONTEXT.md`
- `docs/factory/FACTORY_RUNTIME_EXPLAINED.md`
- `MODULE_BOUNDARIES.md`
- `ARCHITECTURE_DECISIONS.md`

Workers must run self-checks before completion for:

- `ORPHAN_MODULES`
- `UNUSED_EXPORTS`
- `FILES_CREATED`
- `REAL_CODE_LOC`
- `ARTIFACT_LOC`
