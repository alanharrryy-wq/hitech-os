# Stacking and Scope

This pack stacks on top of:
1. Selection Store + InspectorTarget wiring
2. Structure Tree + Canvas sync over Selection Store

It does **not** replace those seams.
It consumes their outputs and makes the write path explicit.

## Scope
- mutation intent building
- mode policy checks
- validation
- preview session state
- diffing
- commit/discard/revert orchestration
- adapter-facing bridge requests
- diagnostics and history

## Out of scope
- runtime persistence
- full product UX polish
- custom widget capability runtime
- server-side approval flows
