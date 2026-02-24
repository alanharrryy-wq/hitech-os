# KERNEL_CONTEXT

Status: Bootstrap
Project: HITECH OS
Last Updated: 2026-02-23

## PROJECT_NAME

HITECH OS

## PROJECT_REASON

Build a deterministic multi-agent monorepo/factory with OS-like governance (Blueprint->Evidence->Decision->Next) and local-first execution.

## FINAL_GOAL

Self-executable governance system: stage blueprints + rich index + evaluator (PASS/WARN/FAIL) + reports with single NEXT + multi-worker integration (A/B/C/D/Z) + policy engine (debt/no-regression/immutability) with deterministic evidence; offline-first.

## GOVERNANCE_RULES

- determinism
- offline-first
- no silent passes
- WARN=>DEBT
- feature flags OFF
- modularity strict

## MULTI_CODEX_FACTORY

- Workers: A, B, C, D
- Aggregator: Z_aggregator
- Run bundle location: `tools/codex/runs/<RUN_ID>/`
- Ledger mode: append-only
- Attestation model: required

## KEY_DOCS_AUTHORITY

- `docs/CONTRACT.md` (root authority)
- `docs/factory/CONTRACT.md`
- `docs/codex-kernel/docs/30_OUTPUT_CONTRACT.md`
- `docs/integration/JOBS_CONTRACT.md`
- `packages/contracts/...` schemas

## OUTPUT: DIFF + CODE MUST BE PLAIN TEXT

- Final response MUST include a `CHANGED FILES` list.
- Final response MUST NOT include unified diffs.
- Unified diff patches MUST be plaintext with no ANSI color sequences (`git diff --no-color --patch` or equivalent) and written to disk as `.patch` artifacts in the run bundle.
- Final response MUST include patch file paths and brief summaries only (no raw diff blocks).
- Final response MAY include targeted file excerpts only when explicitly requested.
- Never rely only on UI color diffs.
- If it is not in the final plaintext output, it did not happen.
- Primary output is `tools/codex/Z_aggregator/RUN_<RUN_ID>/FINAL_REPORT.txt`; UI diffs are optional and must not be relied upon.

## CURRENT_TASK_FOCUS

- Fix git argument dropping in PowerShell scripts.
- Safe swap `docs/CONTRACT_STAGE.md` -> `docs/CONTRACT.md` with content-only integrity check.

## STAGE_SKELETON_AUTHORITATIVE_IDS

- Stage 0: `S0_ORIG`, `S0_DET`, `S0_PRI`, `S0_LEX`, `S0_PROOF`, `S0_NSP`, `S0_TRUST`
- Stage 1: `S1_DEF`, `S1_BLP`, `S1_INV`, `S1_GATE`, `S1_POL`, `S1_DEBT`, `S1_IDX`, `S1_OUT`, `S1_FAIL`, `S1_PROM`
- Stage 2: `S2_DEF`, `S2_MIG`, `S2_ANT`, `S2_NRG`, `S2_ESC`, `S2_SCOPE`, `S2_IMM`, `S2_PROM`
- Stage 3: `S3_DEF`, `S3_OBS`, `S3_JOB`, `S3_CAP`, `S3_AUTO`, `S3_EXC`, `S3_PROM`
- Stage 4: `S4_DEF`, `S4_REL`, `S4_SEC`, `S4_MOD`, `S4_AUD`, `S4_PROM`
- Cross-stage systems: `SYS_IDX`, `SYS_BLP`, `SYS_GATE`, `SYS_DEBT`, `SYS_DOC`, `SYS_RUN`, `SYS_LED`
- Rendering and operator UX: `UX_IDX`, `UX_STA`, `UX_NXT`, `UX_TREE`
- Evolution and versioning: `EV_SCH`, `EV_BLP`, `EV_CON`, `EV_COMP`
