from __future__ import annotations

from capatch_cartridges.registry import load_builtin_cartridges, resolve_cartridge_stack
from capatch_intent.surface_detection import detect_surfaces_for_paths


def test_builtin_cartridges_resolve_visual_stack() -> None:
    registry = load_builtin_cartridges()
    stack = resolve_cartridge_stack(['prisma-tablet'], registry)
    ids = [item.cartridge_id for item in stack]
    assert 'external-output' in ids
    assert 'generic-code' in ids
    assert 'react-ui' in ids
    assert 'visual-premium' in ids
    assert 'prisma-authority' in ids
    assert 'prisma-tablet' in ids


def test_surface_detection_for_tablet_ui() -> None:
    surfaces = detect_surfaces_for_paths(['products/tablet/app/components/pos/checkout.tsx'])
    assert 'prisma-tablet' in surfaces
    assert 'react-ui' in surfaces
    assert 'visual' in surfaces
