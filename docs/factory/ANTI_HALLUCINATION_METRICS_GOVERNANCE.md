# Anti-Hallucination + Metrics Governance

## Scope

This policy hardens worker execution against architecture hallucination, LOC padding, and artifact inflation.

Authoritative machine policy:

- `tools/codex/dispatch/execution_rules.json`

Runtime enforcement:

- `python tools/codex/dispatch/validator.py execution-audit --run-id <RUN_ID> --workers A_core,B_tooling,C_features,D_validation,Z_aggregator`

Worker report outputs:

- `tools/codex/runs/<RUN_ID>/<WORKER>/EXECUTION_RULES_REPORT.json`
- `tools/codex/runs/<RUN_ID>/_debug/EXECUTION_RULES_SUMMARY.json`

## Rule Coverage

1. `CONTEXT FIRST`:
- Mandatory reads: `KERNEL_CONTEXT.md`, `docs/factory/FACTORY_RUNTIME_EXPLAINED.md`, `MODULE_BOUNDARIES.md`, `ARCHITECTURE_DECISIONS.md`.
- Prompt contract injection is validated by `validator.py validate-prompts`.

2. `ARCHITECTURE CONSTRAINTS`:
- Enforced top-level domains: `apps/`, `packages/`, `tools/`, `docs/`.
- Forbidden architecture roots on new files: `engine/`, `framework/`, `runtime/`, `platform/`, `orchestrator/`, `manager/`, `controller/`, `pipeline/`.

3. `PRODUCT IMPACT RULE`:
- Worker/run changes must touch `apps/` or `packages/`.
- Changes limited to tooling domains are blocked as low product impact.

4. `MODULE + ORPHAN CHECKS`:
- New module reference checks and test-reference checks are evaluated.
- Strict orphan blocking is configurable in `execution_rules.json`.

5. `FILE CREATION + FILE SIZE`:
- Run-level max new files enforced (`max_new_files_per_run`).
- Hard file size limit enforced (`file_size_hard_max_loc`).
- Recommended file-size band tracked as warnings.

6. `UTILITY EXPLOSION GUARD`:
- New generic utility names (`utils.*`, `helpers.*`, `common.*`, `shared.*`) are blocked.

7. `LOC SIGNAL POLICY`:
- Real-code extensions only: `.ts`, `.tsx`, `.js`, `.mjs`, `.py`, `.ps1`.
- Artifact-heavy change sets are blocked when ratios violate policy thresholds.

8. `TEST RATIO + CHANGE DENSITY`:
- Test LOC ratio is tracked.
- File-count density is tracked to avoid tiny-file floods and single-file blowups.

9. `AUTOMATIC SELF-CHECK`:
- Prompt contract requires self-check declaration for:
`ORPHAN_MODULES`, `UNUSED_EXPORTS`, `FILES_CREATED`, `REAL_CODE_LOC`, `ARTIFACT_LOC`.

## Operating Notes

- This governance does not replace `meaningful_execution_gate`; it complements it.
- Failures trigger rework/blocking in `rework-cycle` and `validate-guardrails`.
- Warnings remain visible in worker and run reports for operator review.
