# 10_MUTATION_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Validation, Tooling
- Scope: Mutation semantics, governance, validation, and safe change flow

---

## Purpose

This document defines the mutation model for Live Scene Composer. It exists because mutations are where authoring intent becomes runtime-facing effect, and that transition is the most sensitive part of the system.

If mutation semantics are vague, safety becomes imaginary.
If mutation flows are hidden, debugging becomes expensive.
If mutation boundaries are bypassed, the product loses trust.

---

## Mutation Model Summary

A mutation is a typed request to change composition state.
The mutation model exists to make changes:

- explicit
- validated
- scoped
- attributable
- testable
- reversible when appropriate
- governable by mode and policy

All write-capable mutations affecting runtime-facing state must pass through **runtime-mutation-bridge**.

---

## Why a Mutation Model Exists

The composer is not allowed to rely on informal side effects or UI-driven direct writes. A mutation model exists to provide:

- contract clarity
- architecture safety
- operational visibility
- mode-aware governance
- consistent preview / commit semantics
- structured error handling
- future extension without chaos

---

## Mutation Lifecycle

The intended lifecycle of a mutation is:

1. authoring action occurs
2. mutation intent is created
3. source and target are identified
4. mutation type is resolved
5. mode policy is checked
6. validation runs
7. mutation is either rejected or accepted
8. accepted mutations update draft / preview / accepted state as appropriate
9. inverse or revert semantics are recorded where applicable
10. downstream runtime-facing effect occurs only through the governed path

This sequence should be legible in code and in test expectations.

---

## Mutation Categories

### 1. Scene-level mutations

Examples:

- scene metadata updates
- scene-level theme changes
- scene-level baseline/draft transitions

### 2. Layout mutations

Examples:

- move layout node
- resize layout node
- reorder layout node
- adjust layout constraints

### 3. Slot mutations

Examples:

- create slot
- change slot properties
- adjust slot acceptance policy
- move slot association in layout contexts

### 4. Widget mutations

Examples:

- insert widget
- remove widget
- move widget between valid slots
- update widget props
- update widget style
- toggle widget visibility or lock state

### 5. Draft workflow mutations

Examples:

- discard draft
- commit draft
- reset selected element
- reset current module contribution

---

## Mutation Scope

Every mutation should carry an explicit scope.

### Possible scopes

- preview-only
- commit-capable
- accepted-state transition
- local reset
- full draft discard

The exact names may evolve, but the idea must remain explicit.

### Why scope matters

Without scope clarity, the system cannot reliably distinguish:

- temporary visual feedback
- accepted authoring decisions
- reset behavior
- persistence intent

---

## Mutation Source

Every mutation should identify its source.

Examples:

- live-scene-composer
- specific composer module
- future bounded custom widget API wrapper

This matters for:

- policy
- validation
- auditing
- debugging
- safe permissioning

---

## Mutation Target

Every mutation should identify its target.

Possible targets include:

- scene
- layout node
- slot
- widget
- draft state
- module-specific contribution

A mutation without a clear target is a design smell.

---

## Validation Model

A mutation should not be applied just because it was requested.

Validation may include:

- source validation
- target existence validation
- policy allowlist checks
- mode checks
- slot/widget compatibility checks
- structural validity checks
- preview vs commit rules
- reversibility expectations
- future capability checks for custom widget requests

Validation is one of the reasons runtime-mutation-bridge exists.

---

## runtime-mutation-bridge Role

runtime-mutation-bridge is the enforcement layer for write-capable mutation flow.

It should be responsible for:

- receiving typed mutation requests
- checking source and target validity
- enforcing allowed mutation types
- deciding whether the action is legal in Safe Mode or Advanced Mode
- routing approved changes to appropriate adapters or downstream state transitions
- rejecting invalid or unsafe changes clearly

The bridge is not optional infrastructure.
It is the safety boundary.

---

## Safe Mode Mutation Policy

Safe Mode should allow only bounded and strongly understandable mutations.

Typical Safe Mode candidates:

- text changes
- typography updates
- background and color changes
- approved layout adjustments
- widget insertion from valid prefabs
- widget property changes within contract limits
- style changes that remain within governed boundaries
- draft reset / discard / commit actions

Safe Mode should not become a polite label for unrestricted write power.

---

## Advanced Mode Mutation Policy

Advanced Mode may eventually enable more powerful changes, but this mode must still remain explicit and governed.

Advanced Mode should not mean:

- direct runtime access
- policy bypass
- untyped changes
- undocumented mutation flows

Advanced Mode is an expansion of explicit authority, not the absence of authority.

---

## Reversibility

Mutations should explicitly state or imply whether they are reversible.

Reversibility matters for:

- undo / redo
- local reset
- module rollback
- user trust
- validation rigor

Not all future mutations must be perfectly reversible, but the system should know which are and which are not.

---

## Error Semantics

Rejected or failed mutations should fail clearly.

Expected behaviors:

- reject with meaningful reason
- preserve baseline and broader draft integrity
- avoid silent partial corruption
- avoid hidden fallback writes
- surface actionable information for debugging and validation

A failed mutation should never quietly mutate unrelated state.

---

## Mutation Record Shape

The exact type shape may evolve, but a healthy mutation contract should include concepts like:

- mutation id
- source
- type
- mode
- scope
- target
- payload
- timestamp
- reversibility metadata

These concepts help the bridge and validation system reason about change.

---

## Mutation Anti-Patterns

The following are unacceptable:

- direct UI control mutating runtime internals
- untyped “update anything” payloads as the default strategy
- hidden side effects that write outside the declared target
- preview actions silently becoming accepted state
- allowing custom widget code to bypass mutation governance
- using route-level hacks instead of mutation contracts
- treating mode as a UI label rather than a policy input

---

## Minimum MVP Mutation Direction

The MVP should start small and disciplined.

A sensible initial mutation surface would likely include:

- update scene look or visual context
- move / resize / reorder layout node
- insert widget from prefab into valid slot
- update widget props
- update widget style
- remove widget
- discard draft
- commit draft
- reset selected element

This is sufficient to make the product useful without creating a giant mutation universe on day one.

---

## Summary

The mutation model is the governance center of Live Scene Composer. Every meaningful write-capable change should be typed, scoped, validated, and routed through runtime-mutation-bridge. Mutation semantics must remain explicit so that preview, commit, revert, safety modes, and future extensibility all remain coherent and trustworthy.
