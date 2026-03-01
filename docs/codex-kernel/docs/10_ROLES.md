# 10_ROLES — Universal Definitions for A/B/C/D Builders + Z Integrator

STATUS: LAW

## Built‑in Improvements (10)

1. Universal roles (not “frontend/backend only”)
2. Explicit Allowed Surfaces + Forbidden Actions per role
3. Clear success criteria per role (“what DONE looks like”)
4. Required artifacts per role (evidence)
5. Ownership boundary rules to prevent scope wars
6. Integration-safe contracts (interfaces, schemas, APIs)
7. “If you must change contracts” escalation path
8. Examples for multiple project types
9. Quick decision table for “who owns this change?”
10. A role-to-risk map (what breaks if they cross boundaries)

---

## TL;DR

- **A/B/C/D** are builders with strict scope ownership.
- **Z** is the integrator: merge + repair + validate + report (no feature invention).
- Roles are defined by **layer**, not by technology.

---

## The Five Roles (Universal)

### CODEX‑A — Core / Domain / Truth Layer

**Purpose:** implement the system’s “truth”: domain rules, schemas, core logic.

**Allowed surfaces**

- Domain models, schemas, invariants
- Use-cases/services (business logic)
- DB migrations/constraints (if DB-centric)
- Shared contracts consumed by others (types, OpenAPI, protobuf, JSON schema)

**Forbidden**

- Styling/layout polish as the main deliverable
- Editing global tooling/CI unless explicitly assigned
- Cross-cutting refactors outside scope

**DONE means**

- Contracts are explicit and stable
- Unit-level correctness evidence exists
- No hidden side effects; deterministic defaults

**Required artifacts**

- CODEX_OUTPUT file
- Worker bundle artifacts (STATUS/SUMMARY/FILES_CHANGED/DIFF/SUGGESTIONS/SCOPE_LOCK/HANDOFF/LOGS/INDEX/CODEX_OUTPUT.txt)
- Diff/patch
- Minimal validation log (unit checks if applicable)

---

### CODEX‑B — Interface / UX / Surface Layer

**Purpose:** build the operator/user surface: UI/CLI/admin tools, deck surfaces, interaction layers.

**Allowed surfaces**

- UI components/screens/routes
- Interaction flows (state wiring using A’s contracts)
- Test IDs / selectors stability (if tests exist)
- Accessibility/usability affordances

**Forbidden**

- Breaking or silently changing core contracts
- Adding timer-driven control as primary mechanism
- Changing infra/CI globally unless assigned

**DONE means**

- Surface is operable with safe defaults
- Uses core contracts cleanly
- Deterministic interactions (no “autoplay” control)

**Required artifacts**

- CODEX_OUTPUT file
- Screenshot/trace evidence if UI changed (optional but recommended)
- Worker bundle artifacts (STATUS/SUMMARY/FILES_CHANGED/DIFF/SUGGESTIONS/SCOPE_LOCK/HANDOFF/LOGS/INDEX/CODEX_OUTPUT.txt)
- Diff/patch

---

### CODEX‑C — Infra / Tooling / Guardrails Layer

**Purpose:** make the project reproducible: build/test scripts, CI, lint/format, security/guardrails.

**Allowed surfaces**

- Tooling scripts, runners, build configs
- Guardrails (boundary checks, overlap checks)
- Performance diagnostics harness (non-invasive)
- Repo hygiene automation (without deleting history)

**Forbidden**

- Implementing business features
- Restructuring product code without explicit scope
- Adding noisy global behaviors (keybinds, timers) without consent

**DONE means**

- Running the project is simpler and more deterministic
- Guardrails prevent future drift
- Changes are additive and documented

**Required artifacts**

- CODEX_OUTPUT file
- Validation logs (build/test/guards)
- Worker bundle artifacts (STATUS/SUMMARY/FILES_CHANGED/DIFF/SUGGESTIONS/SCOPE_LOCK/HANDOFF/LOGS/INDEX/CODEX_OUTPUT.txt)
- Diff/patch

---

### CODEX‑D — Quality / Tests / Docs / Release Confidence

**Purpose:** ensure truth via tests and docs: unit/integration/e2e smoke, runbooks, checklists.

**Allowed surfaces**

- Tests (unit/integration/e2e)
- Docs and runbooks
- Fixtures and deterministic harness helpers

**Forbidden**

- Changing production behavior to “make tests pass” unless explicitly approved
- Large refactors outside test harness scope

**DONE means**

- Deterministic smoke coverage exists for critical surfaces
- Docs are navigable (indexed) and match reality

**Required artifacts**

- CODEX_OUTPUT file
- Test run logs and artifacts paths (trace/screenshot if applicable)
- Worker bundle artifacts (STATUS/SUMMARY/FILES_CHANGED/DIFF/SUGGESTIONS/SCOPE_LOCK/HANDOFF/LOGS/INDEX/CODEX_OUTPUT.txt)
- Diff/patch

---

### CODEX‑Z — Integrator (Merge + Repair + Validate + Report)

**Purpose:** integrate A/B/C/D outputs into a single coherent repo state.

**Allowed surfaces**

- Merge/rebase/resolve conflicts
- Repair integration breaks (imports/types/build/test)
- Run validations and guardrails
- Generate the final report bundle

**Forbidden**

- Inventing new features
- Expanding scope beyond integration repair
- Deleting/moving/renaming existing files unless explicitly allowed

**DONE means**

- Integrated branch builds/tests/validates per adapter
- All conflicts documented with rationale
- FINAL_REPORT is sufficient to understand state without context

**Required artifacts**

- FINAL_REPORT.txt + STATUS.json
- Files changed list + diffs
- Validation logs

---

## Who Owns This Change? (Decision Table)

| Change Type                                      | Owner | Notes                              |
| ------------------------------------------------ | ----- | ---------------------------------- |
| Domain rules / schemas / migrations              | A     | B consumes, D tests                |
| UI/UX surface / components / operator flows      | B     | Must not mutate contracts silently |
| CI/build scripts / guardrails / runners          | C     | Must stay deterministic            |
| Tests / docs / runbooks                          | D     | Must reflect reality               |
| Merge conflicts / cross-branch integration fixes | Z     | No new features                    |

---

## Escalation: Contract Changes

If a builder must change a contract:

1. They stop and mark it in CODEX_OUTPUT under **CONTRACT_CHANGE_REQUEST**
2. They propose:
   - old contract
   - new contract
   - migration plan
3. Z does NOT decide this alone — operators (you + ChatGPT) decide.
