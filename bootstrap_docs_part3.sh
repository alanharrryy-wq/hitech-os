#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="${1:-docs}"
mkdir -p "$DOCS_DIR"

cat > "$DOCS_DIR/21_DEVELOPER_GUIDE.md" <<'EOF'
# 21_DEVELOPER_GUIDE

## Document Status

- Status: Canonical
- Audience: Engineers, Tooling, Validation, New Contributors
- Scope: Local development workflow, environment setup, and day-to-day development expectations

---

## Purpose

This document explains how engineers should work on Live Scene Composer and its related boundaries without creating avoidable instability, architecture drift, or setup confusion.

It is not only about how to run the code.
It is about how to work in a way that preserves the integrity of the project.

---

## Development Principles

Development on this project should optimize for:

- clarity over speed hacks
- explicit boundaries over informal shortcuts
- typed contracts over folklore
- repeatable local setup over custom machine voodoo
- safe incremental progress over giant rewrites
- architecture preservation over “temporary” convenience

The Composer is not a throwaway experiment. Its development workflow should reflect that.

---

## Expected Repo Context

The developer is working in a repository that contains at least these major concerns:

- shared infrastructure through `console-core`
- `runtime-debug-console`
- `live-scene-composer`
- `runtime-mutation-bridge`
- runtime-facing systems
- scene-related systems
- tests, docs, and architecture guardrails

Before changing anything, a developer should know which boundary they are in.

---

## Before You Start Working

Before writing code, confirm the following:

1. you understand whether the task belongs to:
   - `console-core`
   - `runtime-debug-console`
   - `live-scene-composer`
   - `runtime-mutation-bridge`

2. you have read the relevant docs for the area you are touching

3. you know whether the task affects:
   - scene model
   - layout
   - slots
   - widgets
   - prefabs
   - bridge contracts
   - module SDK
   - dependency policy

4. you know whether the task touches protected nodes

If those answers are fuzzy, stop and clarify before coding.

---

## Recommended Local Setup

A healthy local setup should include:

- the repo checked out cleanly
- the correct package manager installed
- the correct runtime version(s) installed
- the ability to run:
  - typecheck
  - targeted tests
  - architecture guard
  - local app/runtime preview flow where relevant

The exact commands may evolve with the repo, but setup should always support verification, not just coding.

---

## Working Directory Discipline

Do not treat the repo as a flat filesystem.

A developer should know:

- where shared infra lives
- where product-specific code lives
- where mutation governance lives
- where runtime-facing integrations live
- where docs and evidence artifacts are stored

Do not create new “temporary shared” folders because a boundary feels inconvenient.

---

## Read Before Write Rule

Before touching a subsystem, read at minimum:

- the most relevant architecture doc
- the domain or contract doc for that subsystem
- the dependency policy if the change affects imports or ownership
- the protected nodes doc if you are touching high-impact seams

This rule prevents a huge amount of avoidable damage.

---

## Daily Development Workflow

A healthy day-to-day workflow should look like this:

1. identify task boundary
2. identify affected contracts and docs
3. confirm no forbidden dependency is being introduced
4. implement the smallest safe change
5. run targeted verification
6. update docs if the meaning of the system changed
7. review for boundary drift before calling the change done

---

## Composer Development Expectations

When working inside `live-scene-composer`, prefer:

- scene-first reasoning
- typed mutation requests
- slot- and widget-aware behavior
- module-based contribution
- explicit provider and adapter seams
- local failure containment
- draft/preview semantics that remain legible

Do not:

- wire authoring through debug paths
- mutate runtime directly
- hide domain truth in ephemeral component state
- build giant, private “helper” modules that bypass the system shape

---

## Bridge Development Expectations

When working inside `runtime-mutation-bridge`, prefer:

- small typed commands
- source and target validation
- mode-aware enforcement
- adapter seams
- explicit rejection paths
- focused tests

Do not:

- turn the bridge into a broad product logic dumping ground
- allow raw “update anything” payloads as default behavior
- add convenience bypasses for one module or one screen

---

## console-core Development Expectations

When working inside `console-core`, prefer:

- true shared primitives
- minimal product knowledge
- reusable shell and registry abstractions
- clear contracts

Do not:

- sneak authoring logic into shared infrastructure
- sneak debug-only behavior into shared infrastructure
- promote convenience duplication into permanent shared ownership

---

## Runtime Debug Development Expectations

When working inside `runtime-debug-console`, remember:

- it is diagnostics-oriented
- it is not the Composer
- it should not become an editor host
- it may inspect runtime state more deeply, but that does not change Composer rules

Do not use Runtime Debug Console as a staging ground for authoring hacks.

---

## Code Change Size Guidance

Prefer small, reviewable, evidence-backed changes.

Good change shape:

- one boundary
- one seam
- one clear behavioral change
- one testable result

Bad change shape:

- touches five boundaries
- changes contracts casually
- adds helpers in random places
- includes unreviewed architectural widening
- claims “just cleanup” while changing semantics

---

## Local Verification Expectations

Before considering a change done, run the strongest relevant subset of:

- typecheck
- targeted unit or integration tests
- architecture guard
- dependency or path checks
- registration seam tests
- bridge rejection-path tests if mutation behavior changed

Local confidence must not rely only on “it seems fine.”

---

## Documentation Expectations

Update docs when the system meaning changes.

Examples that should trigger doc review:

- contract changes
- mutation model changes
- dependency policy changes
- provider seam changes
- module SDK changes
- new protected nodes
- new top-level workflow assumptions

Not every code change needs doc updates, but any semantic architecture change probably does.

---

## Common Development Mistakes to Avoid

- coding before locating the correct boundary
- importing from the wrong sibling product
- hiding scene truth inside local component state
- bypassing typed mutation flows
- creating duplicate concepts because the canonical one is inconvenient
- using “temporary” path aliases that confuse architecture
- skipping validation because a feature appears visually correct

---

## Pull Request Readiness Checklist

Before opening or finalizing a PR, confirm:

1. the change belongs to the boundary it was implemented in
2. no forbidden dependency was introduced
3. affected docs are still correct
4. relevant tests pass
5. architecture guard still passes if applicable
6. protected-node changes were treated with extra care
7. the change can be explained clearly in terms of system intent

---

## Summary

