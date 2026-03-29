# 51_PREVIEW_SESSION_MODEL

## Purpose

A preview session is the explicit authoring unit for in-progress mutation work.

A preview session exists so that the system can answer:
- what changes are currently being previewed
- what baseline or draft revision they were computed against
- what can still be committed
- what can be discarded
- what can be reverted locally

## Session shape

A preview session should contain:
- session id
- scene id
- baseline revision
- draft revision
- opened at
- last updated at
- active mutation ids
- staged preview patches
- derived diff summary
- warnings
- commit readiness flag

## Rules
1. A preview session is tied to a known revision context.
2. A preview session may aggregate multiple preview-only mutations.
3. A preview session must be discardable without pretending it was accepted.
4. A preview session should provide a compact summary for compare UI.
5. A preview session does not own long-term baseline truth.

## Anti-patterns
- preview state spread across random React components
- visible preview with no session identity
- session ids recreated on every keystroke without lineage
- commit with no recorded preview lineage
