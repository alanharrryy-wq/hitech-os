# Layer Flags System (Keystone + UI Kit)

## Objective

Provide deterministic, shareable visual states for pitch pages:

1. URL query params resolve to layer flags.
2. Layer flags are stored in `LayerFlagsProvider`.
3. Provider applies root `data-layer-*` attributes on `html`.
4. CSS selectors react to those attributes.
5. Debug tooling can inspect, toggle, share, and export diagnostics.

## Next.js App Router Note

In Keystone pitch pages (`app/pitch/**/page.tsx`), `searchParams` may arrive as a promise in modern Next.js.
Pages must resolve `searchParams` asynchronously before calling `resolvePitchLayerFlags`, otherwise URL layer overrides can be ignored on first render.

## Source of Truth

- Contract: `packages/ui-kit/src/layers/layerFlagsContract.ts`
- IDs + attribute mapping: `packages/ui-kit/src/layers/layerIds.ts`
- Resolver + query canonicalization: `packages/ui-kit/src/layers/resolveLayerFlags.ts`
- DOM applier: `packages/ui-kit/src/layers/applyLayerFlagsToDom.ts`

## Query Parameters

- `layers=none|all|id1,id2,...`
- `layerProfile=neutral|fx|perf`
- `motion=on|off`
- `debug=1`

Backward compatibility:

- `motion.enabled` inside `layers=` is accepted as alias for `motion=on`.
- Unknown layer tokens are ignored and reported in diagnostics/UI.

## Precedence

Resolution precedence is deterministic:

1. `defaults` (all flags off)
2. `profile` (`layerProfile`)
3. `layers` (`layers=...`)
4. `motion` (`motion=on|off`)
5. `developer-overrides` (runtime actions in debug/provider)

By default, URL overrides win over defaults/profiles.

## DOM Contract

Target: `document.documentElement` (`html`)

- Enabled layer: set mapped attribute to `"1"` (example: `data-layer-card-blur="1"`).
- Disabled layer: remove the attribute.
- Metadata:
  - `data-layer-source="defaults|profile|layers|mixed"`
  - `data-layer-profile="<profile|none>"`

The applier diffs previous state to avoid redundant DOM writes.

## Canonical URL / Share Links

Canonical query key order:

1. `layers`
2. `layerProfile`
3. `motion`
4. `debug`
5. remaining keys (alphabetical)

Share links are generated from the resolved state and current route, ensuring reproducible looks.

## Debug Tooling

`LayerDebugPanel` (dev + `debug=1`) provides:

- Current source/profile/motion + enabled count.
- Unknown token reporting.
- Live toggles for profile/layers/motion.
- Copy share URL.
- Diagnostic JSON export containing:
  - route
  - timestamp
  - user-agent
  - resolved flags/source/profile/unknown tokens
  - computed canonical URL

Keystone adds a dedicated `Share Look` button on pitch pages (dev/debug scope).

## Troubleshooting

1. Open any pitch route with `?debug=1`.
2. Verify `html` has `data-layer-*` attributes.
3. Toggle a layer in debug panel and confirm attribute diff in DevTools.
4. Copy Scene Link and open in a fresh tab to verify same visual state.
5. If parsing issues exist, check unknown tokens section and exported diagnostic JSON.