The developer workflow for Live Scene Composer should preserve boundaries, enforce disciplined change, and keep architecture visible during day-to-day work. Engineers should know where they are working, what seams they are touching, what rules apply, and what verification is required before the change is considered safe.
EOF

cat > "$DOCS_DIR/22_CONTRIBUTING.md" <<'EOF'
# 22_CONTRIBUTING

## Document Status

- Status: Canonical
- Audience: Engineers, Tooling, Validation, Reviewers
- Scope: Contribution rules, expectations, and review discipline

---

## Purpose

This document defines how contributions should be made to Live Scene Composer and related boundaries. It exists to ensure that contributors do not accidentally weaken the architecture, introduce hidden coupling, or create code that cannot be safely evolved.

Contributing is not only about adding code.
It is about preserving the integrity of the system while extending it.

---

## Contribution Philosophy

All contributions should optimize for:

- explicitness
- correctness
- bounded ownership
- reviewability
- testability
- architecture preservation
- maintainability over cleverness

A contribution that ships a feature but weakens core boundaries is not a successful contribution.

---

## Who This Applies To

This document applies to:

- feature contributors
- core architecture contributors
- tooling contributors
- validation contributors
- reviewers
- automation-assisted contribution flows

Everyone who changes the codebase inherits the obligation to respect its architecture.

---

## What Counts as a Contribution

A contribution may include:

- code
- tests
- architecture guard updates
- dependency policy updates
- documentation
- refactors
- validation additions
- scaffolding or tooling improvements

The same discipline applies whether the change is a feature or “just cleanup.”

---

## Contribution Rules

### Rule 1: Know the boundary you are changing

Every change must have an identifiable boundary owner:

- `console-core`
- `runtime-debug-console`
- `live-scene-composer`
- `runtime-mutation-bridge`
- runtime adapter area
- scene-related integration area

If the contribution crosses multiple boundaries, that should be explicit and justified.

### Rule 2: Do not smuggle architecture changes

A PR labeled as refactor, cleanup, or convenience should not silently introduce:

- new dependency directions
- new product coupling
- mutation bypasses
- hidden ownership shifts

### Rule 3: Respect canonical concepts

Do not invent parallel concepts when the system already has canonical ones such as:

- Scene
- Layout
- Slot
- Widget
- Prefab
- Mutation
- Bridge
- Module manifest

If the canonical concept is insufficient, improve it deliberately instead of duplicating it.

### Rule 4: Update docs when meaning changes

Architecture and domain meaning changes require doc updates or explicit rationale for why docs remain valid.

### Rule 5: Add evidence for risky changes

The higher the risk, the stronger the evidence required.

---

## Contribution Categories

### Low-risk contributions

Examples:

- typo fixes
- local UI polish without semantic changes
- internal cleanup within a bounded private area
- comment improvements

Expected process:
Normal review and normal verification.

### Medium-risk contributions

Examples:

- new module contributions
- inspector behavior additions
- new prefab categories
- structure tooling improvements
- widget-type enhancements

Expected process:
Clear explanation, targeted tests, and architecture awareness.

### High-risk contributions

Examples:

- mutation contract changes
- scene/layout/slot/widget contract changes
- provider seam changes
- adapter seam changes
- dependency policy changes
- shared-core changes
- bridge validation behavior changes

Expected process:
Explicit rationale, focused review, stronger verification, and likely doc updates.

---

## Branch and Change Hygiene

A contribution should be:

- scoped
- coherent
- readable
- minimally noisy
- explainable in one narrative

Avoid PRs that mix:

- feature work
- architecture rewrites
- unrelated cleanup
- random formatting churn

That kind of bundle makes review weaker and regression more likely.

---

## Commit Message Guidance

Commits should explain intent, not only activity.

Prefer messages that communicate:

- what changed
- why it changed
- what boundary or concept it affects

Examples of good intent framing:

- preserve composer/debug boundary in registry wiring
- add typed widget style mutation through bridge
- harden slot compatibility validation
- isolate chart appearance module registration

Avoid vague messages like:

- stuff
- fixes
- cleanup
- updates
- wip

---

## Pull Request Expectations

A healthy PR should include:

- problem statement
- boundary affected
- summary of change
- risk level
- validation run
- docs updated or rationale for not updating
- any remaining risks or follow-up items

The reviewer should not have to guess what the contribution is doing to the system.

---

## Required PR Questions

Every meaningful PR should answer:

1. What problem does this solve?
2. Which boundary owns the solution?
3. What contracts or protected nodes are affected?
4. Does this change dependency direction?
5. Does this alter mutation behavior?
6. What tests or guards prove safety?
7. Do docs remain correct?

These questions are not bureaucracy; they are architecture protection.

---

## Reviewer Expectations

Reviewers should not limit review to “does the code run?”

Reviewers should ask:

- is this in the right place
- is the dependency direction allowed
- does it preserve sibling product separation
- does it widen authority unsafely
- does it weaken the bridge
- does it duplicate an existing concept
- is the blast radius understood

A reviewer is a boundary defender, not just a syntax checker.

---

## Protected Node Contributions

Changes touching protected nodes require stronger discipline.

Examples:

- scene model contracts
- mutation bridge contracts
- dependency policy
- module SDK
- console-core registry foundations
- provider seams
- adapter seams

These changes should include:

- explicit rationale
- stronger validation
- targeted tests
- doc review
- careful impact explanation

---

## Testing Expectations for Contributions

A contributor should run the strongest relevant verification subset for the change.
Possible examples include:

- typecheck
- architecture guard
- targeted tests
- mutation rejection-path tests
- registration seam tests
- dependency or path assertions

The contribution should not depend on the reviewer to discover all missing validation.

---

## Forbidden Contribution Patterns

The following are unacceptable contribution patterns:

- adding a feature by bypassing mutation governance
- importing across sibling boundaries because it is convenient
- hiding architecture changes inside unrelated cleanup
- introducing new shared folders without ownership clarity
- shipping “temporary” hacks that create long-term coupling
- editing protected seams with no explanation or validation

---

## Summary

Contributing to Live Scene Composer requires more than making code compile. Contributors must respect boundaries, preserve canonical concepts, explain changes clearly, validate risky work, and avoid smuggling architectural damage inside convenience changes. Strong contribution discipline is how the project stays healthy as it grows.
EOF

