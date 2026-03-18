# 14_SELECTION_STALENESS_AND_RECOVERY

## Document Status

- Status: Proposed Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Stale selection handling and explicit recovery rules

---

## Purpose

Selection bugs get expensive when stale targets are silently retargeted.
This document defines how stale selection should be represented, surfaced, and recovered.

---

## What makes a selection stale

A selection is stale when the last known selected target can no longer be safely resolved under the current authoritative revision.

Examples:

- selected widget removed
- selected slot destroyed by layout change
- selected layout node replaced during structure rebuild
- selected ref no longer valid after draft refresh

---

## Required stale behavior

When a selection becomes stale:

1. the store must preserve the last known kind/ref for diagnostics
2. the store must mark the snapshot as `stale`
3. canvas must remove target-specific affordances
4. structure tree must stop claiming the target is actively selected
5. inspector must become `unavailable`
6. write-capable target-specific actions must disappear or disable safely

---

## Recovery rules

Allowed recovery strategies include:

### Manual recovery

The user explicitly selects a new entity.
This is the safest and most understandable recovery.

### Explicit fallback recovery

The system selects a known safe fallback, such as the scene root, but only through an explicit, named recovery rule.

### Ref remap recovery

If a structure migration or revision replacement exposes a validated old-ref to new-ref mapping, the system may recover to that exact mapped target.

---

## Forbidden stale recovery

The following behaviors are forbidden:

- nearest surviving widget wins
- last visible sibling wins
- whatever canvas overlay is under the cursor wins
- inspector quietly keeps editing the last resolved payload anyway

These behaviors hide real invalidation and make mutation targeting dangerous.

---

## UX guidance

A stale selection message should say something close to:

- the previously selected target is no longer available
- selection must be refreshed
- choose a new target or accept the explicit fallback

It should not pretend everything is fine.

---

## Summary

Staleness is not an annoying edge case to smooth over. It is a first-class state that protects the user from editing the wrong thing after the target disappeared.
