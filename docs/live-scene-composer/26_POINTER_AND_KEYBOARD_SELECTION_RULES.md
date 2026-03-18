
# 26_POINTER_AND_KEYBOARD_SELECTION_RULES

## Document Status

- Status: Proposed Canonical
- Audience: Engineering, Product, QA
- Scope: Selection interaction rules for pointer and keyboard behavior across Structure Tree and Canvas

---

## Pointer Rules

### Canvas pointer hit

- hit results must be normalized into typed refs
- background click may clear selection only when no protected drag/edit mode is active
- pointer selection should preserve scene revision metadata
- pointer hit ambiguity should prefer explicit target priority rules, not DOM coincidence

### Tree pointer selection

- clicking a tree node selects that node's typed ref
- expansion toggles must not silently mutate selection unless explicitly requested by the user
- stale ghost nodes may support explicit recovery or diagnostics actions, never silent selection rewrites

---

## Keyboard Rules

- arrow navigation operates on tree projection order
- Enter or Space confirms the focused node as selection
- Escape clears selection or closes transient affordances according to local UX policy
- stale nodes cannot become normal active selection through keyboard navigation without explicit recovery

---

## Priority Hints

When multiple target candidates exist for a canvas hit, a reasonable default priority is:

1. widget
2. slot
3. layout node
4. scene

This makes the most precise visible target win unless a specific mode changes the rule.

---

## Summary

Pointer and keyboard behavior must be deterministic, typed, and projection-aware. Input handling must create explicit target requests, not accidental selection side effects.
