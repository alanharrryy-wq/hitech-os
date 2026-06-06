# Code-Atlas Visibility Filtering Spec

**Document ID:** `CA-VFS-001`
**Version:** `1.0`
**Status:** `Ready for implementation`
**Owner:** `Code-Atlas`
**Scope:** preset-driven visibility filtering and thresholds
**Related:** [`code-atlas-visual-relevance-policy.md`](./code-atlas-visual-relevance-policy.md)

---

## Purpose

Turn the visual relevance policy into deterministic, executable rules with explicit thresholds, ordering, and validation criteria.

---

## Immediate Objective

Build a formal visibility-selection layer between the raw graph and the layout engine.

### Required Output Flow

1. build raw graph
2. compute relevance metrics
3. apply preset
4. collapse or hide entities
5. pass visible graph to layout

### Design Rule

Layout does not decide relevance.
It only arranges what the filtering layer already approved.

---

## Required Preset Configuration

A preset definition must include at least:

- preset name
- target view
- whether externals are shown
- whether externals are collapsed
- whether issues are shown
- maximum visible node budget
- maximum visible edge budget
- maximum visible nodes per group
- maximum visible items per `focus` lane
- minimum node score for visibility
- collapse rules
- discard rules

---

## Required Scores

Every potentially visible node and edge must receive a score.

## Node Score

The node score must combine at least:

- inbound
- outbound
- hub status
- island status
- cross-group participation
- package status
- focus status
- focus-neighborhood participation
- external status
- issue/note status

### Recommended Signal

Higher node score means higher survival probability.

### Required Penalties

- `external` penalized in `executive` and `engineering`
- `note` penalized outside `raw`
- `island` penalized outside `raw`
- low-traffic leaf penalized in `engineering`

## Edge Score

The edge score must combine at least:

- weight
- whether it connects distinct groups
- whether it touches a hub
- whether it touches the focus
- self-loop status
- whether both endpoints have low score
- whether it is redundant with a stronger aggregate edge

### Required Penalties

- self-loop reduced close to zero outside `raw`
- weak intra-group edge penalized in `executive`
- external edge penalized outside `raw` unless an explicit exception applies

---

## Initial Thresholds by Preset

These are the recommended v1 thresholds.

## `executive`

### Nodes

- max total visible: **24**
- max per group: **6**
- minimum node score: **high**
- `package`: visible
- `module`: hidden
- `external`: hidden
- `note`: hidden from main canvas

### Edges

- max total visible: **18**
- only `package -> package`
- self-loops: no
- intra-group edges: no
- cross-group edges: yes, above threshold only
- weak edges: hidden

### Focus

- if focus exists, elevate the priority of its package
- do not break abstraction down to module level

---

## `engineering`

### Nodes

- max total visible: **60**
- max per group: **10**
- max leaves per hub: **3**
- minimum node score: **medium**
- `package`: visible
- `module`: visible if above threshold
- `external`: collapsed by root
- `note`: outside main canvas

### Edges

- max total visible: **90**
- self-loops: no
- intra-group edges: yes, but only top relevant ones
- cross-group edges: yes, high priority
- edges to externals: only if they explain a boundary or the focus
- redundant edges: collapse

### Focus

- inbound top-N: **8**
- outbound top-N: **8**
- mixed top-N: **6**
- context top-N: **4**

---

## `raw`

### Nodes

- max visible: bounded only by technical limits
- `package`: visible
- `module`: visible
- `external`: visible
- `note`: visible

### Edges

- all visible unless truncated by safety limits

### Focus

- preserve the full neighborhood according to raw logic

---

## Collapse Rules

## Externals

### `executive`
- hide entirely

### `engineering`
- collapse by root library
- one visible node per external family
- if multiple weak edges point to the same collapsed external, aggregate them

### `raw`
- do not collapse unless technical limits force it

## Low-Value Modules

In `engineering`, collapse modules when all of the following are true:

- low score
- leaf status
- same internal group
- no cross-boundary relevance
- not the focus
- not in the priority 1-hop neighborhood of the focus

## Issues

- `executive`: panel or footer
- `engineering`: side panel
- `raw`: may enter the graph

---

## Discard Order

Discard in this order:

1. issues
2. externals
3. self-loops
4. islands
5. low-score leaves
6. weak intra-group edges
7. lateral focus context
8. nodes below minimum score
9. edges whose endpoints were already discarded

---

## Allowed Exceptions

An otherwise discardable entity may survive if at least one is true:

- it is the focus
- it connects two distinct groups
- it participates in a high-score edge
- it is a real hub
- it explains a bottleneck
- removing it would make the graph misleading

---

## Validation Metrics

Implementation is considered good when it satisfies the following:

### `executive`

- readable without aggressive zoom
- a reader identifies 3 to 5 key zones in under 60 seconds
- the graph does not look like spaghetti

### `engineering`

- key dependencies can be followed without confusion
- the focus tells a clear story
- externals do not dominate the scene

### `raw`

- remains exhaustive
- preserves mental compatibility with the raw dependency graph

---

## Recommended Implementation Order

### Phase 1
Create the formal preset configuration model.

### Phase 2
Compute `node_score` and `edge_score`.

### Phase 3
Apply discard and collapse rules.

### Phase 4
Move `issues` out of the main canvas except in `raw`.

### Phase 5
Pass only the visible graph to the existing layout layer.

### Phase 6
Tune thresholds using three real repositories and compare readability.

---

## Non-Negotiable Rule

If a visual improvement requires showing more noise just to look impressive, reject it.

Priority order:

1. useful truth
2. readability
3. consistency
4. aesthetics

---

## Final Decision

The correct immediate implementation step is to add an explicit **preset-driven visibility filtering layer** with deterministic thresholds per preset before layout.

Not the theme.
Not the glow.
Not more ornaments.

First, reduce the monster.
