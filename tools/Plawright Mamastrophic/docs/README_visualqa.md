# VisualQA extension for Plawright Mamastrophic

Adds `RUN.ps1 -Mode visualqa -Surface <surface>` without renaming the tool or changing the no-start/no-kill/no-DB/no-deploy policy.

## What it adds

- DOM snapshots under `dom/<surface>/*.dom.json`
- Computed style captures under `dom/<surface>/*.computed.json`
- Screenshots under `screens/<surface>/*.png`
- Summaries and CSVs under `reports/`
- Offline surfaces reported as `skipped_offline`
- Non-strict offline skips produce `PARTIAL_PASS`
- `-Strict` converts skips into failure

## Key reports

- `reports/SUMMARY.md`
- `reports/visualqa.summary.json`
- `reports/visualqa.full.json`
- `reports/computed-layers.csv`
- `reports/background-obstructions.csv`
- `reports/route-status.csv`
- `reports/console-errors.csv`
- `reports/network-failures.csv`

## Policy

This phase observes only. It does not modify CSS, TSX, assets, databases, services, or deployment state.
