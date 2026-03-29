
# 30_STRUCTURE_CANVAS_PACKAGE_DECISIONS

## Decision A

Surface coordination is centralized in one seam rather than scattered across tree and canvas components.

## Decision B

Canvas overlays are derived from typed viewmodel projection rather than ad hoc component state.

## Decision C

Tree projection preserves Scene -> Layout -> Slots -> Widgets instead of flattening into generic items.

## Decision D

Reconciliation produces explicit stale state before any recovery suggestion.

## Decision E

Mutation-intent entrypoints are allowed, but direct writes remain prohibited.
