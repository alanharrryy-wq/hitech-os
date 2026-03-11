# 42_ARCHITECTURE_ARTIFACTS

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation, Reviewers
- Scope: Architecture evidence package for Live Scene Composer boundaries and dependencies

---

## Purpose

This document explains the architecture artifacts package located at:

- `docs/live-scene-composer/architecture-artifacts/`

The package provides a practical evidence layer that complements architecture policy docs with graph and JSON artifacts suitable for both human review and machine tooling.

---

## What the Package Contains

Core files:

- `README.md`
- `GRAPH_LEGEND.md`
- `live-scene-composer-architecture-boundaries.dot`
- `live-scene-composer-architecture-deps.dot`
- `dependency-inventory.json`
- `protected-nodes-map.json`
- `ARTIFACT_MANIFEST.json`

Optional rendered files when Graphviz is available:

- `live-scene-composer-architecture-boundaries.svg`
- `live-scene-composer-architecture-deps.svg`

---

## Why There Are Two Main Graphs

### Strategic boundaries graph

`live-scene-composer-architecture-boundaries.dot`

This graph is intentionally compact and answers:

- what the top-level boundaries are
- what is shared infrastructure
- where writes are allowed
- what is forbidden

### Tactical dependencies graph

`live-scene-composer-architecture-deps.dot`

This graph captures practical engineering seams:

- protected nodes
- adapter boundaries
- bridge-governed write paths
- suspicious/questionable couplings

Both are required. One gives clarity at policy level; the other supports day-to-day implementation and review.

---

## How to Regenerate

From repository root:

```bash
python tools/live-scene-composer/generate_architecture_artifacts.py --repo-root . --output-dir docs/live-scene-composer/architecture-artifacts
```

Helper wrappers:

```bash
tools/live-scene-composer/generate_architecture_artifacts.sh .
```

```bat
tools\live-scene-composer\generate_architecture_artifacts.bat .
```

The generator scans architecture-relevant boundaries and imports, then rebuilds:

- `.dot` graphs
- `dependency-inventory.json`
- `protected-nodes-map.json`
- `ARTIFACT_MANIFEST.json`
- `.svg` renders when `dot` is available

---

## How to Interpret the Artifacts

- Use `GRAPH_LEGEND.md` for notation.
- Treat `forbidden` edges as architecture defects.
- Treat `questionable` edges as review-required.
- Treat `write-path` edges as high-governance seams.
- If code and artifacts diverge, update artifacts in the same change set where possible.

---

## Inventory and Protected Maps

`dependency-inventory.json`:

- summarizes architecture-relevant edges
- includes code evidence where observed
- marks policy-only edges where architecture requires a seam not yet instantiated

`protected-nodes-map.json`:

- lists high-impact seams
- explains why each is protected
- defines minimum validation and review expectations

---

## Maintenance Rule

When changing boundary wiring, bridge contracts, protected seams, or dependency policy:

1. regenerate architecture artifacts
2. update this document if interpretation changes
3. ensure `README.md`, `00_TOC.md`, and `00_READING_PATHS.md` still point to this package
