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
- `CODEX_OUTPUT.txt`

## Z -> Operator Required Artifacts

- `FINAL_REPORT.txt`
- `STATUS.json`
- `FILES_CHANGED.json`
- `DIFF.patch`
- `MERGE_PLAN.md`
- `LOGS/*`

## Automation Rules

- Worker closeout artifacts are auto-generated and auto-repaired before `bundle-validate`.
- Preflight runs in auto-repair mode by default.
- Missing worker folders must trigger auto-heal first; blocking is only allowed when recovery fails.
- Prompt hygiene is mandatory: clean-session contract headers are injected during prompt materialization.
- Visual baseline owner default is `B_worker` (`--update-baseline` responsibility).
- Z integrator must run with ledger/watch visibility (`watch` + `ledger`).

## Anti-Ambiguity Conventions

- Use repo-relative paths.
- Provide deterministic file ordering.
- Include SHA256 per changed file entry.
