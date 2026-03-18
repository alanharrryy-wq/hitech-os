# 15_SELECTION_MUTATION_INTENT_BOUNDARY

## Document Status

- Status: Proposed Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Boundary between selection-assisted UX and explicit mutation targeting

---

## Purpose

This document defines the line between **selection** and **mutation intent**.

That line matters because selection is a convenience for UX focus, while mutation target identity is a safety-critical part of write-capable behavior.

---

## Core rule

Selection may assist mutation composition, but it may not replace an explicit target contract.

In practical terms:

- the inspector may start from the current selection
- a command may prefill its target from the current selection
- a toolbar button may act on the selected item only after an explicit typed target is composed

But a write-capable mutation must still carry its own typed target.

---

## Healthy mutation composition flow

1. user selection establishes current editorial focus
2. UI derives the visible editing affordance
3. user triggers an action
4. action composes a typed mutation target from the selected ref
5. mutation request is validated and routed through the proper boundary

That means the write does not depend on a hidden global “current thing” at execution time.

---

## Example

### Bad

`updateWidgetStyle({ color: "red" })`

This is ambiguous if it secretly means “whatever widget is selected now.”

### Better

`updateWidgetStyle({ target: { kind: "widget", widgetId: "widget-7" }, patch: { color: "red" } })`

Now the target is explicit, testable, and governable.

---

## Consequences for inspector actions

Inspector actions should be rendered from `InspectorTarget`, but the action payload must still embed a typed target.
That protects the system from races where selection changes between render time and mutation execution time.

---

## Summary

Selection is a navigation and editing-focus contract. Mutation targeting is a write-safety contract. They are related, but they must not collapse into one vague mechanism.
