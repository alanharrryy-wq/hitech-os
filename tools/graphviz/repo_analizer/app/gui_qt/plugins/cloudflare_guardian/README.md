# Cloudflare Guardian Diagnostics graph radar

`CloudflareGuardianGraphRadar` is a **graph consumer** for Cloudflare Guardian Diagnostics.
It renders graph state that already exists in the snapshot, normalizes sparse payloads deterministically, and does **not** invent upstream nodes, edges, hotspots-as-graph, or host-side graph semantics.

## Official public API

The widget exposes only the frozen radar contract:

- `set_snapshot(snapshot)`
- `set_graph_data(nodes, edges=None, focus_node_id=None)`
- `set_focus_node(node_id)`
- `set_theme_tokens(tokens)`
- `set_animation_enabled(enabled)`
- `clear()`

## Canonical snapshot keys

Canonical keys consumed first:

- `nodes`
- `edges`
- `focus_node_id`
- `status_text`
- `subtitle`

Compatibility-only snapshot aliases accepted internally:

- `graph_nodes`, `radar_nodes`
- `graph_edges`, `radar_edges`
- `focus_node`, `focused_node_id`

Alias support is internal survivability glue only. Future shells should continue emitting canonical keys.

## Canonical node expectations

Preferred node fields:

- identity: `id` or `node_id`
- label: `label` or `title`
- coordinates: `x`, `y`
- optional weight: `weight`
- optional severity: `severity`
- optional active state: `active`
- optional metadata: `meta`

Coordinate handling:

- preferred range: `-1..1`
- compatibility-only range: `0..100`, normalized internally to `-1..1`
- explicit coordinates are clamped into the supported normalized range
- missing coordinates stay in radar ownership and use deterministic fallback placement

## Canonical edge expectations

Preferred edge fields:

- `source`
- `target`
- optional `weight`
- optional `active`
- optional `kind`

Compatibility-only endpoint aliases accepted internally:

- `from`, `to`, `src`, `dst`

The radar ignores orphan edges instead of repairing or synthesizing endpoints.

## Optional hotspot rendering

The frozen public contract still treats the radar as a graph consumer first.
When a snapshot mapping already includes canonical `hotspots`, v6 renders them as **informational perimeter signals only**:

- they are not converted into graph nodes
- they do not create edges
- they do not replace `nodes` / `edges`
- they remain local rendering hints for severity and operator attention

Preferred hotspot item fields when present:

- `id`
- `label`
- optional `severity`
- optional `active`
- optional `meta`

## Sparse-data and deterministic fallback behavior

The widget is intentionally strict about not manufacturing graph truth while still remaining usable on partial payloads:

- duplicate node ids resolve deterministically as first-seen-wins
- orphan edges are ignored, not repaired
- nodes missing both `x` and `y` stay visible through deterministic fallback placement
- missing or invalid focus falls back to the first active node, otherwise the first normalized node, otherwise empty focus
- empty or missing node payloads render a valid empty radar state
- canonical keys win over alias keys when both are present
- when no graph exists but canonical `hotspots` exist, the widget keeps an empty-valid graph and renders hotspots as informational signals only

## Implemented visual and interaction states

v6 ships the behavior it documents:

- premium layered radar surface with scanline/grid framing
- focus emphasis with halo pulse and stronger edge glow
- explicit-vs-fallback node treatment
- sparse-data footer notes and empty-state dignity
- hotspot perimeter signals with severity / active styling
- local hover inspection for nodes and hotspots
- animation that is optional and correctness-independent

## Theme handling

`set_theme_tokens(tokens)` accepts:

- a `SkinTokens`-like object with matching attributes
- a mapping-like payload with matching keys
- `None`, which restores the built-in dark fallback theme

The widget reads only a narrow visual token subset:

- `bg`, `panel`, `panel_alt`
- `border`, `border_soft`, `border_strong`
- `text`, `text_muted`
- `accent`, `accent_glow`
- `success`, `warning`, `danger`
- `selection`, `focus_ring`, `shadow`

## Integration notes

- keep canonical snapshot keys primary in the shell
- keep alias handling local to the radar implementation
- do not promote shell-local graph aliases into shared docs or summaries without a frozen-contract update first
- treat this slice as a view over existing graph state, not as a hidden graph model builder

