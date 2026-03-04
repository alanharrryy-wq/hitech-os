# CONTEXT_LAYER

## Purpose

`_context/` is the frozen run context package for deterministic multicodex execution.

## Location

- `tools/codex/runs/<RUN_ID>/_context/`

## Required Contents

- `RUN_MANIFEST.json`
- `REPO_FINGERPRINT.json`
- `CONTEXT_FINGERPRINT.json`
- `REPO_TREE.txt`
- `TARGET_FILES.txt`
- `CONTRACT_SOURCES.txt`
- `CONTRACT_SUMMARY.md`
- `KERNEL_CONTEXT.md`
- `FACTORY_RUNTIME_EXPLAINED.md`
- `MODULE_BOUNDARIES.md`
- `ARCHITECTURE_DECISIONS.md`
- `WORKER_INPUTS/<WORKER>.md`
- `SHARED_REFERENCES.md`
- `OPEN_QUESTIONS.md`

## Generation

- Built deterministically by:
  - `python tools/codex/factory/context_layer.py --run-id <RUN_ID> --workers A_core,B_tooling,C_features,D_validation,Z_aggregator`

## Determinism Rules

1. Context files are written with stable ordering.
2. `CONTEXT_FINGERPRINT.json` hashes each file and the aggregate context.
3. Workers consume context as read-only input.
4. Re-running context generation for the same run is idempotent.
