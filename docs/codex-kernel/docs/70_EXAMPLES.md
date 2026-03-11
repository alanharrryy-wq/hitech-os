# 70_EXAMPLES — Universal Patterns (Web App / DB / CRM / Slides / CLI)

STATUS: ACTIVE

## Built‑in Improvements (10)

1. Five archetypes, same kernel roles
2. Copy/paste scope briefs (patterns)
3. Example validation adapter entries per archetype
4. Example “DONE” definitions per archetype
5. Example Z merge plan per archetype
6. Common pitfalls per archetype
7. Minimal smoke test ideas (deterministic)
8. “What to log” examples
9. How to keep additive-only while moving fast
10. How to avoid parallel implementations

---

## TL;DR

These are patterns. Don’t cargo-cult the folder names; cargo-cult the boundaries.

---

## Example 1 — Web App (UI + API)

**Scopes**

- A: domain + API contracts
- B: tooling/CI/guards
- C: UI surface
- D: tests/docs

**Smoke validation idea**

- typecheck + build
- 1 e2e smoke: login -> primary flow (if applicable)

---

## Example 2 — DB-Heavy System

**Scopes**

- A: schema + migrations + constraints
- B: env harness (docker compose, seed tools)
- C: query adapters / admin surface
- D: integrity tests + migration tests + runbooks

**Smoke validation idea**

- migrate up/down
- seed minimal dataset
- run 2–3 invariant checks

---

## Example 3 — CRM Workflow Engine

**Scopes**

- A: permissions + audit + workflow rules
- B: import/export tooling + guardrails
- C: operator UI dashboards/forms
- D: end-to-end workflow tests + docs

---

## Example 4 — Interactive Slides / Deck

**Scopes**

- A: state/replay/evidence contracts
- B: determinism + guards + runner
- C: visual surfaces/modules
- D: e2e smoke + runbooks

---

## Example 5 — CLI Tool

**Scopes**

- A: core logic + command contracts
- B: packaging/release scripts
- C: CLI UX (help text, prompts, formatting)
- D: golden tests + docs

---

## Z Merge Plan Examples

- Web app: merge A then C then D then B (or B earlier if it provides shared tooling)
- DB-heavy: merge A then C then D then B (to ensure harness exists before tests)
