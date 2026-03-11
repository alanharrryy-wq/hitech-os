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
