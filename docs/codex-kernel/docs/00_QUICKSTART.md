# 00_QUICKSTART — Run the Universal 4+1 Factory (Python-first)

STATUS: LAW

## Built‑in Improvements (10)

1. 30‑second TL;DR path
2. “Copy/paste only” operator commands
3. Works for apps/keystone/DB/CRM/slides/CLI (not stack-locked)
4. Deterministic defaults and safe fallbacks
5. Minimal required evidence outputs per run
6. Preflight checks to avoid wasted runs
7. Stop conditions (when to halt and mark BLOCKED)
8. Troubleshooting shortcuts for common failures
9. Clean naming for worktrees/runs/artifacts
10. A “done means done” checklist at the end

---

## TL;DR (30 seconds)

- You run **4 Codex builders** in parallel **in isolated worktrees**.
- Each builder produces a **bundle** (changes + logs + diffs) and a `CODEX_OUTPUT_*.txt`.
- Then you run **Z Integrator** to merge, repair, validate, and produce `FINAL_REPORT.txt`.
- You operate via **Python runner** from VS Code terminal (shell is just a launcher).

---

## Prereqs (Fast)

**Required**

- Git
- Python (Windows: `py -3`)
- The repo is cloned and you have write access

**Optional (only if your project uses them)**

- Node + package manager (pnpm/npm/yarn)
- Playwright (for UI e2e)
- Docker / DB client tools (for DB integration tests)

---

## Folder expectations (Kernel)

The kernel does not enforce a tech stack, but it **does** enforce artifact structure:

- `docs/codex-kernel/` (this folder)
- `tools/codex/` (python runner + runs) ← recommended
- `.run/` or `tools/codex/runs/` (generated artifacts) ← recommended

---

## Golden Operator Flow (Copy/Paste)

### 1) Preflight (do not skip)

From repo root:

- Confirm clean status:
  - `git status`
- Confirm worktrees list:
  - `git worktree list`

If you see weirdness, go to **60_TROUBLESHOOTING.md**.

### 2) Create worktrees (A/B/C/D)

Naming is a contract. Use:

- `<RepoRoot>__codex-A__<scope>`
- `<RepoRoot>__codex-B__<scope>`
- `<RepoRoot>__codex-C__<scope>`
- `<RepoRoot>__codex-D__<scope>`

See `templates/WORKTREE_NAMING.md`.

### 3) Run the 4 builders (A/B/C/D)

Each builder:

- runs inside their worktree
- must not cross scope
- must output:
  - `CODEX_OUTPUT_<Agent>_<Scope>.txt` (repo root of that worktree)
  - bundle directory (recommended) with logs/diff/status

### 4) Run Z Integrator

Z runs from **main repo root** (or a dedicated integration worktree) and:

- merges A/B/C/D branches
- resolves conflicts
- repairs integration breakage
- runs validation commands
- outputs `FINAL_REPORT.txt` + machine-readable `STATUS.json`

---

## Minimal Evidence Required (Per Builder)

A builder output is **invalid** without:

- WHAT CHANGED (plain English)
- FILES CREATED/MODIFIED (explicit list)
- COMMAND LOGS (what ran + results)
- DIFF (full or patch)
- DELETION_REQUESTS (if they think something should be deleted — but they must NOT delete)

Template: `templates/CODEX_OUTPUT_TEMPLATE.md`.

---

## Minimal Evidence Required (Z Integrator)

Z output is **invalid** without:

- Which branches were integrated
- Conflicts encountered + resolution
- Repairs performed (with files)
- Validation commands executed + results
- Final status summary (PASS/BLOCKED) + next actions
- `FINAL_REPORT.txt` + `STATUS.json`

Template: `templates/FINAL_REPORT_TEMPLATE.md`.

---

## Stop Conditions (When to mark BLOCKED)

Stop immediately if any of these occur:

- Worktree corruption (missing `.git` metadata or broken worktree pointers)
- A builder violates additive-only (deletes/moves/renames outside run)
- Conflicts cannot be resolved without changing contracts
- Validation fails in a way that requires re-slicing scope (wrong ownership)

When BLOCKED:

- Do not “push through”
- Produce a BLOCKED report with exact evidence and the single next action

---

## “Done Means Done” Checklist

✅ All builder bundles exist  
✅ Z merged all intended branches  
✅ Z ran validations (as defined by your validation adapter)  
✅ FINAL_REPORT exists and is readable without context  
✅ No undocumented deletions/moves/renames  
✅ Contracts are preserved (single source of truth, deterministic defaults)
