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
