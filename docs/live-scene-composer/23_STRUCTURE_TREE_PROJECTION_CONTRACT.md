
# 23_STRUCTURE_TREE_PROJECTION_CONTRACT

## Document Status

- Status: Proposed Canonical
- Audience: Architecture, Engineering
- Scope: Structural projection rules from Scene -> Layout -> Slots -> Widgets into the Structure Tree

---

## Purpose

This document defines how structural authoring data becomes a tree projection for authoring navigation.

The tree must preserve the product's canonical domain model:

**Scene -> Layout -> Slots -> Widgets**

The tree is not a random UI list.
It is a typed authoring projection.

---

## Projection Inputs

A healthy tree projection should be built from:

- scene metadata
- layout node graph
- slot registry / slot metadata
- widget placement or slot-hosted widget membership
- visibility or lock hints where available
- diagnostic state such as selected/stale status from the synchronization seam

---

## Projection Rules

1. The scene root appears exactly once.
2. Layout nodes form the primary structural hierarchy.
3. Slot nodes appear where referenced by layout nodes.
4. Widgets appear under the slot that currently hosts them.
5. A widget must not appear as though it owns layout children.
6. Missing entities may appear only as diagnostics ghosts, not as normal active nodes.
7. Node ids must remain stable enough for keyboard navigation and expansion-state persistence.

---

## Node Kinds

Expected structural node kinds include:

- `scene`
- `layout-node`
- `slot`
- `widget`
- `diagnostic-ghost`

The first four map to domain entities.
The last exists only for bounded stale/recovery diagnostics.

---

## Tree Node Payload Expectations

Each node should carry enough data for:

- title and subtitle rendering
- icon or badge rendering
- stable ref resolution
- expanded/collapsed behavior
- keyboard navigation
- selection affordance
- diagnostics notes where appropriate

It should not carry the entire mutable scene as payload.

---

## Anti-Patterns

Reject these:

- flattening the tree into panels or unnamed UI items
- placing widgets directly under scene if a slot owns them
- using DOM order as the semantic structure source
- letting tree projection mutate scene structure
- hiding stale diagnostics as if the old node still exists normally

---

## Summary

The Structure Tree is a typed projection of authoring structure, not a convenience outline. It must preserve the canonical domain hierarchy, remain navigable, and support synchronized selection without becoming a second scene model.
