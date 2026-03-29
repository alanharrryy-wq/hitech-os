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
