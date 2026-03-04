# LAYERS v1 Cookbook

Canonical source for Layer Toggles v1:

- `packages/ui-kit/src/layers/layerIds.ts`
- `packages/ui-kit/src/layers/resolveLayerFlags.ts`
- `packages/ui-kit/src/layers/layerFlagsContract.ts`
- `docs/design/layers/LAYER_FLAGS_SYSTEM.md`

Do not invent new IDs.

## Layer IDs

Stage:

- `stage.haze`
- `stage.vignette`
- `stage.noise`
- `stage.scanlines`
- `stage.horizon`
- `frame.bezel`

Cards:

- `card.blur`
- `card.innerStroke`
- `card.specular`
- `card.grain`
- `card.shadowAmbient`

Inset:

- `inset.shadow`

Motion:

- `motion.enabled`

## Querystring Rules

Precedence:

1. defaults
2. `layerProfile=neutral|fx|perf`
3. `layers=none|all|list`
4. `motion=on|off`

Debug panel visibility:

- only with `?debug=1`
- and only when `NODE_ENV !== "production"`

## Required Examples

1. Panic switch all OFF:

- `?layers=none`

2. Explicit single stage layer:

- `?layers=stage.noise`

3. Explicit card blur layer:

- `?layers=card.blur`

4. Performance profile:

- `?layerProfile=perf`

5. Debug panel:

- `?debug=1`

6. Motion override:

- `?motion=on`

## Additional Useful URLs

- `?layers=all` (debug only, never default)
- `?layers=stage.noise,card.innerStroke`
- `?layers=none&debug=1`
- `?layerProfile=fx&debug=1`

## Data Attribute Wiring

Stage root attributes:

- `data-layer-stage-haze="on|off"`
- `data-layer-stage-vignette="on|off"`
- `data-layer-stage-noise="on|off"`
- `data-layer-stage-scanlines="on|off"`
- `data-layer-stage-horizon="on|off"`
- `data-layer-frame-bezel="on|off"`

Card root attributes:

- `data-layer-card-blur="on|off"`
- `data-layer-card-inner-stroke="on|off"`
- `data-layer-card-specular="on|off"`
- `data-layer-card-grain="on|off"`
- `data-layer-card-shadow-ambient="on|off"`

Inset root attributes:

- `data-layer-inset-shadow="on|off"`

Motion:

- `data-layer-motion-enabled="on|off"`

Global root attributes on `html` (applied by provider):

- `data-layer-<id>` present as `"1"` when enabled, removed when disabled
- `data-layer-source="defaults|profile|layers|mixed"`
- `data-layer-profile="<profile|none>"`

## Blur Budget Rule

- Blur is only active when:
  - `data-layer-card-blur="on"`
  - and `@supports(backdrop-filter: blur(1px))`
- Otherwise card uses flat translucent surface.

## Reproduce a Layer Bug in 10 Seconds

1. Open `/pitch/01-double-engine?layers=none&debug=1`.
2. Toggle `stage.noise` in debug panel and verify `data-layer-stage-noise` changes on `.stage`.
3. Open `/pitch/01-double-engine?layers=card.blur&debug=1` and confirm blur only appears in browsers with `backdrop-filter` support.
4. Switch to `/pitch/02-industrial-flow?layerProfile=perf&debug=1` and verify `card.blur` and `motion.enabled` remain OFF.
5. Force precedence check with `/pitch/03-hitech-os?layers=stage.scanlines&layerProfile=fx&debug=1`; verify only explicit layers apply.
