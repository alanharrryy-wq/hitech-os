# CAPATCH Git Hygiene And Archive Report

- Generated: 2026-04-09 23:25:47 -06:00
- Scope: CAPATCH runtime artifacts archival + default ignore policy

## Objective
- Keep docs and source files intact (no destructive delete).
- Move ephemeral runtime artifacts to OneDrive archive (`F:\OneDrive\trashingang`).
- Enforce default ignore rules so these artifacts do not reappear in Git status.

## Archive Destination
- Trashingang root: `F:\OneDrive\trashingang\hitech-os\capatch_system_artifacts_20260409_232456`
- Local evidence manifest: `F:\repos\hitech-os\tools\_local\evidence\capatch_archive_moves_20260409_232456\capatch_archive_moves.json`

## Moves Executed
- MOVED: `F:\repos\hitech-os\apps\code-atlas\capatch_system\__pycache__` -> `F:\OneDrive\trashingang\hitech-os\capatch_system_artifacts_20260409_232456\__pycache__`
- MOVED: `F:\repos\hitech-os\apps\code-atlas\capatch_system\capatch_plugins\\_logs` -> `F:\OneDrive\trashingang\hitech-os\capatch_system_artifacts_20260409_232456\capatch_plugins\\_logs`
- MOVED: `F:\repos\hitech-os\apps\code-atlas\capatch_system\integration_reports` -> `F:\OneDrive\trashingang\hitech-os\capatch_system_artifacts_20260409_232456\integration_reports`
- MOVED: `F:\repos\hitech-os\apps\code-atlas\capatch_system\reports\\bundles` -> `F:\OneDrive\trashingang\hitech-os\capatch_system_artifacts_20260409_232456\reports\\bundles`
- MOVED: `F:\repos\hitech-os\apps\code-atlas\capatch_system\reports\\diagnostics` -> `F:\OneDrive\trashingang\hitech-os\capatch_system_artifacts_20260409_232456\reports\\diagnostics`
- MOVED: `F:\repos\hitech-os\apps\code-atlas\capatch_system\tmp` -> `F:\OneDrive\trashingang\hitech-os\capatch_system_artifacts_20260409_232456\tmp`

## .gitignore Updates Applied
- `apps/code-atlas/capatch_system/__pycache__/`
- `apps/code-atlas/capatch_system/capatch_plugins/_logs/`
- `apps/code-atlas/capatch_system/integration_reports/`
- `apps/code-atlas/capatch_system/reports/`
- `apps/code-atlas/capatch_system/tmp/`

## Safety Notes
- No `rm -rf`, no `git clean`, no `git reset --hard` were used.
- Artifacts were moved, not deleted.
- This report does not rewrite history and does not remove tracked docs/source.

## Related Branch/PR Intent
- PR 1: CAPATCH Phase 0 closeout functional compatibility.
- PR 2: Git ignore hygiene + archival movement report (this file).
