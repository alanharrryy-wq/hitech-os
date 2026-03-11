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
