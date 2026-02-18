# 60_TROUBLESHOOTING — Common Failures and Fast Fixes
STATUS: ACTIVE

## Built‑in Improvements (10)
1) Fast symptom → cause → fix mapping  
2) Worktree corruption recovery notes  
3) Merge conflict playbook  
4) Validation failure triage order  
5) Flaky test containment strategy  
6) Environment dependency checklist  
7) “Do not panic” rollback steps  
8) Logging paths and where to look first  
9) Windows-first notes (paths, shells)  
10) Templates for BLOCKED reports  

---

## TL;DR
When something fails, do not freestyle. Follow the triage order.

---

## Triage Order (Always)
1) Preflight / environment
2) Worktrees integrity
3) Guardrails
4) Typecheck/build
5) Unit tests
6) E2E smoke

---

## Worktree Corruption
**Symptom:** git complains about missing `.git` in a worktree  
**Cause:** deleted folder without cleaning worktree metadata  
**Fix:** remove the worktree properly and clean metadata.

Operator steps:
- `git worktree list`
- `git worktree remove <path>` (if possible)
- If stuck: delete the stale entry under `.git/worktrees/` cautiously (backup first)

---

## “Builder crossed scope”
**Symptom:** a builder touched forbidden folders  
**Fix:** revert those changes in that worktree and re-run builder with corrected scope.
**Policy:** Z must not integrate cross-scope work without operator approval.

---

## Merge Conflicts Everywhere
**Symptom:** conflicts in many files across subsystems  
**Cause:** slice was wrong (overlap)  
**Fix:** stop, re-slice ownership using 20_SCOPE_RULES.md.

---

## Validation fails after merge
**Fix order**
1) missing imports / path errors
2) type errors
3) build configuration mismatch
4) test harness config
5) flaky e2e due to selectors/timing

---

## Flaky E2E
Containment:
- reduce e2e to 1–2 deterministic smoke paths
- assert stable test IDs/state
- avoid waits without signals

---

## BLOCKED Report Template
When BLOCKED, produce:
- What failed
- Evidence logs
- Why it cannot proceed
- The single next action
