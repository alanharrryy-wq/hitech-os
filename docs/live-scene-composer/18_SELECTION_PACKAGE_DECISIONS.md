# 18_SELECTION_PACKAGE_DECISIONS

## Decision A

The package includes both docs and reference source.

### Why

Pure docs would leave the next engineering step ambiguous again.
Pure code would drift from the architecture contract too easily.

## Decision B

The installer stages source files under `tools/live-scene-composer/selection-store-inspector-target-wiring-v1` even when repo source root inference is ambiguous.

### Why

A safe staged install is better than guessing a wrong product path and spraying files into the repo like confetti.

## Decision C

The source implementation is framework-light.

### Why

The contract matters more than one UI framework opinion right now.
Keeping the selection store and derivation logic mostly plain TypeScript makes adoption easier.

## Decision D

Tests are lightweight and reference-oriented.

### Why

They are meant to anchor behavior and contracts, not pretend we already know the repo’s final runner topology.

## Decision E

No multi-select in v1.

### Why

Multi-select would multiply surface, capability, and mutation complexity too early.
The project’s current leverage is in nailing single-target semantics first.
