# Code-Atlas Visual Relevance Policy

**Document ID:** `CA-VRP-001`  
**Version:** `1.0`  
**Status:** `Approved for technical landing`  
**Owner:** `Code-Atlas`  
**Scope:** dependency graph generation and SVG readability  
**Related:** [`code-atlas-visibility-filtering-spec.md`](./code-atlas-visibility-filtering-spec.md)

---

## Purpose

Define the official policy for what should and should not be visible in Code-Atlas graphs so the SVG output is readable by humans before it is exhaustive for machines.

---

## Core Principle

The visible graph is **not** the full graph.

The visible graph is a **curated subset** of the total dependency graph, selected for architectural relevance.

### Golden Rule

**Filter first, arrange second, beautify last.**

No theme, spacing adjustment, or layout enhancement can compensate for an overloaded input graph.

---

## Mandatory Pipeline Order

Visibility selection must happen in the following order:

1. Raw graph construction
2. Semantic filtering
3. Entity collapsing
4. Optional issue/note injection
5. Layout
6. SVG rendering

### Contract

- `layout` must never decide what exists or does not exist
- `render` must never rescue noise that should have been removed earlier
- `issues` must not enter the main graph body unless the preset explicitly allows it
- `externals` must not enter the visible canvas by default

---

## Official Presets

Only the following presets exist:

### `executive`

Default preset.  
Optimized for fast reading, architecture review, and decision-making.

### `engineering`

Technical analysis preset.  
Shows more detail while preserving readability.

### `raw`

Forensic preset.  
Shows almost everything and intentionally sacrifices readability.

---

## Visibility Rules by Preset

## `executive`

### Included

- `package` nodes
- `package -> package` relationships
- only active groups
- only internal package-level edges
- package-level focus when applicable
- package hubs when applicable

### Collapsed

- all modules inside each package
- all external dependencies into a single logical `external` bucket, only if they explain a dominant dependency
- all warnings into a side panel or footer

### Hidden

- `module` nodes
- individual external nodes
- issue nodes in the main canvas
- irrelevant islands
- self-loops and trivial relationships
- visually weak edges

### Usage Rule

If a repository does not read clearly in `executive`, the problem is filtering, not theming.

---

## `engineering`

### Included

- relevant internal modules
- relevant packages
- high-value internal edges
- hubs
- cross-group connections
- explicit or inferred focus
- focus neighbors ranked by importance

### Collapsed

- low-degree leaves hanging from hubs
- repetitive low-traffic clusters within the same package
- externals by root library, not by symbol
- issues into a side panel unless debug mode explicitly allows them

### Hidden

- internal modules without useful connectivity
- individual externals by default
- long utility chains that do not improve system understanding
- redundant edges inside the same subtree
- low-value context edges below the preset threshold

### Usage Rule

`engineering` must not render “everything parsed”.  
It must render only what helps explain architecture, coupling, flow, and hot zones.

---

## `raw`

### Included

- all internal nodes
- all internal edges
- individual externals
- visible issues
- islands
- long chains
- full focus neighborhood

### Collapsed

- nothing, except where required by hard technical safety limits

### Hidden

- only what would violate safety, performance, or hard execution limits

### Usage Rule

`raw` exists for inspection and debugging, not as the normal reading mode.  
It must never be the default.

---

## External Dependency Policy

### Official Rule

External dependencies are **not first-class visual citizens** in normal architectural reading.

### Per Preset

- `executive`: hidden
- `engineering`: collapsed by root library
- `raw`: visible individually

### Exception

An external may be shown in `engineering` if at least one is true:

- it connects multiple internal groups
- it dominates a hub’s traffic
- it explains a real architectural boundary
- it is part of the explicit analysis focus

---

## Focus Policy

### Official Rule

The `focus` view is not “all direct neighbors and done”.  
It is a narrative view centered on architectural causality.

### Must Include

- the focus node
- relevant inbound nodes
- relevant outbound nodes
- relevant mixed nodes
- minimal justified context

### Must Exclude

- low-value lateral context
- externals unless they explain the focus
- trivial leaves
- first-hop noise

### Visibility Priority

When rendering `focus`, visible priority must be:

1. `hero`
2. `mixed`
3. `inbound`
4. `outbound`
5. `context`

---

## Issues and Notes Policy

### Official Rule

`issues` are diagnostic metadata, not primary structure.

### Per Preset

- `executive`: footer or side panel
- `engineering`: side panel
- `raw`: may enter as visible graph nodes

### Limit

Issues must never displace architectural nodes from the main visual plane.

---

## Hard Filtering Rules

These rules apply before layout.

### Rule 1

Any visible entity must satisfy at least one of the following:

- is the focus
- connects groups
- is a hub
- has significant traffic
- explains a meaningful boundary
- is required by the preset

### Rule 2

Any entity that satisfies none of the above must:

- be hidden
- or be collapsed

### Rule 3

Islands are only shown in `raw`, or in `engineering` when they are the focus.

### Rule 4

Self-loops are not shown outside `raw`.

### Rule 5

If two packages exchange many weak relationships, the preset may collapse them into a single aggregated edge.

### Rule 6

In `engineering`, each group has a finite visual budget:

- maximum visible nodes per group
- maximum visible cross-group edges per group
- maximum visible leaves per hub

### Rule 7

In `focus`, each lane has a finite visual budget:

- inbound top-N
- outbound top-N
- mixed top-N
- context top-N

---

## Visual Budget Rule

Each preset must operate under a **maximum visible complexity budget**.

### Recommended Budget Intensity

- `executive`: very low
- `engineering`: medium
- `raw`: high

### Trim Order

When the visible budget is exceeded, trim in this order:

1. issues
2. externals
3. islands
4. trivial leaves
5. weak intra-group edges
6. lateral context
7. low-score nodes

---

## Truth Rule

If a person cannot explain the SVG in under 60 seconds, the SVG failed.

### Operational Meaning

A valid graph must allow a reader to identify quickly:

- which zones are the system center
- what depends on what
- where coupling exists
- which cross-group relations matter
- where the focus lives
- what has been hidden by design

---

## Official Defaults

### Product Default

- preset: `executive`
- initial view: `package`
- externals: hidden
- issues: panel or footer
- focus: optional

### Technical Analysis Default

- preset: `engineering`
- externals: collapsed
- issues: side panel
- focus: explicit or inferred

---

## Acceptance Criteria

The policy is considered correctly implemented when:

- `executive` is readable without aggressive zoom
- `engineering` allows following real dependencies without turning into spaghetti
- `raw` still exists for full inspection
- visual themes improve clarity but do not carry the burden of saving structural noise
- switching presets changes the **amount and kind of truth shown**, not merely the color palette

---

## Final Decision

Code-Atlas must adopt preset-driven semantic filtering before layout, using:

- `executive` as the default mode
- `engineering` as the curated technical mode
- `raw` as the forensic mode

No more rendering everything first and trying to make it look pretty afterward.
