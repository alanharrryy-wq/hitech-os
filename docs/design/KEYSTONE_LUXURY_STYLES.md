# Keystone Luxury Styles

## Decision Matrix

| Style ID | Visual posture | Accent behavior | Surface behavior | Hard bans |
|---|---|---|---|---|
| `LIQUID_GLASS` | Frosted translucent layers | semantic accents may glow within cap | blur+tint allowed only through material recipes | neon hues, thick bloom, clutter |
| `GOLD_NOIR_TERMINAL` | Matte black enamel with restrained gold | gold only for micro-emphasis, never wall-to-wall fill | low glow, precision hairlines | rainbow ramps, gamer LEDs, thick rims |
| `GRAPHITE_PRISM_ISO` | Graphite/petrol technical stack | prism gradients allowed only for chart data channels | subtle grid/grain overlays on cards only | gradient text, gradient page backgrounds, heavy glow |

## Mandatory Budgets

1. Accents per screen: `<= 3`
2. Accents per chart: `<= 4`
3. Hero motion events per screen: `<= 1`
4. Reduced motion path: always render final state (`motion=off` behavior)

Style-specific ceilings are encoded in token packs under `packages/ui-kit/src/luxury/tokens/`.

## Surface Rulebook

`SurfaceId` must always resolve through the material engine. Do not style these surfaces ad-hoc:

- `controlRoomHud`
- `pitchCard`
- `pitchPanel`
- `kpiWidget`
- `tableDense`
- `drawer`
- `rail`
- `popover`

## Anti-Flicker Contract

- No query rewrites during mount.
- Query normalization is allowed only on explicit user actions.
- Normalization must be idempotent and preserve non-luxury keys.

## Derive, Do Not Invent

Valid derivation examples:

- `glass/inset` derives from `glass/card` by reducing depth.
- `ink/drawer` derives from `ink/card` and adjusts shell context.
- `graphite/inset` derives from `graphite/card` with tighter elevation.

Invalid invention examples:

- One-off CSS classes with custom glow radii.
- New semantic color intent outside the approved intent set.
- New premium preset IDs not represented by `MaterialId`.

## Acceptance Checklist

1. Uses `applyLuxuryStyle` for style/surface binding.
2. Uses `applyLuxuryMaterial` for material application.
3. Uses semantic registry for accent decisions.
4. Passes governance budget check output (`OK` or explicit warnings).
