
# 29_STRUCTURE_CANVAS_TEST_PLAN

## Test categories

1. structure projection correctness
2. canvas overlay derivation correctness
3. tree/canvas synchronization after selection changes
4. stale and recovery behavior
5. keyboard navigation determinism
6. pointer-hit priority correctness
7. mutation-intent enablement gating
8. diagnostics event log legibility

## Must-have checks

- removing a widget marks selection stale and clears editable overlays
- moving selection by keyboard updates tree highlight and canvas focus together
- scene selection produces scene-level focus frame and tree root highlight
- slot selection enables slot insertion entrypoints but not widget-style entrypoints
- stale selection suppresses all write-capable entrypoints

## Suggested repo validation

- targeted typecheck for the seam
- focused tests for projections and coordinator
- architecture guard after doc installation
