# Factory Runbook

## Goal

Run the Multi-Codex Factory pipeline deterministically with auditable artifacts and explicit PASS/BLOCKED/FAIL outcomes.

## Primary Command

```powershell
python -m tools.codex.factory oneshot --base-ref HEAD --dry-run
```

Use `--run-id <RUN_ID>` to pin an explicit run ID.

## Standard Operator Flow

1. Help:

```powershell
python -m tools.codex.factory --help
```

2. Doctor:

```powershell
python -m tools.codex.factory doctor
```

2. Launch deterministic run scaffolding:

```powershell
python -m tools.codex.factory launch --base-ref HEAD --dry-run
```

3. Validate bundles:

```powershell
python -m tools.codex.factory bundle-validate --run-id <RUN_ID>
```

4. Integrate:

```powershell
python -m tools.codex.factory integrate --run-id <RUN_ID>
```

5. Read ledger:

```powershell
python -m tools.codex.factory ledger --limit 50
python -m tools.codex.factory ledger --raw-events --run-id <RUN_ID> --limit 200
python -m tools.codex.factory ledger-replay --run-id <RUN_ID>
```

6. Open report folder:

```powershell
python -m tools.codex.factory open-report --run-id <RUN_ID>
python -m tools.codex.factory open-run --run-id <RUN_ID>
python -m tools.codex.factory print-report --run-id <RUN_ID>
python -m tools.codex.factory watch --run-id <RUN_ID>
```

## One-Shot Stage Order

`oneshot` executes:

1. `preflight`
2. `launch`
3. `bundle-validate`
4. `integrate`
5. summary emission

The command exits non-zero on any blocked/failed required stage.

## Artifact Layout

All run artifacts must remain under:
`tools/codex/runs/<RUN_ID>/`

Expected directories:

- `tools/codex/runs/<RUN_ID>/A_worker/`
- `tools/codex/runs/<RUN_ID>/B_worker/`
- `tools/codex/runs/<RUN_ID>/C_worker/`
- `tools/codex/runs/<RUN_ID>/D_worker/`
- `tools/codex/runs/<RUN_ID>/Z_integrator/`

Required worker artifacts:

- `STATUS.json`
- `SUMMARY.md`
- `FILES_CHANGED.json`
- `DIFF.patch`
- `SUGGESTIONS.md`
- `SCOPE_LOCK.json`
- `HANDOFF_NOTE.json`
- `LOGS/INDEX.json`

Required integrator artifacts:

- `STATUS.json`
- `FINAL_REPORT.txt`
- `FILES_CHANGED.json`
- `DIFF.patch`
- `MERGE_PLAN.md`
- `LOGS/INDEX.json`

## Status Semantics

- `PASS`: all required checks `rc == 0` and schema validations pass.
- `BLOCKED`: overlap/scope/policy/schema violations or required check non-zero.
- `FAIL`: internal execution error.

`FINAL_REPORT.txt`, `STATUS.json`, and CLI exit code must align.

## Determinism Rules

- Run IDs are deterministic for a fixed `kind + timestamp + existing ledger`.
- Run IDs include base-ref hash token: `<kind>_<utc>_<base_hash>_<seq>`.
- Ledger rendering is deterministic: sort by `ts_utc` then `event_type`.
- Overlap/scope conflict lists are deterministic and stable.
- Feature flags remain off by default.

## Config Layering

Factory config precedence:

1. defaults
2. `tools/codex/factory/factory.config.json` (if present)
3. env vars prefixed with `FACTORY_`
4. CLI overrides

## Z Write Policy

Z-integrator writes are restricted to:
`tools/codex/runs/<RUN_ID>/...`

Any attempted write outside this root is blocked and reported in:

- `Z_integrator/FINAL_REPORT.txt`
- `Z_integrator/STATUS.json`

## Quick Troubleshooting

If `oneshot` is blocked:

1. Inspect `Z_integrator/FINAL_REPORT.txt`
2. Inspect worker `STATUS.json` files
3. Run `bundle-validate` manually for detail
4. Run `ledger --limit 50` to inspect event timeline

If integration is blocked by overlap:

1. Resolve duplicate `FILES_CHANGED` ownership or add explicit shared scope lock entries.
2. Re-run `integrate`.

If integration is blocked by scope:

1. Correct `SCOPE_LOCK.json` or worker file paths.
2. Re-run `bundle-validate` and `integrate`.
