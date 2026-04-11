# tools/scripts

General repository utility scripts.

## Purpose

This directory collects reusable repo operations that do not belong inside a single app, service, or package.

## Observed script categories

The bundled repo includes scripts in this directory for:

- docs index generation
- workspace boundary validation
- dependency hygiene
- release discipline
- sensitive path reporting
- repo hygiene reporting
- engineering health collection
- smoke checks
- environment validation
- helper PowerShell commands for local workflows

## Typical examples

- `generate_docs_index.mjs`
- `validate_workspace_boundaries.mjs`
- `check_dependency_hygiene.mjs`
- `report_repo_hygiene.mjs`
- `collect_engineering_health.mjs`

## New scripts added by this patch set

- `check_contract_python_parity.py`
- `check_repo_navigation.py`

These additions are intentionally narrow and focus on:
- contract/Python sync visibility
- navigation / local README coverage

## Usage pattern

Most scripts here are expected to run from repo root.

Examples:

```powershell
node tools/scripts/generate_docs_index.mjs
node tools/scripts/validate_workspace_boundaries.mjs
py tools/scripts/check_contract_python_parity.py --repo-root .
py tools/scripts/check_repo_navigation.py --repo-root .
```

## Boundaries

This directory is a utility layer, not a dumping ground.
Prefer one of these paths before adding new files here:
- if it is app-specific, keep it in the app
- if it is service-specific, keep it in the service
- if it is a repo-wide validator, this directory is appropriate
