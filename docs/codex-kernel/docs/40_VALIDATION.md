# 40_VALIDATION — Pluggable Validation Adapter (Python-first + Optional Playwright)
STATUS: LAW

## Built‑in Improvements (10)
1) Pluggable adapter design (stack-agnostic)
2) Default deterministic policy (offline-first)
3) Minimal “smoke” philosophy (fast, brutal, reliable)
4) Optional Playwright executed under Python control
5) Support matrix examples: Node/TS, Python, .NET, Go, DB tools
6) A strict logging contract for every command
7) Failure classification (flaky vs deterministic)
8) Stop conditions + rollback guidance
9) Recommended file format (YAML/JSON) with schema notes
10) A repeatable “validation recipe” per run

---

## TL;DR
Validation is not “tests”. Validation is the evidence pipeline that decides if integration is allowed.

---

## Design Goals
- Stack-agnostic
- Deterministic by default
- Minimal but meaningful checks
- Always logged, always reproducible

---

## Adapter Concept
A per-repo file defines commands by category:
- preflight
- typecheck/lint
- build
- unit
- integration
- e2e_smoke
- guardrails

The Python runner:
- loads the adapter
- executes commands in order
- captures stdout/stderr to logs
- writes `STATUS.json`

### Required vs Optional (Gate Semantics)
- Each command may declare `required: true|false`.
- Required commands determine final PASS/BLOCKED.
- Optional commands may fail without changing final PASS.
- `allow_fail` must remain `false` for required gates such as `typecheck`, `build`, and `test_unit`.

---

## Recommended Location
- `tools/codex/validation.yaml` (or `.run/validation.yaml`)

---

## Example Adapter (Conceptual)
```yaml
version: 1
preflight:
  - { name: git_status, cmd: "git status --porcelain=v1" }

node:
  detect: { any_files: ["package.json", "pnpm-lock.yaml"] }
  commands:
    - { name: typecheck, cmd: "pnpm -w -r typecheck" }
    - { name: build, cmd: "pnpm -w -r build" }

python:
  detect: { any_files: ["pyproject.toml", "requirements.txt"] }
  commands:
    - { name: lint, cmd: "python -m ruff check ." }
    - { name: test, cmd: "python -m pytest -q" }

playwright:
  detect: { any_files: ["playwright.config.ts"] }
  commands:
    - { name: e2e_smoke, cmd: "npx playwright test --reporter=line" }

guardrails:
  commands:
    - { name: no_overlap, cmd: "python tools/codex/guards/no_overlap.py" }
```

---

## Playwright Policy (Optional but recommended for UI)
- Playwright is a tooling dependency, not a coordination dependency.
- The operator still uses Python; Python calls Playwright as a subprocess.
- E2E should be **smoke minimal**:
  - 1–2 representative flows
  - avoid timing guesses
  - assert deterministic signals (test ids/state)

---

## Logging Contract (Required)
For every command:
- log file stored under the run bundle
- includes:
  - command string
  - working directory
  - start/end time
  - exit code
  - captured output

---

## Failure Classification
- **Deterministic failure:** consistent under rerun → must fix before proceeding.
- **Flaky failure:** non-deterministic → must be minimized by better assertions or reduced scope.
- **Environment failure:** missing tools/keys → mark BLOCKED with exact missing dependency.

---

## Stop Conditions
Stop the run and mark BLOCKED if:
- preflight fails
- guardrails fail
- deterministic validations fail
- a required tool is missing (unless explicitly optional)

---

## Validation Recipe (Per Integration)
Minimum recommended:
1) preflight
2) guardrails
3) typecheck/lint
4) build
5) unit
6) e2e_smoke (if UI)
