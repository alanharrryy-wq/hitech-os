# 18_RUNTIME_MUTATION_BRIDGE

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Validation, Tooling
- Scope: Mutation governance boundary, validation role, and bridge responsibilities

---

## Purpose

This document defines the role of `runtime-mutation-bridge` in Live Scene Composer. It exists because the bridge is the central safety boundary between authoring intent and runtime-facing write effect.

The bridge is not an optional abstraction. It is the mechanism that makes the Composer governable.

---

## Bridge Summary

`runtime-mutation-bridge` is the controlled write boundary for the Composer.

It should be responsible for:

- receiving typed mutation requests
- validating source, target, and mutation type
- enforcing mode policy
- distinguishing preview from accepted commit paths
- routing approved effects through explicit adapters
- rejecting unsafe or invalid changes clearly

The bridge prevents the Composer from mutating runtime-facing state directly and informally.

---

## Why the Bridge Exists

The bridge exists to solve several problems:

1. direct UI-to-runtime writes are too fragile
2. safety mode policy must be enforceable somewhere explicit
3. mutation validation must be centralized enough to stay real
4. reversibility expectations need a visible boundary
5. future custom and modular extension must not become write bypasses
6. diagnostics and authoring must not share the same mutation habits

Without the bridge, mutation safety becomes a social preference instead of an architectural fact.

---

## Core Bridge Principle

All write-capable Composer mutations that affect runtime-facing state must pass through `runtime-mutation-bridge`.

This principle must remain true in naming, import paths, implementation, tests, and review decisions.

---

## Bridge Responsibilities

The bridge should own:

- typed mutation intake
- source validation
- target validation
- allowlist checks
- safe mode / advanced mode gating
- preview vs commit semantics
- routing to runtime-facing adapters
- structured rejection and error reporting
- optional inverse/revert metadata handling

The bridge should not own:

- the full authoring UI
- the whole scene model
- debug tooling
- every detail of rendering
- all business logic everywhere

It is a governance boundary, not a giant application layer.

---

## Mutation Intake

The bridge should receive typed mutations with explicit metadata such as:

- source
- type
- target
- mode
- scope
- payload
- reversibility expectations

The bridge should not accept vague “update anything” requests as the default pattern.

---

## Source Validation

The bridge should validate who is asking for the change.

Possible approved sources may include:

- live-scene-composer shell
- approved composer modules
- future bounded custom widget request wrappers

This matters because not every caller should have equal authority.

---

## Target Validation

The bridge should validate what the mutation targets.

Potential targets may include:

- scene
- layout node
- slot
- widget
- draft-level operations

The bridge must reject or flag ambiguous targets.
A write without a clear target is an architecture risk.

---

## Mode Policy

The bridge is the place where operational mode becomes enforceable policy.

### Safe Mode

Allows only approved, understandable, bounded changes.

### Advanced Mode

May eventually allow broader operations, but still under typed, explicit, validated rules.

Mode must not remain a cosmetic label in the UI.
It should influence bridge behavior.

---

## Preview vs Commit

The bridge should understand whether a mutation is:

- preview-only
- commit-capable
- draft-reset or discard-related
- accepted-state transition related

This is essential for:

- trust
- compare/revert behavior
- testing
- preventing “everything visible becomes accepted automatically” bugs

---

## Adapter Routing

The bridge should route approved changes toward downstream runtime-facing effects through explicit adapters or equivalent seams.

This matters because:

- runtime specifics should remain bounded
- bridge policy should not depend on every runtime detail
- integration becomes easier to test and evolve

The bridge is therefore both a policy boundary and a routing boundary.

---

## Rejection Behavior

The bridge must reject clearly when a mutation is not allowed.

Rejection behavior should aim for:

- explicit reason
- no hidden fallback path
- no unrelated state corruption
- preserved draft/baseline integrity where possible
- useful diagnostics for validation and tooling

A rejected mutation that still partially writes is worse than an obvious failure.

---

## Early Bridge Command Direction

The early bridge should remain intentionally small.

A reasonable early typed command surface may include:

- scene look update
- layout move
- layout resize
- layout reorder
- widget insert
- widget remove
- widget props update
- widget style update
- draft discard
- draft commit
- selected element reset

This is enough to support a useful early Composer without building an enormous mutation universe too early.

---

## Bridge and Modules

Modules should not bypass the bridge.
Instead, modules should access mutation ability through approved, typed helper seams that eventually route through the bridge.

This keeps modular growth compatible with mutation governance.

---

## Bridge and Custom Widgets

Custom widgets must not receive raw bridge access.
At most, they should be allowed to request bounded actions through safe wrappers that remain subject to bridge validation.

This prevents custom widgets from becoming a hidden authority tier.

---

## Bridge Anti-Patterns

The bridge model must reject:

- direct UI writes that skip the bridge
- giant untyped mutation payloads
- hidden privileged callers
- preview actions that silently become accepted commits
- route-level runtime mutation hacks
- bridge implementations that are policy-free pass-through shells

A bridge that does not enforce policy is only pretending to exist.

---

## Validation Expectations

The bridge should be validated through:

- command contract tests
- source/target validation tests
- mode policy tests
- rejection-path tests
- adapter routing tests
- no-bypass architecture guard assertions where feasible

The bridge must be observable enough that teams can prove it is still doing its job.

---

## Summary

`runtime-mutation-bridge` is the central safety boundary between Live Scene Composer and runtime-facing write effects. It validates, gates, scopes, and routes mutations so the Composer can be powerful without becoming reckless. It is one of the most important pieces of the system and must remain a real enforcement boundary, not a symbolic directory name.