cat > "$DOCS_DIR/23_CODE_STYLE.md" <<'EOF'
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
EOF

cat > "$DOCS_DIR/24_TESTING_STRATEGY.md" <<'EOF'
# 24_TESTING_STRATEGY

## Document Status

- Status: Canonical
- Audience: Engineering, Validation, Tooling, Reviewers
- Scope: Testing philosophy, layers, priorities, and boundary-oriented verification

---

## Purpose

This document defines the testing strategy for Live Scene Composer and its related architecture. It exists because this project cannot rely on visual confidence alone. The system includes protected contracts, mutation governance, sibling product boundaries, and integration seams that require targeted evidence.

The goal is not “more tests.”
The goal is the right tests at the right layers.

---

## Testing Principles

The testing strategy should optimize for:

- boundary protection
- contract confidence
- mutation governance
- local failure detection
- regression resistance
- confidence in architectural rules
- focused evidence rather than noisy test volume

A thousand shallow tests are less useful than a smaller set of tests that defend the real seams.

---

## What the Test Suite Must Protect

The test strategy must protect at minimum:

- sibling separation between Runtime Debug Console and Live Scene Composer
- canonical domain contracts
- mutation bridge enforcement
- slot/widget compatibility rules
- module registration discipline
- dependency policy assumptions
- preview/commit/revert semantics at the level the product supports
- failure isolation for bounded modules and widgets where implemented

---

## Test Layers

### 1. Contract tests

These validate important typed contracts and domain rules.

Examples:

- scene/layout/slot/widget contract expectations
- prefab compatibility rules
- module manifest validation
- mutation command shape validation

Contract tests matter because many future capabilities depend on these definitions staying coherent.

---

### 2. Boundary tests

These validate architecture boundaries and wiring expectations.

Examples:

- runtime-debug does not register composer modules
- composer does not write directly to runtime paths
- no legacy shared-core path drift
- no forbidden sibling imports where checkable

Boundary tests are among the highest leverage tests in this project.

---

### 3. Mutation behavior tests

These validate the mutation model and bridge.

Examples:

- rejects invalid target
- rejects forbidden Safe Mode command
- accepts allowed widget style mutation
- rejects bypass path
- preserves explicit preview vs commit behavior

These tests matter because mutation is the safety center of the system.

---

### 4. Module registration tests

These validate module lifecycle and contribution discipline.

Examples:

- module registers valid inspector contribution
- invalid manifest is rejected
- disabled module does not contribute surfaces
- broken module contribution does not collapse the shell

---

### 5. Integration tests

These validate meaningful end-to-end slices within bounded scope.

Examples:

- selecting a widget exposes the expected inspector contribution
- inserting a prefab into a compatible slot produces expected structure
- valid mutation request updates draft and preview
- invalid insertion is blocked and reported

Integration tests should prove coherent slices, not replace every lower-level test.

---

### 6. Smoke tests

These validate top-level health.

Examples:

- core architecture-related tests pass
- key shells mount
- critical routes or providers initialize
- architecture guard still passes

Smoke tests do not prove depth, but they help catch catastrophic breakage early.

---

## Risk-Based Testing Priority

Higher risk areas deserve stronger testing density.

### Highest priority

- mutation bridge
- scene/layout/slot/widget contracts
- dependency policy enforcement
- provider seams
- registration seams
- runtime/composer separation

### Medium priority

- inspector contributions
- widget-specific editing behavior
- prefab filtering and insertion
- structure tree interactions

### Lower but still meaningful priority

- minor UI polish
- purely cosmetic rendering details
- static documentation-only surfaces

The point is not to ignore low-risk areas, but to assign energy intelligently.

---

## What Not to Over-Rely On

Do not over-rely on:

- visual manual testing alone
- giant broad integration tests that are hard to maintain
- snapshot tests as the main correctness mechanism
- local “seems okay” runtime impressions
- tests that only assert implementation details with no product or architecture meaning

This system needs evidence aligned with its actual risks.

---

## Mutation Bridge Testing Expectations

The bridge deserves special attention.

At minimum, the bridge should have tests for:

- accepted command flow
- rejected command flow
- source validation
- target validation
- mode gating
- preview vs commit handling
- no-bypass assumptions where feasible

If the bridge is under-tested, the whole product safety story weakens.

---

## Dependency and Path Guard Testing

The project should verify critical path and dependency rules such as:

- no legacy core path reintroduction
- no composer registration inside runtime-debug
- no canonical shared boundary drift
- no forbidden path aliases

These checks may be split between tests and architecture guard tooling.

---

## Failure Isolation Testing

As modularity grows, the test strategy should increasingly validate local containment.

Examples:

- one broken module does not break unrelated inspector surfaces
- widget-type-specific failure does not collapse selection model
- future sandboxed custom widget failures stay local

The Composer should be tested not only for happy paths but for survivability.

---

## Test Writing Guidelines

A good test should:

- describe behavior clearly
- target a meaningful seam
- fail for the right reason
- remain stable as implementation refactors
- communicate intent in plain language

A bad test:

- is coupled to internals that should be private
- asserts incidental implementation details
- is so broad that failures are hard to interpret
- duplicates other tests without adding confidence

---

## Minimum Verification for Risky Changes

For higher-risk changes, the contributor should usually run:

- typecheck
- architecture guard
- relevant unit or integration tests
- targeted new tests for the seam being changed

Risky changes without evidence should not be normalized.

---

## Summary

The testing strategy for Live Scene Composer should defend the architecture, mutation safety, and domain integrity of the system. Boundary tests, contract tests, bridge tests, and focused integration tests matter far more than raw test count. The goal is to prove that the important seams still hold, not merely that the UI still renders.
EOF

cat > "$DOCS_DIR/25_DEBUGGING_GUIDE.md" <<'EOF'
# 25_DEBUGGING_GUIDE

## Document Status

- Status: Canonical
- Audience: Engineers, Validation, Tooling, Operators
- Scope: Debugging approach for Composer-related issues without collapsing architecture boundaries

---

## Purpose

This document explains how to debug Live Scene Composer and related boundaries safely and effectively. It exists because debugging can either reveal architecture truth or destroy it, depending on how people approach the system.

The right goal is not only to find the bug.
It is to find the bug without breaking the architecture in the process.

---

## Debugging Principles

Debugging should prioritize:

