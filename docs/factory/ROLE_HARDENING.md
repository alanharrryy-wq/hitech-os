# Role Hardening

## A/B/C/D workers

- Must stay inside declared scope lock.
- Must emit required bundle artifacts.
- Required closeout includes `CODEX_OUTPUT.txt` (auto-generated when missing).
- Must not write to another worker bundle.
- If a required folder/path is missing, must auto-repair before declaring `BLOCKED`.
- `B_worker` is default visual baseline owner.

## Z integrator

- Must never invent features.
- Must only merge, validate, report.
- Must block run on missing required artifacts.
- Must monitor run progress via `watch`/`ledger`.
