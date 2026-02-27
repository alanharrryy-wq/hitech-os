# Communication Protocol

## Worker -> Z Required Artifacts

- `STATUS.json`
- `SUMMARY.md`
- `FILES_CHANGED.json`
- `DIFF.patch`
- `SUGGESTIONS.md`
- `SCOPE_LOCK.json`
- `HANDOFF_NOTE.json`
- `LOGS/INDEX.json`

## Z -> Operator Required Artifacts

- `FINAL_REPORT.txt`
- `STATUS.json`
- `FILES_CHANGED.json`
- `DIFF.patch`
- `MERGE_PLAN.md`
- `LOGS/*`

## Anti-Ambiguity Conventions

- Use repo-relative paths.
- Provide deterministic file ordering.
- Include SHA256 per changed file entry.
