# Atlas Plus Features

## Atlas Coverage Audit

Module: `src/code_atlas/coverage/atlas_audit.py`

Purpose: compare project files, package ZIP entries, atlas JSON files, and meta/kept manifests. It outputs JSON and Markdown reports with important paths, missing important files, missing atlas nodes, extras, and noise classification.

## Important Files Gate

Module: `src/code_atlas/coverage/important_gate.py`

Purpose: produce a blocking PASS/FAIL decision based on coverage results. Missing important entrypoints and critical DB/tool/source paths block the gate.

## DB Reality Check

Module: `src/code_atlas/db_glass/reality_check.py`

Purpose: read-only SQLite inspection, Prisma schema parsing, migration/seed/env/API route discovery, and inferred ghost relations for columns that look like FKs but are not declared.

## Todo El Show Manifest Plus

Module: `src/code_atlas/manifest/todo_el_show_plus.py`

Purpose: orchestrates the three checks above, writes reports, emits a full tree text file, creates a manifest, and packages everything into a bundle ZIP.
