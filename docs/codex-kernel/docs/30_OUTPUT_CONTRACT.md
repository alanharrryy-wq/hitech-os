# 30_OUTPUT_CONTRACT — Evidence Artifacts and Bundle Standard

STATUS: LAW

## Built‑in Improvements (10)

1. A strict minimum output contract (“invalid if missing”)
2. A bundle schema usable by scripts and humans
3. Deterministic naming and sorting rules
4. Separation: builder bundles vs integrator bundle
5. A diff policy (patch + file list)
6. Command logs as first-class evidence
7. Deletion request mechanism (no silent deletion)
8. Machine-readable status JSON
9. A “what changed” narrative template that prevents ambiguity
10. A lightweight verification checklist for operators

---

## TL;DR

If it’s not in the output, it didn’t happen.

---

## Builder Output (A/B/C/D) — Required

Each builder must produce:

### 1) CODEX_OUTPUT file (repo root of their worktree)

Name:

- `CODEX_OUTPUT_<Agent>_<Scope>.txt`

Must include:

- WHAT CHANGED
- FILES CREATED
- FILES MODIFIED
- DELETION_REQUESTS (if any)
- COMMAND LOGS
- DIFF (full patch preferred)
- FINAL SUMMARY
- BLOCKERS (if any)

Template: `templates/CODEX_OUTPUT_TEMPLATE.md`.

Automation rule:

- If worker output is incomplete, factory auto-closeout must generate/repair `CODEX_OUTPUT` and bundle artifacts before `bundle-validate`.

### 2) Bundle directory (recommended)

Path (recommended):

- `tools/codex/runs/<RUN_ID>/<AGENT>/`

Must include:

- `STATUS.json`
- `SUMMARY.md`
- `FILES_CHANGED.json`
- `DIFF.patch`
- `LOGS/` (typecheck/build/tests)
- `SUGGESTIONS.md`
- `CODEX_OUTPUT.txt`

Schema: `templates/BUNDLE_SCHEMA.md`.

---

## Z Integrator Output — Required

Z must produce:

### 1) FINAL_REPORT.txt

Autocontained report:

- Inputs (branches/worktrees integrated)
- Merge strategy
- Conflicts + resolution
- Repairs made
- Validations run + results
- Final repo status (PASS/BLOCKED)
- Next action (single)

Template: `templates/FINAL_REPORT_TEMPLATE.md`.

### 2) Integrator bundle

Path (recommended):

- `tools/codex/runs/<RUN_ID>/Z_integrator/`

Must include:

- `STATUS.json`
- `FINAL_REPORT.txt`
- `MERGE_PLAN.md`
- `FILES_CHANGED.json`
- `DIFF.patch`
- validation logs

---

## Naming Rules (Deterministic)

- Run IDs: `run_YYYYMMDD_HHMMSS` or monotonic counter
- Agent IDs: `A_core`, `B_surface`, `C_tooling`, `D_validation`, `Z_integrator`
- JSON: stable key order if possible; sort file lists

---

## Deletion Policy

Default: NO deletion, move, rename.

If a delete/move/rename is necessary:

- Do not perform it
- Add to `DELETION_REQUESTS` with justification and migration plan

---

## Operator Verification Checklist (2 minutes)

✅ Every builder has CODEX_OUTPUT  
✅ Every builder bundle has DIFF + FILES_CHANGED + LOGS  
✅ Z produced FINAL_REPORT and STATUS.json  
✅ Validations were executed and logged  
✅ No undocumented deletes/moves/renames
