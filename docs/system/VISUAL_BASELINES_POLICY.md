# VISUAL_BASELINES_POLICY

Status: **OFF BY DEFAULT**

## Policy

1. Baseline capture and updates are manual-only.
2. Baseline updates require explicit operator intent (`--update-baseline`).
3. No new CI hard gate is enabled by default.
4. Any future CI enforcement must be enabled only after constitution approval.
5. Default baseline ownership is assigned to `B_worker` for factory runs.

## Allowed Paths

- `docs/visual-baselines/<suite>/...` for tracked baseline images.
- `tools/_local/visual/...` for local runtime captures and diffs.

## Determinism Checklist

- Fixed viewport set.
- UTC timezone.
- Animation suppression.
- Stable naming and stable folder structure.
- Comparison output includes threshold and mode.

## Change Management

- Baseline updates should be reviewed like source changes.
- Keep suite names stable (`default`, `keystone`, etc.).
- Avoid ad-hoc path names that encode local machine state.
