
# 32_STRUCTURE_CANVAS_REPO_INTEGRATION_PLAYBOOK

## Safe integration order

1. Install docs into `docs/live-scene-composer`
2. Stage source seam under `tools/live-scene-composer/structure-tree-canvas-sync-over-selection-store-v1`
3. Review source seam and align target composer path
4. Mirror into composer src only when the path is clear enough
5. Wire the seam incrementally: projection -> coordinator -> surface adapters -> mutation-intent entrypoints

## Good first repo experiments

- replace local tree projection builder with `buildStructureTreeProjection`
- derive canvas overlays from `buildCanvasViewModel`
- route tree and canvas UI events through `createSurfaceCoordinator`
- keep runtime writes out; emit intents only

## Review checklist

- no debug-console imports inside composer seam
- no bridge bypasses
- tree projection keeps slot/widget relationships honest
- overlays clear on stale state
- mutation-intent builders stay typed and target-aware
