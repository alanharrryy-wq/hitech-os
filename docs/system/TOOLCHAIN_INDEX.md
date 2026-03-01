# TOOLCHAIN_INDEX

Status for all modules below: **OFF BY DEFAULT until Constitution**

## Core

- `tools/hos/_core/repo_root.py`: repo root detection from arbitrary cwd.
- `tools/hos/_core/paths.py`: safe path joins and forbidden-path registry helpers.
- `tools/hos/_core/log.py`: deterministic structured logger.
- `tools/hos/_core/stable_json.py`: stable JSON read/write.
- `tools/hos/_core/stable_text.py`: normalized text writing.
- `tools/hos/_core/cli.py`: subcommand registry helpers.
- `tools/hos/_core/progress.py`: terminal progress utility (Windows-friendly).
- `tools/hos/_core/reports.py`: deterministic report writer for docs/system and tools/_local.
- `tools/hos/_core/exec.py`: safe subprocess execution wrapper.
- `tools/hos/_core/hashing.py`: deterministic hashing utilities.

## Turbo

- `tools/hos/turbo/resolve_profile.py`
- `tools/hos/turbo/turbo_wrap.py`
- `tools/hos/turbo/remote_cache_check.py`
- `tools/hos/turbo/generate_ci_snippets.py`
- `tools/hos/turbo/profiles.json`

Reference docs:
- `docs/system/REMOTE_CACHE_SETUP.md`
- `docs/system/TURBO_PROFILES.md`

## Data Simulation

- `tools/hos/data/cli_simulate.py`
- `tools/hos/data/simulator_core.py`
- `tools/hos/data/keystone_shapes.py`
- `tools/hos/data/export_json.py`
- `tools/hos/data/export_api_mock.py`
- `tools/hos/data/scenarios/*.py`

Reference docs:
- `docs/system/KEYSTONE_DATA_SIMULATOR.md`

## Visual Regression

- `tools/hos/visual/cli_visual.py`
- `tools/hos/visual/storybook_detect.py`
- `tools/hos/visual/storybook_runner.py`
- `tools/hos/visual/playwright_capture.py`
- `tools/hos/visual/baseline_store.py`
- `tools/hos/visual/compare.py`

Reference docs:
- `docs/system/VISUAL_REGRESSION.md`
- `docs/system/VISUAL_BASELINES_POLICY.md`

## UI Scaffolding

- `tools/hos/ui/scaffold_component.py`
- `tools/hos/ui/mirror_state.py`
- `tools/hos/ui/controls/generate_controls.py`
- `tools/hos/ui/controls/templates/*`

Reference docs:
- `docs/system/UI_SCAFFOLDING.md`
- `docs/system/MIRROR_INPUTS.md`

## Hygiene + Doctor

- `tools/hos/hygiene/cli_hygiene.py`
- `tools/hos/hygiene/scan_root_artifacts.py`
- `tools/hos/hygiene/scan_worktree_contamination.py`
- `tools/hos/hygiene/scan_large_files.py`
- `tools/hos/doctor/doctor.py`

Reference docs:
- `docs/system/REPO_HYGIENE.md`
- `docs/system/HYGIENE_REPORT_SAMPLE.md`

## Optional Scripts

- `pnpm -w run hos:doctor`
- `pnpm -w run hos:turbo`
- `pnpm -w run hos:visual`
- `pnpm -w run hos:simulate`
- `pnpm -w run hos:hygiene`

These scripts are optional entrypoints and do not enforce new CI steps.

