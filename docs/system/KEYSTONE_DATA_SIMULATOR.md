# KEYSTONE_DATA_SIMULATOR

Deterministic data simulation tooling for Keystone-like API contracts.
This toolchain is **OFF by default** and manual-only until constitution enables policy.

## Modules

- `tools/hos/data/simulator_core.py`
- `tools/hos/data/keystone_shapes.py`
- `tools/hos/data/reference_catalog.py`
- `tools/hos/data/scenarios/*.py`
- `tools/hos/data/export_json.py`
- `tools/hos/data/export_api_mock.py`
- `tools/hos/data/cli_simulate.py`

## Scenarios

- `normal`: healthy baseline with low error pressure.
- `spike`: bursty demand with queue oscillation.
- `degraded`: sustained elevated latency and moderate failures.
- `incident`: high-pressure incident profile.
- `recovery`: post-incident improvement trend.

## Determinism Guarantees

- Seeded PRNG (`--seed`) controls all generated values.
- Stable ordering for runs/events/widgets/layout.
- Stable JSON formatting (sorted keys, LF newline).
- `determinismHash` emitted in simulation metadata.

## Usage

```powershell
python tools/hos/data/cli_simulate.py --scenario normal --seed 1337
python tools/hos/data/cli_simulate.py --scenario incident --seed 9001 --export-api-mock
python tools/hos/data/cli_simulate.py --scenario recovery --seed 20260301 --run-count 120 --duration-minutes 480
```

Outputs are written under `tools/_local/data_sims/...`.

## Output Structure

- `simulation_bundle.json`: full generated payload
- `series.csv`: time-series export
- `api_mock/runs.json` (optional)
- `api_mock/activity.json` (optional)
- `api_mock/widgets.json` (optional)

## Notes

- No app code is modified by simulator execution.
- Simulator payloads are intended for mocks, fixtures, and exploratory tooling workflows.
