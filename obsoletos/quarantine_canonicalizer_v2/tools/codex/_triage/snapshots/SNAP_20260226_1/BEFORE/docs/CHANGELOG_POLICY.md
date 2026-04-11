# CHANGELOG POLICY

Version: 1.0.0
Last Updated: 2026-02-23

## Scope

Applies to governance docs, contracts, runtime interfaces, and validation gates.

## Policy

1. Any breaking contract change requires an explicit changelog entry before merge.
2. Changelog entries must include date, scope, reason, and rollback guidance.
3. Intent changes belong in `docs/CONSTITUTION.md`; enforcement changes belong in `docs/CONTRACT.md`.
4. Runtime contract updates must reference impacted files and validation evidence.
5. Temporary debt/exception items must be mirrored in `docs/NOTEBOOK.md`.

## Minimum Entry Format

- Date (UTC)
- Area (`contracts`, `runtime`, `docs`, `validation`)
- Change summary
- Compatibility impact (`none`, `minor`, `breaking`)
- Required follow-up actions
