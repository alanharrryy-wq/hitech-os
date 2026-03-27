# git_sentinel_modular

`git_sentinel_modular` already contains real sentinel lifecycle logic. This bundle closes the seams that still caused drift and confusing ownership:

- one package-aware bootstrap model for `tools.hos.git_sentinel_modular`
- one canonical runtime/path contract
- one internal control plane owned by `operations`
- one package-level CLI surface
- one minimal plugin seam for future external integrations
- one coherent plan-only rollout flow from `shadow -> promotion -> cutover -> execute`

## Current boundary

This package stays focused on its own modular sentinel lifecycle. `engine_guardian`, Cloudflare, Keystone, Repo Analyzer, scheduled tasks, and other external systems remain outside the package boundary.

## Canonical entrypoints

- `python -m tools.hos.git_sentinel_modular --help`
- `python -m tools.hos.git_sentinel_modular shadow-prepare --run-id demo`
- `python -m tools.hos.git_sentinel_modular promotion --workspace-root <path>`
- `python -m tools.hos.git_sentinel_modular cutover --workspace-root <path>`
- `python -m tools.hos.git_sentinel_modular execute-plan --workspace-root <path> --target-root <path>`
- `python -m tools.hos.git_sentinel_modular execute-run --workspace-root <path> --target-root <path> --confirm-token EXECUTE_MANUAL_PROMOTION`
- `python -m tools.hos.git_sentinel_modular status`
- `python -m tools.hos.git_sentinel_modular plugin-list`

## Testing

- `python -m pytest tools/hos/git_sentinel_modular/tests/sentinel_shadow`
- `python -m pytest tools/hos/git_sentinel_modular/tests/sentinel_shadow_apply`
- `python -m pytest tools/hos/git_sentinel_modular/tests/sentinel_supervisor`
- `python -m pytest tools/hos/git_sentinel_modular/tests/sentinel_observability`
- `python -m pytest tools/hos/git_sentinel_modular/tests/integration/test_rollout_pipeline_plan_only.py`

See `docs/TESTING_AND_EXECUTION.md` for the validation path used by the bundle.
