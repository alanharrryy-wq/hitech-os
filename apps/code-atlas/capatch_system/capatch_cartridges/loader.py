from __future__ import annotations

from pathlib import Path

from capatch_intent.surface_detection import detect_surfaces_for_paths

from .registry import load_builtin_cartridges, resolve_cartridge_stack


def recommend_cartridges(paths: list[str]) -> list[str]:
    surfaces = detect_surfaces_for_paths(paths)
    stack: list[str] = ['external-output', 'generic-code']
    if 'react-ui' in surfaces:
        stack.append('react-ui')
    if 'visual' in surfaces:
        stack.append('visual-premium')
    if 'prisma-tablet' in surfaces:
        stack.extend(['prisma-authority', 'prisma-tablet'])
    elif 'prisma-pc' in surfaces:
        stack.extend(['prisma-authority', 'prisma-pc'])
    elif 'prisma-mobile' in surfaces:
        stack.extend(['prisma-authority', 'prisma-mobile'])
    return list(dict.fromkeys(stack))


def load_recommended_stack(paths: list[str], base_dir: Path | None = None):
    registry = load_builtin_cartridges(base_dir)
    return resolve_cartridge_stack(recommend_cartridges(paths), registry)
