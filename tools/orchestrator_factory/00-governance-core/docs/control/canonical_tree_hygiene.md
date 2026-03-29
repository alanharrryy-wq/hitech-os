
# Canonical Tree Hygiene

Canonical framework artifacts must describe the logical framework, not interpreter exhaust.

## Exclude from the canonical tree
- `__pycache__/`
- `*.pyc`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `.DS_Store`
- `Thumbs.db`
- temporary archives and editor swap files

## Why this matters
- tree docs become misleading when runtime junk appears as if it were designed structure
- starter bundles should stay portable and deterministic
- operators should not confuse cache output with governed assets

## Source of truth
Use:
`configs/execution_framework/canonical_tree_excludes.json`

## Enforcement
- `tools/execution_framework/smoke_framework_checks.py` should flag runtime junk in the framework tree
- tree docs should show the clean logical structure only
- starter kits should be repackaged from a clean tree