- evidence over guesswork
- boundary-aware reasoning
- explicit reproduction steps
- smallest plausible failing seam
- safe observability over invasive hacks
- preserving the distinction between debug tooling and authoring tooling

Do not turn Runtime Debug Console into a fix-by-inspection path for Composer architecture problems.

---

## First Question: What Kind of Bug Is This

Before debugging deeply, classify the issue.

Possible categories:

- boundary bug
- mutation bug
- scene model bug
- layout bug
- slot compatibility bug
- widget rendering bug
- module registration bug
- preview/commit state bug
- runtime adapter bug
- performance bug
- sandbox/custom widget bug in future phases

Classification matters because the debugging path should match the kind of failure.

---

## Reproduction Discipline

Always begin with a reproducible description.

A useful bug report should capture:

- what was expected
- what actually happened
- what selection/scene/widget context was active
- what mode the system was in
- whether the failure occurs in preview, commit, or both
- whether the bug is deterministic
- which boundary appears involved

Without reproduction discipline, debugging turns into superstition.

---

## Debugging by Boundary

### If it looks like a composer shell issue

Check:

- provider initialization
- module registration
- selection lifecycle
- inspector contribution resolution
- shell-level failure boundaries

### If it looks like a scene model issue

Check:

- scene/layout/slot/widget relationships
- domain invariants
- draft vs baseline state
- mutation target resolution
- structure tree interpretation

### If it looks like a mutation issue

Check:

- command type
- source
- target
- mode
- bridge validation
- rejection handling
- preview vs commit path

### If it looks like a runtime integration issue

Check:

- adapter seams
- runtime-observed mapping
- view synchronization
- whether the bug is read-path or write-path related

### If it looks like a debug/composer coupling issue

Check:

- imports
- registration paths
- route binding
- hidden shared helpers
- boundary drift introduced by recent changes

---

## Safe Debugging Tools

Preferred debugging tools include:

- targeted logs with clear boundary context
- focused tests
- architecture guard
- structure inspection in controlled authoring surfaces
- typed mutation traces where available
- validation error outputs
- local runtime observation through approved seams

Use tools that preserve or reveal structure, not tools that bypass it.

---

## What Not to Do While Debugging

Do not:

- add direct runtime writes just to see if something works
- temporarily wire Composer logic into Runtime Debug Console
- mutate production contracts casually
- add giant permanent logging noise for one bug
- use hidden mutable globals to “see state”
- fix a bridge bug by bypassing the bridge

These are classic debugging mistakes that create worse problems than the original bug.

---

## Debugging Mutation Failures

When a mutation seems wrong, inspect in this order:

1. was the correct target selected
2. was the correct mutation type generated
3. was the mode what you think it was
4. did bridge validation allow or reject it
5. was the failure a rejection or a silent no-op
6. did the draft state update correctly
7. did preview reflect draft correctly
8. did commit semantics diverge from preview semantics

Mutation bugs often appear visual, but the root cause is usually somewhere in this chain.

---

## Debugging Preview vs Commit Issues

If the UI looks right in preview but wrong after commit, or vice versa, check:

- state category boundaries
- preview-only mutation behavior
- accepted-state transitions
- baseline update behavior
- revert/reset handling
- adapter routing differences

This class of bug often reveals unclear state semantics.

---

## Debugging Slot/Widget Problems

If insertion, replacement, or editing feels structurally wrong, inspect:

- slot identity
- slot acceptance policy
- widget type/capability
- slot capacity
- prefab compatibility filtering
- structure view representation
- mutation target resolution

Do not assume the issue is only visual.
Many slot/widget bugs are domain bugs first.

---

## Debugging Layout Problems

For move/resize/reorder issues, inspect:

- layout node identity
- parent/child structure
- snap and guide calculations
- interaction state vs domain state
- layout mutation generation
- preview synchronization

Layout debugging should not rely only on watching the DOM and guessing.

---

## Logging Guidance

Logs should be:

- scoped
- structured when possible
- easy to correlate with target and mutation
- removable after the issue is understood

A good log line often includes:

- boundary
- entity id
- mutation type
- mode
- result

A bad log strategy floods the console and still explains nothing.

---

## When to Add a Test

Add or update a test when:

- the bug touches a protected seam
- the bug represents a likely regression class
- the bug exposed a mistaken assumption about boundary or state
- the bug required non-obvious reasoning to diagnose

If the bug taught the team something real, it often deserves a test.

---

## Summary

Debugging Live Scene Composer should be evidence-driven, boundary-aware, and architecture-preserving. The goal is to isolate the failing seam, not to poke the runtime until the problem disappears. Good debugging strengthens the system by making failure modes clearer and more testable.
EOF

cat > "$DOCS_DIR/26_ERROR_HANDLING.md" <<'EOF'
# 26_ERROR_HANDLING

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Error handling philosophy, failure containment, and expected behaviors

---

## Purpose

This document defines how errors should be handled in Live Scene Composer and its related architecture. It exists because a live authoring product must fail in ways that preserve trust, state integrity, and shell stability.

The question is not whether errors will happen.
The question is whether the system remains understandable and survivable when they do.

---

## Error Handling Principles

The system should handle errors in a way that is:

- explicit
- local where possible
- non-corrupting
- diagnosable
- architecture-preserving
- respectful of draft/baseline integrity

A failed action should not turn into silent state corruption or hidden fallback writes.

---

## Error Categories

The system should reason about errors by category.

### Validation errors

Examples:

- invalid slot insertion
- forbidden mutation in Safe Mode
- missing widget props
- invalid target reference

These should typically be rejected clearly before application.

### Integration errors

Examples:

- runtime adapter mismatch
- stale render mapping
- provider seam failure
- missing registration contribution

These may require fallback behavior and stronger diagnostics.

### Execution errors

Examples:

- broken module contribution
- widget render crash
- future custom widget failure
- local inspector crash

These should be locally contained wherever possible.

### Systemic errors

Examples:

- unrecoverable shell initialization failure
- corrupted core configuration
- severe dependency or registration failure preventing the product from operating meaningfully

These are more serious and may require top-level fallback behavior.

---

## Error Handling Goals

Error handling should aim to:

1. prevent bad state from spreading
2. preserve shell stability
3. preserve baseline and draft integrity
4. expose enough context to debug effectively
5. make rejection and failure understandable to the user and the developer
6. avoid turning local issues into global crashes

