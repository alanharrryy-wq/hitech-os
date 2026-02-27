# 20_SCOPE_RULES — How to Slice Any Project into 4 Parallel Scopes

STATUS: LAW

## Built‑in Improvements (10)

1. Scope slicing patterns for 5 project archetypes
2. Anti-overlap rules (“single source of truth”)
3. “Interfaces first” slicing to reduce merge conflicts
4. Checklist to validate a slice is well-formed
5. A “scope boundary contract” template
6. A risk meter (high-impact surfaces)
7. Deterministic default guidance per archetype
8. Upgrade path when scope was sliced wrong
9. A “do not touch list” mechanism
10. Example scope maps you can copy/paste

---

## TL;DR

Slicing is the secret sauce. If you slice wrong, Z becomes a therapist. Slice right, Z becomes a machine.

---

## The Universal Slice Rule

A slice must be:

- **Owned** (one builder)
- **Bounded** (clear file/folder surface)
- **Interface-driven** (consumes/produces explicit contracts)
- **Testable** (has at least one deterministic validation signal)

---

## Archetype Patterns (Pick one)

### 1) Web App / Product UI

- A: domain + shared contracts
- B: UI surface + routing + interaction
- C: tooling + CI + guardrails + performance harness
- D: tests + docs + smoke e2e

### 2) API / Service Platform

- A: domain + API schema + core services
- B: client SDK / admin console / API explorer (or none)
- C: infra (containers, deploy scaffolding, tracing) + guardrails
- D: integration tests + contract tests + docs

### 3) Database-Heavy System

- A: schema design + migrations + constraints + invariants
- B: query layer / repository adapters / admin UI (if present)
- C: backup/restore tools + environment harness + performance checks
- D: migration tests + data integrity tests + runbooks

### 4) CRM / Workflow Engine

- A: entities + permissions + audit + business rules
- B: operator UI (pipelines, dashboards, forms)
- C: automation tooling + import/export + guardrails
- D: end-to-end workflow tests + docs + release checklist

### 5) Interactive Deck / Slides System

- A: state machine / evidence / replay / contracts
- B: slide surfaces / UI modules / test IDs
- C: build/test determinism + guard scripts + runner tooling
- D: e2e smoke + docs + operator runbooks

---

## Anti-Overlap Rules (Non-negotiable)

- Only one canonical implementation per subsystem.
- Wrappers are allowed for compatibility, but must be thin.
- If two slices touch the same subsystem, stop and re-slice.

---

## How to Write a Scope Brief (Use the template)

Use `templates/SCOPE_BRIEF_TEMPLATE.md`.

A good scope brief includes:

- Scope ID + owner
- Allowed folders
- Forbidden folders
- Contracts produced/consumed
- Validation signals
- “Do not touch” list

---

## Slice Quality Checklist

A slice is acceptable only if:

- It names the canonical files/folders it owns
- It lists the contracts it may change
- It specifies at least one validation command
- It identifies high-impact files it must avoid
- It states additive-only policy

---

## When Slicing Was Wrong (Fix without chaos)

Symptoms:

- repeated merge conflicts
- duplicated logic
- builders “fixing” each other’s work

Fix process:

1. Freeze changes (no new work)
2. Identify the disputed subsystem
3. Choose ONE canonical owner
4. Convert others to adapters/wrappers or revert overlaps
5. Update docs + scope briefs
