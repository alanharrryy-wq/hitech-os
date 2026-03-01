# VISUAL_REGRESSION

Visual tooling harness for deterministic screenshot capture and baseline comparison.
This capability is **OFF by default** and opt-in only.

## Modules

- `tools/hos/visual/storybook_detect.py`
- `tools/hos/visual/storybook_runner.py`
- `tools/hos/visual/playwright_capture.py`
- `tools/hos/visual/baseline_store.py`
- `tools/hos/visual/compare.py`
- `tools/hos/visual/cli_visual.py`

## Storage

- Tracked baselines: `docs/visual-baselines/`
- Runtime captures: `tools/_local/visual/capture/`
- Runtime current snapshots: `tools/_local/visual/current/`
- Runtime diff outputs: `tools/_local/visual/diff/`

## Determinism Controls

- Fixed viewport matrix in capture script.
- UTC timezone and light color scheme in browser context.
- Animation/transition disabling via injected style.
- Stable file naming: `target__viewport.png`.

## Usage

```powershell
python tools/hos/visual/cli_visual.py --suite keystone --base-url http://127.0.0.1:6007 --target root=/
python tools/hos/visual/cli_visual.py --suite keystone --update-baseline
python tools/hos/visual/cli_visual.py --suite keystone --threshold 0.01 --strict
```

## Optional Storybook Auto-Start

```powershell
python tools/hos/visual/cli_visual.py --suite keystone --start-storybook --port 6007
```

If no Storybook workspace is detected, the command continues against `--base-url` unless `--strict` is set.

## Baseline Update Policy

- Baseline updates require explicit `--update-baseline`.
- No automatic baseline updates are configured in CI.
- Baselines remain optional until constitution enables mandatory enforcement.
- Factory default ownership for baseline update is `B_worker`.
