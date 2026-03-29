# 23_CODE_STYLE

## Document Status

- Status: Canonical
- Audience: Engineers, Reviewers, Tooling
- Scope: Naming, structure, readability, and implementation style guidelines

---

## Purpose

This document defines the preferred code style for Live Scene Composer and its related boundaries. It exists to promote consistency, clarity, and maintainability across the codebase.

Code style is not cosmetic. Good style reduces ambiguity, improves review quality, and makes architecture easier to preserve.

---

## Core Style Principles

The codebase should optimize for:

- clarity over cleverness
- explicitness over implication
- strong naming over vague utility sprawl
- typed contracts over loose payloads
- compositional readability over giant files
- stable architecture over local shortcuts

The question is not “can this compile?”
The question is “can this be understood and safely evolved?”

---

## Naming Principles

### Prefer domain names over UI accident names

Good names reflect the model:

- `SceneDocument`
- `LayoutNode`
- `SlotDefinition`
- `WidgetInstance`
- `PrefabDefinition`
- `RuntimeMutation`

Avoid names that collapse meaning, such as:

- `Thing`
- `Item`
- `Stuff`
- `Data`
- `Helper`
- `Manager` unless it really manages something cohesive

### Prefer intent-rich names

Names should communicate responsibility.

Good examples:

- `registerTypographyModule`
- `validateSlotCompatibility`
- `applyWidgetStyleMutation`
- `resolveInspectorTarget`

Weak examples:

- `doUpdate`
- `handleThing`
- `mutateData`
- `miscUtils`

---

## File Naming

File names should reflect stable concepts or clearly bounded implementation units.

Prefer:

- concept-driven names
- boundary-aware names
- explicit seam names

Examples:

- `scene-model.ts`
- `slot-contracts.ts`
- `runtime-mutation-policy.ts`
- `live-scene-composer-provider.tsx`

Avoid:

- ambiguous catch-all files
- generic utility dumps
- duplicate names in multiple places with different meanings

---

## Function Style

Functions should be:

- small enough to reason about
- named by intent
- explicit about input and output
- easy to test in isolation when possible

A function should generally do one coherent thing.
If a function requires a page of comments to explain its flow, it probably needs decomposition.

---

## Type Style

### Favor explicit types at important boundaries

Important boundaries should use clearly named types and interfaces rather than anonymous sprawling object literals.

Examples:

- mutation contracts
- scene model contracts
- module manifests
- slot compatibility rules
- inspector target resolution

### Avoid “stringly typed” architecture

Do not rely on vague string conventions where typed unions, enums, or named contracts are more appropriate.

### Avoid broad `any`-style escapes

A type escape should be rare, temporary, and justified.
It should not be the default way to move faster.

---

## Component Style

UI components should follow these rules:

- one clear responsibility per component
- separate view concerns from domain transformation when possible
- avoid hiding domain truth in local UI state
- avoid giant all-knowing components
- keep mutation requests explicit

A component should not quietly become a scene model, mutation policy, and layout engine all at once.

---

## State Style

Keep state ownership explicit.

Prefer:

- scene/domain state in domain-oriented layers
- ephemeral UI state in interaction-oriented layers
- typed mutation flows for sensitive changes

Avoid:

- leaking domain truth into transient component-local state
- silently syncing multiple unofficial sources of truth
- mixing preview, baseline, and draft state without naming the distinction

---

## Import Style

Imports should follow architecture, not convenience.

Prefer:

- imports from canonical seams
- imports from public boundaries
- explicit adapter contracts where needed

Avoid:

- reaching into private sibling internals
- forbidden cross-boundary imports
- “just this once” imports from the wrong product
- resurrecting legacy path aliases

The import graph is an architecture signal, not an implementation detail.

---

## Module and Folder Style

A folder should represent a coherent unit of responsibility.
Do not create folders like:

- `misc`
- `temp`
- `shared2`
- `new-core`
- `stuff`

If a folder exists, its ownership should be explainable in one sentence.

---

## Utility Style

Utility files should be rare and narrow.

A good utility module has:

- one clear theme
- low conceptual weight
- no hidden authority
- obvious ownership

A bad utility file becomes a trash can for code with no home and no architecture accountability.

---

## Comment Style

Comments should explain:

- why something exists
- why a decision was made
- what invariant matters
- what assumption would be dangerous to break

Comments should not repeat trivial syntax.
The code should explain the “what”; comments should help explain the “why.”

---

## Error Message Style

Error messages should be:

- specific
- actionable when possible
- tied to the actual failure condition
- free of vague filler

Good examples:

- invalid widget insertion: slot `heroChart` does not accept widget capability `textual`
- mutation rejected: `widget.style.update` is not allowed in Safe Mode

Bad examples:

- invalid
- failed
- something went wrong

---

## Test Naming Style

Tests should describe behavior and boundary intent.

Prefer names like:

- rejects widget insertion into incompatible slot
- does not allow composer writes outside mutation bridge
- keeps runtime-debug registration free of composer modules

Avoid vague names like:

- works
- test stuff
- should be okay

---

## Refactor Style

Refactors should preserve behavior unless behavior change is explicitly part of the task.
A refactor PR should not silently alter mutation semantics, dependency direction, or ownership.

If behavior changes, say so clearly.

---

## Anti-Patterns

The code style must reject:

- giant god files
- vague helpers
- unnamed payload blobs
- boundary-breaking imports
- domain concepts hidden behind generic UI naming
- overloaded “manager” or “service” types that own too much
- casual duplication of canonical concepts

---

## Summary

The code style for Live Scene Composer should make architecture visible in code. Strong names, explicit types, clean boundaries, and readable responsibilities matter far more than clever compactness. Good style is one of the cheapest ways to keep the system maintainable as it grows.