---

## Validation Failure Behavior

Validation errors should generally:

- fail early
- fail explicitly
- avoid side effects
- provide actionable context when possible

Example classes:

- slot does not accept widget capability
- mutation target does not exist
- command not allowed in Safe Mode

These are healthy failures.
The system should not hide them.

---

## Mutation Rejection Behavior

When the bridge rejects a mutation, expected behavior includes:

- clear rejection reason
- no fallback direct write
- preserved draft integrity
- preserved baseline integrity
- observability for testing and debugging

A rejected mutation must not partially succeed through another path.

---

## UI-Level Error Handling

The Composer UI should favor containment and resilience.

Preferred behavior:

- local surface error boundaries
- fallback rendering for failed sections
- clear status or error indication where appropriate
- continued shell operation where possible

Examples:

- one inspector section fails but the rest of the inspector remains available
- one widget editor fails but the structure view remains usable
- one module contribution fails without crashing the whole workspace

---

## State Integrity Rules

Errors must not silently destroy state boundaries.

The following must remain true even when failure occurs:

- baseline stays trustworthy
- draft does not become half-applied garbage
- preview does not lie about accepted state
- selection remains understandable or resets clearly
- unrelated widgets or modules do not mutate as collateral damage

State integrity is one of the main reasons to formalize the model at all.

---

## Failure Containment

Containment is a first-class design requirement.

The system should aim for:

- widget-local containment
- module-local containment
- inspector-section containment
- adapter-seam containment
- sandbox-local containment for future custom widgets

The default mental model should be:
local failure should remain local unless there is a strong reason it cannot.

---

## User-Facing Error Behavior

Users do not need every low-level technical detail, but they do need outcomes that make sense.

Good user-facing behavior may include:

- action blocked because target is invalid
- change rejected because it is not allowed in current mode
- local component failed to render
- draft could not be committed

Bad user-facing behavior includes:

- silent nothing
- unrelated UI disappearing
- broken state with no explanation
- false indication that a change succeeded

---

## Developer-Facing Error Information

Developer-facing errors should include enough context to diagnose the problem.

Useful context may include:

- boundary name
- mutation type
- target id
- source module
- mode
- validation rule that failed
- adapter seam involved
- local lifecycle stage

The goal is to reduce debugging time and ambiguity.

---

## Logging Errors

Error logs should be:

- scoped
- structured where possible
- traceable to boundary and target
- limited to meaningful information
- not so noisy that real failures disappear

A noisy system that logs everything teaches engineers to ignore logs.

---

## Error Anti-Patterns

The system must reject:

- swallowing errors with no trace
- falling back to unsafe direct writes after rejection
- allowing partial mutation side effects
- global crashes from local module mistakes
- using error handling as an excuse to blur boundary responsibilities
- treating “caught” as equivalent to “handled”

Caught but corrupt is still failure.

---

## Testing Error Paths

Error behavior should be tested for meaningful seams, especially:

- mutation rejection
- invalid slot/widget operations
- registration failures
- module-local containment
- adapter failure handling
- future sandbox failure containment

Happy path testing alone is not enough for a product like this.

---

## Summary

Error handling in Live Scene Composer must protect trust, integrity, and containment. Validation failures should be explicit, mutation rejections should be side-effect free, local failures should remain local, and the shell should survive most non-systemic errors. Good error handling is one of the strongest signs that the architecture is healthy.
EOF

cat > "$DOCS_DIR/27_PERFORMANCE_MODEL.md" <<'EOF'
# 27_PERFORMANCE_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Performance goals, sources of cost, and performance-aware design rules

---

## Purpose

This document defines the performance model for Live Scene Composer. It exists because a live visual authoring product lives or dies on responsiveness. If the product feels sluggish, delayed, or unstable under normal editing, users stop trusting it quickly.

Performance should not be treated as “optimize later” decoration.
The basic performance model should shape architecture from the start.

---

## Performance Principles

The product should optimize for:

- responsive interaction
- fast selection feedback
- predictable preview updates
- bounded recomputation
- local rendering work where possible
- graceful degradation under load
- architecture-aware performance, not hacks

The goal is not perfect micro-optimization.
The goal is a responsive system whose performance characteristics remain understandable.

---

## Primary Performance Sensitivities

The most performance-sensitive areas are likely:

- selection changes
- canvas interaction
- drag / resize / reorder workflows
- inspector updates
- structure synchronization
- preview rendering
- runtime observation and mapping
- module contribution loading or reactivity
- future custom widget isolation surfaces

These areas should be designed with cost awareness.

---

## Performance Goals by Experience

### Selection should feel immediate

Selecting a widget or slot should quickly update:

- visual selection state
- handles and overlays
- structure highlighting
- inspector context

Users should not feel like selection is a batch job.

### Direct manipulation should feel live

Dragging, resizing, and reordering should feel smooth enough that the system reads as interactive, not transactional.

### Preview should remain credible

Preview updates should be timely and consistent enough that users believe the system is showing the real current draft state.

### Shell stability should remain intact

Performance issues in one module or one widget type should not freeze the entire Composer shell whenever possible.

---

## Major Sources of Performance Cost

### Scene model recomputation

Expensive scene model recalculation can make normal editing feel delayed.
Updates should prefer targeted recalculation over broad invalidation where possible.

### Inspector recalculation

If every selection change causes heavy recomputation across unrelated inspector modules, responsiveness will degrade quickly.

### Canvas overlay churn

Handles, guides, hover state, and bounds overlays can become expensive if they redraw too broadly or too often.

### Runtime mapping and measurement

Reading runtime-observed state can be costly if done excessively, synchronously, or without good scoping.

### Module-wide reactivity

If every module re-renders or recomputes for every small state change, modularity becomes expensive instead of helpful.

### Heavy widget rendering

Some widgets, especially charts and future custom widgets, may introduce significant rendering cost.

---

## Performance-Aware Architectural Rules

### Rule 1: Keep domain and interaction state scoped

Not every interaction change should invalidate the full scene or the full shell.

### Rule 2: Prefer targeted invalidation

Selection changes should update the necessary surfaces, not everything.

### Rule 3: Avoid all-knowing global render paths

A single giant render path that depends on all state is a performance trap.

