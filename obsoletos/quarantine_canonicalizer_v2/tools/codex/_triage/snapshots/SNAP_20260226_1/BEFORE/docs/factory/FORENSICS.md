# Factory Forensics Guide

## Purpose

Provide deterministic evidence for run diagnosis, replay, and audit.

## Core Artifacts

- `tools/codex/runs/<RUN_ID>/RUN_MANIFEST.json`
- `tools/codex/runs/<RUN_ID>/Z_integrator/FINAL_REPORT.txt`
- `tools/codex/runs/<RUN_ID>/Z_integrator/STATUS.json`
- `tools/codex/runs/<RUN_ID>/attestations/bundles.sha256`
- `tools/codex/runs/<RUN_ID>/attestations/ledger.sha256`
- `tools/codex/runs/<RUN_ID>/attestations/report.sha256`
- `tools/codex/runs/factory_ledger.jsonl`
- `tools/codex/runs/factory_ledger.sha256`

## Verify Z No-Write Policy

1. Review `FINAL_REPORT.txt` for `policy:` lines.
2. Confirm all generated paths are under `tools/codex/runs/<RUN_ID>/`.
3. Run integration test:

```powershell
python -m unittest tools.codex.factory.tests.integration.test_factory_pipeline.FactoryPipelineIntegrationTests.test_z_no_write_policy_blocks_on_external_write_attempt
```

## Verify Attestations

1. Generate/refresh:

```powershell
python -m tools.codex.factory integrate --run-id <RUN_ID>
```

2. Check files:

```powershell
Get-Content tools/codex/runs/<RUN_ID>/attestations/bundles.sha256
Get-Content tools/codex/runs/<RUN_ID>/attestations/report.sha256
Get-Content tools/codex/runs/<RUN_ID>/attestations/ledger.sha256
```

3. Validate global ledger signature:

```powershell
python -m tools.codex.factory ledger --raw-events --limit 1
```

`signature.status` must be `PASS`.

## Replay Ledger

Reconstruct run states:

```powershell
python -m tools.codex.factory ledger-replay
python -m tools.codex.factory ledger-replay --run-id <RUN_ID>
```

## Diagnose BLOCKED Runs

1. `python -m tools.codex.factory print-report --run-id <RUN_ID>`
2. `python -m tools.codex.factory ledger --run-id <RUN_ID> --raw-events --limit 200`
3. `python -m tools.codex.factory bundle-validate --run-id <RUN_ID>`
4. `python -m tools.codex.factory integrate --run-id <RUN_ID>`

Typical blockers:

- overlap conflict
- hidden overlap (DIFF.patch path missing from FILES_CHANGED)
- invalid path (absolute/traversal)
- scope violation
- lock collision

## Determinism Reproduction

1. Use explicit run id and base ref:

```powershell
python -m tools.codex.factory oneshot --run-id <RUN_ID> --base-ref HEAD --dry-run
```

2. Re-run integration:

```powershell
python -m tools.codex.factory integrate --run-id <RUN_ID>
```

3. Compare normalized outputs:

```powershell
python -m unittest tools.codex.factory.tests.integration.test_determinism
```
