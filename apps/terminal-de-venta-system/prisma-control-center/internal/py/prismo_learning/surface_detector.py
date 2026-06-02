# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Surface detection from paths, names and text snippets."""
from __future__ import annotations
from typing import Iterable

SURFACES = ["control_center", "prismo", "pc", "tablet", "mobile", "pos", "chart_lab", "sync", "visual_os"]
SURFACE_HINTS = {
    "control_center": ["control-center", "control center", "panel_3150", "3150"],
    "prismo": ["prismo", "adaptive intelligence", "authority brain"],
    "pc": ["pc", "backoffice", "3130"],
    "tablet": ["tablet", "3120", "pos tablet"],
    "mobile": ["mobile", "3140"],
    "pos": ["pos", "terminal", "cash", "sales"],
    "chart_lab": ["chart-lab", "chart lab", "echarts", "3000"],
    "sync": ["sync", "outbox", "ingest", "dispatcher", "ack"],
    "visual_os": ["visual-os", "cloudglass", "surface visual"],
}


def detect_surfaces(*chunks: str) -> list[str]:
    text = "\n".join(str(c or "") for c in chunks).lower()
    found: list[str] = []
    for surface, hints in SURFACE_HINTS.items():
        if any(h.lower() in text for h in hints):
            found.append(surface)
    return found or ["unknown"]


def dominant_surface(surfaces: Iterable[str]) -> str:
    seq = [s for s in surfaces if s and s != "unknown"]
    return seq[0] if seq else "unknown"