### Rule 4: Treat expensive runtime reads carefully

Runtime measurement and mapping should be explicit and bounded.

### Rule 5: Keep module contributions local

Modules should respond to the context they need, not to broad product state they do not own.

---

## Selection Performance

Selection is one of the most frequent actions in the product.
It must remain cheap.

The system should aim to ensure that selection updates:

- do not trigger full scene recomputation
- do not cause unrelated module churn
- do not create broad layout recalculation unless required
- keep inspector target resolution reasonably bounded

If selection is slow, the whole product feels broken.

---

## Drag and Resize Performance

Drag and resize interactions should favor:

- low-latency local feedback
- bounded mutation or preview scheduling
- careful separation between interaction-phase updates and accepted-state transitions
- efficient overlay rendering

The system should avoid a model where every pixel movement becomes a giant global recalculation.

---

## Structure and Inspector Coordination

Structure and inspector synchronization matters for usability, but it should be implemented carefully.

A good approach favors:

- lightweight target resolution
- memoized or scoped contribution activation
- avoiding full tree rerender on small unrelated changes
- explicit boundaries between structure view state and domain state

---

## Module Performance Responsibility

Modules are not exempt from performance discipline.

A module should:

- subscribe narrowly
- compute only what it needs
- clean up properly
- avoid broad polling
- avoid expensive recomputation on every selection tick

A module that behaves like a global observer of everything will eventually make the product feel heavy.

---

## Chart and Rich Widget Performance

Charts and other visually complex widgets deserve special attention.

Possible concerns include:

- rerender cost
- layout thrash
- expensive data formatting
- heavy prop transformations
- unnecessary redraws during selection or hover

The authoring system should not treat all widgets as equally cheap.

---

## Future Custom Widget Performance

Custom widgets introduce additional performance risk.

The sandbox model should consider:

- isolation overhead
- messaging overhead
- rendering cost
- failure containment
- slot-bounded repaint or refresh behavior

Custom extension must not be allowed to make the core authoring shell unpredictably sluggish.

---

## Performance Anti-Patterns

The system must reject:

- global rerender on small local interactions
- hidden broad subscriptions in every module
- synchronous heavy runtime measurements in hot paths
- coupling preview correctness to expensive full-tree recomputation
- using performance hacks that break architecture semantics
- “works on my machine” as performance validation

---

## Performance Validation

Performance should be validated through:

- interaction-focused profiling
- targeted render or recomputation inspection
- smoke checks for obvious regressions
- careful review of hot paths
- evidence when major performance-sensitive seams change

This does not require premature obsession, but it does require awareness.

---

## Summary

The performance model for Live Scene Composer should prioritize responsive interaction, bounded recomputation, and local cost control. Selection, canvas interaction, preview, runtime mapping, and module contributions are the main areas to watch. The system should be designed so that normal authoring feels immediate and stable without sacrificing architectural clarity.
EOF

cat > "$DOCS_DIR/28_SECURITY_MODEL.md" <<'EOF'
# 28_SECURITY_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Security, Validation
- Scope: Safety, authority boundaries, restricted capabilities, and system hardening principles

---

## Purpose

This document defines the security and authority model for Live Scene Composer. It exists because a live authoring product that interfaces with runtime-facing state can become dangerous very quickly if permissions, boundaries, and execution surfaces are not governed carefully.

Security here includes both traditional safety concerns and architectural authority control.

---

## Security Model Summary

The security model for Live Scene Composer is based on:

- explicit authority boundaries
- typed mutation governance
- bounded extension surfaces
- restricted capability exposure
- clear sibling product separation
- safe defaults
- containment of failures and privileges

The system is not a trusted freeform scripting shell.
It is a governed authoring environment.

---

## Core Security Principles

### 1. Least authority

Give each subsystem only the authority it needs.

### 2. Explicit write boundaries

All write-capable runtime-facing changes from the Composer must go through `runtime-mutation-bridge`.

### 3. Safe defaults

Normal operation should occur in Safe Mode with bounded capabilities.

### 4. No hidden privilege inheritance

Diagnostic power from Runtime Debug Console must not quietly transfer into the Composer.

### 5. Bounded extension

Modules and future custom widgets must not receive unrestricted access by default.

### 6. Local containment

A failure or misuse in one area should not automatically compromise the rest of the product.

---

## Security-Relevant Boundaries

The most security-relevant top-level boundaries are:

- `console-core`
- `runtime-debug-console`
- `live-scene-composer`
- `runtime-mutation-bridge`

The most sensitive among them for authority control is `runtime-mutation-bridge`.

The most sensitive for extension control is future custom widget support.

---

## Authority Model

Authority in the system should be explicit and layered.

### Shared infrastructure authority

`console-core` should have infrastructure authority, not product-specific mutation authority.

### Diagnostic authority

`runtime-debug-console` may have stronger inspection capabilities for diagnostics, but that must not imply authoring write authority.

### Authoring authority

`live-scene-composer` may create mutation intent, but should not directly apply unrestricted runtime writes.

### Mutation authority

`runtime-mutation-bridge` governs whether requested write-capable actions are allowed, and under what mode and policy.

---

## Safe Mode

Safe Mode should be the default authority posture.

It should allow:

- bounded visual changes
- approved layout operations
- approved text and style edits
- valid prefab insertions
- safe draft workflows

It should not allow:

- unrestricted scripting
- arbitrary runtime writes
- vague untyped privileged actions
- extension mechanisms that bypass policy

Safe Mode exists to protect both the product and the user.

---

## Advanced Mode

Advanced Mode may eventually enable more powerful capabilities, but it must still remain explicit, typed, and governed.

Advanced Mode should not be:

- an architecture bypass
- a hidden admin mode for unsafe writes
- a broad permission shortcut

If Advanced Mode exists, it must remain legible and testable.

---

## Mutation Security

Mutation security depends on the bridge enforcing:

- source validation
- target validation
- allowed command types
- mode policy
- reversibility or acceptance semantics as relevant
- adapter routing discipline

This is one of the central security mechanisms of the product.

---

## Module Security

Modules should operate through declared capabilities and approved SDK surfaces.

A module must not:

- access arbitrary runtime internals
- widen its own authority silently
- register hidden privileged actions
- act as a shadow bridge
- access sibling product internals by convenience

Modules are extension units, not privilege loopholes.

