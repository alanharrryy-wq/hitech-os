# Code Atlas agent rules

- Keep `code-atlas.py` compatible unless the user explicitly approves deeper migration.
- New features go under `src/code_atlas/*`.
- Never permanently delete files. Move old folders to `F:\Trash-old`.
- Keep outputs, reports, result ZIPs, and diagnostics in `F:\descargasf`.
- No fake green. Failing tests must generate a fail ZIP/report.
- Preserve rollback for any install/replace operation.
