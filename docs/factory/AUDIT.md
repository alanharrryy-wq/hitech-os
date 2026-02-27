# Factory Audit Procedure

## Objective

Provide reproducible evidence that a factory run is deterministic, policy-compliant, and complete.

## Required Inputs

- `RUN_ID`
- Repository commit SHA used for the run
- CLI command transcript

## Required Artifacts

Under `tools/codex/runs/<RUN_ID>/`:

- `RUN_MANIFEST.json`
- `A_worker/*`
- `B_worker/*`
- `C_worker/*`
- `D_worker/*`
- `Z_integrator/FINAL_REPORT.txt`
- `Z_integrator/STATUS.json`
- `Z_integrator/MERGE_PLAN.md`
- `Z_integrator/FILES_CHANGED.json`
- `Z_integrator/DIFF.patch`
- `Z_integrator/LOGS/INDEX.json`

Global ledger:

- `tools/codex/runs/factory_ledger.jsonl`

## Verification Checklist

1. Run manifest:

- `run_id` matches requested run.
- `paths.run_dir` and `paths.integrator_dir` exist.

2. Worker bundle validity:

- `python -m tools.codex.factory.cli bundle-validate --run-id <RUN_ID>` returns `PASS`.
- Required bundle artifacts exist for each worker.

3. Integrator outcome:

- `python -m tools.codex.factory.cli integrate --run-id <RUN_ID>` returns expected status.
- `FINAL_REPORT.txt` includes `Worker bundles processed: 4`.
- `STATUS.json` required checks have expected rc/status.

4. PASS logic:

- Final `PASS` only when required checks are rc=0 and schemas pass.
- `BLOCKED` when overlap/scope/policy violations exist.
- `FAIL` only for internal errors.

5. Z write policy:

- Confirm no writes outside `tools/codex/runs/<RUN_ID>/`.
- If violation attempted, report contains policy violation line.

6. Ledger verification:

- Ledger lines are valid JSON objects.
- Required fields present:
  - `ts_utc`
  - `run_id`
  - `event_type`
  - `actor`
  - `hashes`
  - `rc`
  - `details`
- CLI ledger output is deterministic (sorted by `ts_utc`, then `event_type`).

## Reproduce Deterministically

1. Use explicit run ID:

```powershell
python -m tools.codex.factory.cli oneshot --run-id <RUN_ID> --base-ref HEAD --dry-run
```

2. Repeat integration:

```powershell
python -m tools.codex.factory.cli integrate --run-id <RUN_ID>
```

3. Compare report hash:

- Hash of `FINAL_REPORT.txt` should remain stable for unchanged inputs.

## Evidence Bundle Suggestion

Collect these for review:

- One-shot JSON output (`--json-out`)
- `Z_integrator/FINAL_REPORT.txt`
- `Z_integrator/STATUS.json`
- Last 50 ledger entries (`ledger --limit 50`)