---

## Custom Widget Security

Custom widgets are a major security surface and must be tightly bounded.

The sandbox model should enforce:

- bounded region rendering
- restricted API surface
- no filesystem access
- no unrestricted DOM or global access
- no uncontrolled runtime mutation
- local failure isolation
- explicit capability declaration

Custom widgets are valuable only if they remain safer than raw code injection.

---

## Data Access Security

Composer-facing data access should remain scoped and intentional.

The system should avoid:

- exposing unrelated global state widely
- giving extension points broad hidden data access
- letting runtime mappings become a side-channel for unrestricted reads or writes

Data access should be designed, not leaked.

---

## Path and Dependency Security

Path discipline is also part of the security posture.

The system should reject:

- legacy or ambiguous shared-core paths
- forbidden sibling imports
- hidden route-binding privilege shortcuts
- accidental coupling that widens authority

Bad dependency direction is often a security problem in architecture clothing.

---

## Failure Security

When a sensitive operation fails, the system should fail in a way that:

- preserves state integrity
- does not widen authority
- does not silently fall back to unsafe paths
- remains diagnosable

A rejection followed by an unsafe fallback is a security failure.

---

## Security Anti-Patterns

The system must reject:

- direct runtime write access from UI layers
- broad “admin” helpers with unclear scope
- modules that mutate anything because they can import it
- custom widget paths with unrestricted power
- hidden privilege transfer from debug tooling
- mode toggles that do not actually change authority rules

---

## Summary

The security model for Live Scene Composer is built on bounded authority, explicit mutation governance, safe defaults, and restricted extension surfaces. The product must remain powerful without becoming permissive by accident. Security here is not only about hostile misuse; it is also about preventing the system from becoming architecturally unsafe.
EOF

cat > "$DOCS_DIR/29_OPERATIONS_GUIDE.md" <<'EOF'
# 29_OPERATIONS_GUIDE

## Document Status

- Status: Canonical
- Audience: Operators, Engineers, Validation, Tooling
- Scope: Operational health, routine checks, incident handling, and runtime-awareness for the Composer ecosystem

---

## Purpose

This document explains how the system should be operated and monitored from an engineering and product-health perspective. It exists because a live authoring system requires operational discipline, not just code correctness.

Operations here means keeping the system trustworthy, diagnosable, and stable in real use.

---

## Operations Principles

Operational handling of the Composer ecosystem should prioritize:

- visibility into system health
- fast identification of boundary failures
- clear incident classification
- safe rollback or disablement paths
- local containment
- preservation of draft and baseline trust

The goal is not to treat every issue like an emergency.
The goal is to know what kind of problem it is and how to respond without making it worse.

---

## Operational Scope

Operational awareness should cover at minimum:

- Composer shell health
- bridge health
- module registration health
- dependency or path drift indicators
- runtime integration health
- selection and preview responsiveness
- failure isolation effectiveness
- future sandbox/custom widget containment if enabled

---

## Routine Health Checks

A healthy project should have routine confidence checks such as:

- architecture guard passes
- canonical path rules remain intact
- key architecture-related tests pass
- bridge validation paths behave as expected
- no composer/debug coupling regressions appear
- local or CI typecheck remains clean
- critical shells and providers still initialize

Routine health checks reduce the odds of discovering foundation breakage late.

---

## Operational Signals to Watch

### Structural signals

- dependency drift
- unexpected registration changes
- reappearance of forbidden paths
- unreviewed protected-node changes

### Product behavior signals

- preview mismatches
- commit/revert inconsistencies
- selection or inspector desynchronization
- slot compatibility anomalies
- module-local failures becoming shell failures

### Runtime integration signals

- adapter errors
- stale runtime mapping
- bridge rejection spikes
- runtime-observed alignment problems

---

## Incident Categories

### Category 1: Architecture incidents

Examples:

- composer/debug coupling reintroduced
- forbidden import path reappears
- bridge bypass path discovered

These are high-severity because they threaten the foundation.

### Category 2: Mutation incidents

Examples:

- mutation command incorrectly allowed
- mutation rejection missing
- preview and commit behavior diverge dangerously

These are high importance because they affect trust and safety.

### Category 3: Domain incidents

Examples:

- slot/widget compatibility failures
- structure corruption
- draft/baseline confusion

These affect correctness and user confidence.

### Category 4: Experience incidents

Examples:

- severe selection lag
- inspector mismatch
- drag/resize instability

These are often user-visible and can quickly make the product feel broken.

### Category 5: Local module incidents

Examples:

- one module crashes
- one widget-type editor fails
- one contribution misbehaves locally

These should ideally be containable.

---

## Incident Response Principles

When an incident occurs:

1. classify it correctly
2. identify the affected boundary
3. assess whether protected nodes are involved
4. determine whether the issue is local or systemic
5. contain blast radius first
6. avoid architecture-breaking emergency hacks
7. preserve evidence for follow-up

A bad hotfix that widens unsafe behavior is not a successful incident response.

---

## Safe Containment Options

Containment may include:

- disabling or gating a module
- blocking a mutation command path
- reverting a protected-node change
- restoring canonical routing
- restricting a broken extension point
- falling back to read-only or reduced-authority behavior when appropriate

Containment is often better than a rushed invasive fix.

---

## Operational Logging Expectations

Operational logs should help answer:

- what boundary failed
- what command or target was involved
- whether failure was validation, integration, or execution-related
- whether failure was local or systemic

Logs should not drown operators in noise or require reading raw internals to understand severity.

---

## Recovery Considerations

Recovery should aim to preserve:

- accepted baseline state
- understandable draft state
- shell stability
- bounded failure scope
- architectural integrity

Recovery should not normalize bypasses or permanently widen authority.

---

## Change Management

Operationally significant changes should be treated with extra care, especially changes involving:

- mutation contracts
- provider seams
- adapter seams
- dependency policy enforcement
- module registration behavior
- sandbox or capability rules

These are not normal “small tweaks,” even when the diff is small.

---

## Operations Anti-Patterns

The operations model must reject:

- fixing incidents by bypassing the bridge
- hiding incidents by suppressing errors without containment
- merging unrelated risky changes while operational health is uncertain
- treating architecture guard failures as cosmetic
- using debug-only privileges to patch authoring behavior permanently

---

## Summary

