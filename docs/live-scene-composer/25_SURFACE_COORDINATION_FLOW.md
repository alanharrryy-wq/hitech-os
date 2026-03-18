
# 25_SURFACE_COORDINATION_FLOW

## Document Status

- Status: Proposed Canonical
- Audience: Architecture, Engineering
- Scope: Flow of typed events and instructions among Selection Store, Structure Tree, Canvas, and mutation-intent entrypoints

---

## Core Flow

1. A surface emits a typed event.
2. The Surface Coordinator normalizes the event.
3. The coordinator updates or queries the Selection Store.
4. The coordinator rebuilds synchronized instructions for tree, canvas, and inspector.
5. Optional mutation-intent entrypoints become available only from explicit selected target data.
6. Diagnostics records are emitted for tests and debugging.

---

## Why a coordinator exists

Without a coordinator, synchronization logic leaks into:

- tree components
- canvas components
- inspector components
- random hooks
- one-off refactor leftovers

The result is usually duplicated logic and divergent behavior.

---

## Coordinator Responsibilities

- normalize surface events
- call store operations deterministically
- derive per-surface instruction sets
- generate stale/recovery suggestions
- emit event records for tracing
- expose capability summaries for mutation-intent builders

---

## Coordinator Must Not Own

- full scene model mutation
- runtime writes
- arbitrary component lifecycle details
- unrelated product modules

---

## Summary

The Surface Coordinator is the conductor, not the orchestra pit. It coordinates typed surface behavior around one selection seam without absorbing domain ownership or mutation authority.
