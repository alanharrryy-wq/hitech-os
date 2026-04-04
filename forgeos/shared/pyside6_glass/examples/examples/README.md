# Glass Workbench and Examples

This folder now ships **two primary visual entry points** for `pyside6_glass`:

- `catalog`: the original registry-driven workbench for browsing compositions, primitives, dashboards, data probes, and editor tools.
- `showcase`: a new **premium command-center shell** meant to look far more flagship out of the box.

## Launch

Legacy catalog:

```bash
python -m forgeos.shared.pyside6_glass.examples --mode catalog
```

New premium showcase:

```bash
python -m forgeos.shared.pyside6_glass.examples --mode showcase
```

Other modes remain available:

```bash
python -m forgeos.shared.pyside6_glass.examples --mode integration
python -m forgeos.shared.pyside6_glass.examples --mode smoke
python -m forgeos.shared.pyside6_glass.examples --mode proof
```

## What the showcase is trying to prove

The showcase is intentionally biased toward a stronger first impression:

- command-center shell instead of picker-first workbench
- hero panel + live command feed + telemetry plot + operator queue
- actual story about runtime context, orchestration, token resolution, and release gating
- optional use of local extras when present:
  - `pyqtgraph` for the telemetry panel
  - `qtawesome` for richer toolbar icons

If those extras are missing, the UI degrades gracefully and still runs.

## Why keep both

The catalog is still the better tool for framework exploration and extension.
The showcase is the better answer to:

> "Can this thing open and already feel premium?"

Use the catalog to inspect capabilities.
Use the showcase to sell the vibe.