Operations for Live Scene Composer should focus on keeping the system stable, visible, and governable. Boundary health, bridge integrity, module containment, and runtime integration quality are the main operational concerns. Good operations protect the product without sacrificing the architecture in the name of urgency.
EOF

cat > "$DOCS_DIR/30_DEPLOYMENT_MODEL.md" <<'EOF'
# 30_DEPLOYMENT_MODEL

## Document Status

- Status: Canonical
- Audience: Engineering, Tooling, Operations, Validation
- Scope: Deployment expectations, release safety, rollout discipline, and environment-aware risk management

---

## Purpose

This document defines the deployment model for Live Scene Composer and its related architecture. It exists because deployment is where architecture, safety, product behavior, and operational discipline all meet.

A bad deployment model can undo good architecture very quickly.

---

## Deployment Principles

Deployment should prioritize:

- safety over novelty
- bounded rollout over uncontrolled blast radius
- verification over optimism
- explicit enablement over accidental exposure
- rollback readiness
- boundary preservation during release

The Composer should not be deployed like an ungoverned front-end toy.
It has runtime-facing consequences and needs serious rollout discipline.

---

## Deployment Scope

The deployment model should consider:

- Composer shell changes
- module registration changes
- bridge contract changes
- dependency policy changes
- provider seam changes
- adapter changes
- runtime integration changes
- future custom widget or sandbox changes

Different changes have different deployment risk levels.

---

## Change Risk Tiers

### Tier 1: Low-risk deployment changes

Examples:

- doc-only updates
- isolated local UI polish
- non-semantic refactors in bounded private areas
- internal cleanup with strong unchanged behavior evidence

Expected handling:
Normal deployment flow.

### Tier 2: Medium-risk deployment changes

Examples:

- new safe module addition
- inspector contribution changes
- prefab library enhancements
- bounded widget editing improvements

Expected handling:
Targeted verification and clear release note context.

### Tier 3: High-risk deployment changes

Examples:

- mutation command changes
- provider seam changes
- dependency policy enforcement changes
- runtime adapter changes
- protected-node contract changes
- new capabilities in safe/advanced mode behavior

Expected handling:
Extra review, extra testing, explicit rollout caution, and strong rollback readiness.

---

## Deployment Readiness Checklist

Before deployment, confirm:

1. relevant tests pass
2. typecheck passes
3. architecture guard passes where applicable
4. protected-node changes are reviewed
5. dependency policy remains intact
6. no forbidden path or coupling regressions were introduced
7. docs remain consistent with system meaning
8. rollback approach is understood for risky changes

A release is not ready just because the app still renders.

---

## Rollout Strategy

The preferred rollout posture is gradual confidence, not broad assumption.

Good rollout behavior may include:

- bounded release scope
- targeted verification after deployment
- optional gating or feature flags for risky new capabilities
- staged enablement of new modules or mutation commands
- careful observation of bridge behavior and error signals

The exact rollout mechanics may vary, but the philosophy should remain conservative for protected seams.

---

## Feature Gating

Feature gating can be useful for:

- new modules
- new mutation commands
- advanced-mode capabilities
- early custom widget support
- risky runtime adapter changes

Gating is not a substitute for good design, but it is a valuable deployment safety mechanism when used deliberately.

---

## Bridge Deployment Considerations

Changes to `runtime-mutation-bridge` deserve extra caution because they directly affect what the Composer is allowed to do.

For bridge changes, deployment should consider:

- compatibility with existing callers
- rejection-path correctness
- target validation behavior
- mode policy behavior
- adapter routing correctness
- rollback implications if a command becomes too permissive or too restrictive

Bridge deployment mistakes can create either unsafe writes or broken authoring flows.

---

## Module Deployment Considerations

Module additions or changes should consider:

- registration correctness
- safe mode compatibility
- local failure containment
- impact on selection, inspector, and structure surfaces
- removal or disablement path if the module misbehaves

A module should be deployable without becoming irremovable.

---

## Provider and Adapter Deployment Considerations

Changes involving providers or adapters should be treated carefully because they often affect broad product behavior.

Key concerns:

- shell initialization
- runtime alignment
- scene mapping
- command routing
- boundary preservation

A provider or adapter deployment should never be treated as “just plumbing.”

---

## Rollback Philosophy

Rollback should be thought through before deployment for higher-risk changes.

Possible rollback strategies may include:

- revert the commit or release unit
- disable a module
- disable a new command path
- restore a prior provider seam
- re-enable stricter bridge validation

The important principle is:
rollback should not require introducing unsafe emergency architecture.

---

## Post-Deployment Verification

After deployment, verify at minimum:

- shell initialization
- selection and inspector coherence
- bridge behavior for critical commands
- no composer/debug boundary regressions
- no obvious performance collapse in key flows
- no abnormal rejection or failure spikes in critical seams where observability exists

The point is to confirm the important seams still hold in the deployed environment.

---

## Deployment Anti-Patterns

The deployment model must reject:

- releasing protected-node changes with no extra caution
- broad risky bundles with unclear blast radius
- skipping verification because the change “seemed minor”
- normalizing hotfixes that bypass architecture
- deploying new authority without updated policy or tests
- treating rollback as an afterthought

---

## Summary

The deployment model for Live Scene Composer should be conservative around protected seams, mutation behavior, provider and adapter changes, and new extension capabilities. Good deployment discipline preserves the same thing the architecture is trying to preserve: clarity, safety, and confidence as the product evolves.
EOF

echo "[OK] Generated Part 3 docs in: $DOCS_DIR"
echo "[OK] Files created:"
ls -1 "$DOCS_DIR"/21_DEVELOPER_GUIDE.md \
      "$DOCS_DIR"/22_CONTRIBUTING.md \
      "$DOCS_DIR"/23_CODE_STYLE.md \
      "$DOCS_DIR"/24_TESTING_STRATEGY.md \
      "$DOCS_DIR"/25_DEBUGGING_GUIDE.md \
      "$DOCS_DIR"/26_ERROR_HANDLING.md \
      "$DOCS_DIR"/27_PERFORMANCE_MODEL.md \
      "$DOCS_DIR"/28_SECURITY_MODEL.md \
      "$DOCS_DIR"/29_OPERATIONS_GUIDE.md \
      "$DOCS_DIR"/30_DEPLOYMENT_MODEL.md