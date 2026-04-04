#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Patch de paridad visual "Code Atlas" para el browser/content picker.
Objetivo: quitar el look negro/cian feo y empujar el shared pyside6_glass
hacia el mismo lenguaje de shell/cards/inputs/backdrop que usa code-atlas.

Ruta default:
    F:\repos\hitech-os

Uso:
    python patch_browse_content_code_atlas_parity.py
    python patch_browse_content_code_atlas_parity.py --root "F:\repos\hitech-os"

El script:
- crea backups *.bak_code_atlas_parity
- aplica reemplazos conservadores
- falla si no encuentra anchors clave
"""

from __future__ import annotations

import argparse
import py_compile
import shutil
import sys
from pathlib import Path


BACKUP_SUFFIX = ".bak_code_atlas_parity"


class PatchError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def ensure_backup(path: Path) -> None:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if not backup.exists():
        shutil.copy2(path, backup)


def apply_exact_map(text: str, replacements: dict[str, str], *, label: str) -> tuple[str, int]:
    count = 0
    already = 0
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            count += 1
        elif new in text:
            already += 1
    if count == 0 and already == 0:
        raise PatchError(f"No expected anchors found while patching {label}.")
    return text, count


THEME_REPLACEMENTS = {
    # base silver palette closer to clean glass, not black pit
    'shell_top="rgba(13, 14, 18, 0.9)"': 'shell_top="rgba(255, 255, 255, 0.16)"',
    'shell_bottom="rgba(7, 8, 11, 0.93)"': 'shell_bottom="rgba(220, 226, 233, 0.18)"',
    'input_bg="rgba(5, 6, 10, 0.56)"': 'input_bg="rgba(255, 255, 255, 0.08)"',
    'progress_bg="rgba(5, 6, 10, 0.76)"': 'progress_bg="rgba(207, 214, 222, 0.20)"',
    'tab_bg="rgba(15, 18, 24, 0.48)"': 'tab_bg="rgba(255, 255, 255, 0.08)"',
    'tab_active_bg="rgba(140, 235, 255, 0.16)"': 'tab_active_bg="rgba(255, 255, 255, 0.16)"',
    'tab_hold_bg="rgba(140, 235, 255, 0.10)"': 'tab_hold_bg="rgba(244, 247, 251, 0.16)"',
    'tab_pending_bg="rgba(140, 235, 255, 0.08)"': 'tab_pending_bg="rgba(236, 240, 245, 0.16)"',
    'tab_warning_bg="rgba(255, 208, 122, 0.12)"': 'tab_warning_bg="rgba(232, 236, 241, 0.18)"',
    'tab_border="rgba(140, 235, 255, 0.24)"': 'tab_border="rgba(255, 255, 255, 0.22)"',
    'button_top="rgba(140, 235, 255, 0.12)"': 'button_top="rgba(255, 255, 255, 0.10)"',
    'button_bottom="rgba(140, 235, 255, 0.06)"': 'button_bottom="rgba(225, 231, 238, 0.10)"',
    'button_border="rgba(140, 235, 255, 0.20)"': 'button_border="rgba(255, 255, 255, 0.22)"',
    'input_border="rgba(140, 235, 255, 0.16)"': 'input_border="rgba(255, 255, 255, 0.18)"',
    'input_border_hover="rgba(140, 235, 255, 0.30)"': 'input_border_hover="rgba(255, 255, 255, 0.30)"',
    'accent_soft="rgba(140, 235, 255, 0.16)"': 'accent_soft="rgba(255, 255, 255, 0.16)"',
    'panel_form_border="rgba(140, 235, 255, 0.18)"': 'panel_form_border="rgba(255, 255, 255, 0.18)"',
    'panel_data_border="rgba(140, 235, 255, 0.18)"': 'panel_data_border="rgba(245, 248, 252, 0.18)"',
    'panel_metrics_border="rgba(140, 235, 255, 0.18)"': 'panel_metrics_border="rgba(239, 243, 247, 0.18)"',
    'panel_detail_border="rgba(140, 235, 255, 0.18)"': 'panel_detail_border="rgba(233, 237, 242, 0.18)"',
    'panel_summary_border="rgba(140, 235, 255, 0.18)"': 'panel_summary_border="rgba(244, 247, 251, 0.18)"',
    'panel_aux_border="rgba(140, 235, 255, 0.18)"': 'panel_aux_border="rgba(255, 255, 255, 0.18)"',

    # stylesheet hardcoded cyan -> silver
    'rgba(140, 235, 255, 0.14)': 'rgba(255, 255, 255, 0.16)',
    'rgba(140, 235, 255, 0.24)': 'rgba(255, 255, 255, 0.28)',
    'rgba(140, 235, 255, 0.12)': 'rgba(255, 255, 255, 0.14)',
    'rgba(140, 235, 255, 0.16)': 'rgba(255, 255, 255, 0.18)',
    'rgba(140, 235, 255, 0.18)': 'rgba(255, 255, 255, 0.20)',
    'rgba(140, 235, 255, 0.20)': 'rgba(255, 255, 255, 0.22)',
    'rgba(140, 235, 255, 0.28)': 'rgba(255, 255, 255, 0.30)',
    'rgba(140, 235, 255, 0.30)': 'rgba(255, 255, 255, 0.32)',
    'rgba(140, 235, 255, 0.36)': 'rgba(255, 255, 255, 0.36)',
    'rgba(140, 235, 255, 0.44)': 'rgba(255, 255, 255, 0.40)',
    '#8cefff': '#f5f7fa',
}


ATLAS_BRIDGE_REPLACEMENTS = {
    'canvas_top = _qcolor_from_value("#04070d", 1.0)': 'canvas_top = _qcolor_from_value("#f6f8fb", 1.0)',
    'canvas_bottom = _qcolor_from_value("#0f1824", 1.0)': 'canvas_bottom = _qcolor_from_value("#d9dee5", 1.0)',
    'wash = _qcolor_from_value("#eef6ff", 0.022 if selector_variant else 0.028)': 'wash = _qcolor_from_value("#ffffff", 0.18 if selector_variant else 0.22)',
    'border = _qcolor_from_value("#e8f6ff", 0.20 if selector_variant else 0.16)': 'border = _qcolor_from_value("#ffffff", 0.26 if selector_variant else 0.22)',
    'line = _qcolor_from_value("#8cefff", 0.05)': 'line = _qcolor_from_value("#ffffff", 0.12)',
    'sheen = _qcolor_from_value("#ffffff", 0.08)': 'sheen = _qcolor_from_value("#ffffff", 0.22)',
    'orb_a = _qcolor_from_value("#eff7ff", 0.18 if selector_variant else 0.14)': 'orb_a = _qcolor_from_value("#ffffff", 0.16 if selector_variant else 0.12)',
    'orb_b = _qcolor_from_value("#8cefff", 0.15 if selector_variant else 0.12)': 'orb_b = _qcolor_from_value("#eef2f6", 0.14 if selector_variant else 0.10)',
    'orb_c = _qcolor_from_value("#d7e1ff", 0.10 if selector_variant else 0.08)': 'orb_c = _qcolor_from_value("#d9dee5", 0.12 if selector_variant else 0.09)',
    'star_soft = _qcolor_from_value("#eef6ff", 0.18)': 'star_soft = _qcolor_from_value("#ffffff", 0.20)',
    'star_bright = _qcolor_from_value("#ffffff", 0.62)': 'star_bright = _qcolor_from_value("#ffffff", 0.72)',
    'top_wash.setColorAt(0.38, QColor(156, 224, 255, 8))': 'top_wash.setColorAt(0.38, QColor(255, 255, 255, 10))',
    'color=QColor(140, 239, 255, 26 if self._variant == \'selector\' else 18),': 'color=QColor(255, 255, 255, 18 if self._variant == \'selector\' else 12),',
    'vignette.setColorAt(1.0, QColor(0, 0, 0, 76 if self._variant == \'selector\' else 58))': 'vignette.setColorAt(1.0, QColor(185, 192, 200, 22 if self._variant == \'selector\' else 14))',
}


BACKDROP_REPLACEMENTS = dict(ATLAS_BRIDGE_REPLACEMENTS)


ATLAS_STYLES_REPLACEMENTS = {
    'background: rgba(12, 21, 32, 0.20);': 'background: rgba(255, 255, 255, 0.08);',
    'background: rgba(12, 21, 32, 0.44);': 'background: rgba(255, 255, 255, 0.14);',
    'border: 1px solid rgba(140, 235, 255, 0.18);': 'border: 1px solid rgba(255, 255, 255, 0.22);',
    'border: 1px solid rgba(140, 235, 255, 0.30);': 'border: 1px solid rgba(255, 255, 255, 0.32);',
    'color: #8cefff;': 'color: #f5f7fa;',
}

CATALOG_SHELL_REPLACEMENTS = {
    'rgba(140, 235, 255,': 'rgba(255, 255, 255,',
    'background: rgba(12, 21, 32, 0.44);': 'background: rgba(255, 255, 255, 0.10);',
    'background: rgba(18, 25, 39, 0.75);': 'background: rgba(255, 255, 255, 0.09);',
    'background: rgba(5, 6, 10, 0.56);': 'background: rgba(255, 255, 255, 0.08);',
}

DEMO_APP_REPLACEMENTS = {
    'background: rgba(12, 21, 32, 0.44);': 'background: rgba(255, 255, 255, 0.14);',
    'rgba(140, 235, 255,': 'rgba(255, 255, 255,',
}

COMPOSITIONS_REPLACEMENTS = {
    'obsidian_ice': 'silver_frost_cyan',
}


def patch_file(path: Path, replacements: dict[str, str], *, label: str) -> int:
    text = read_text(path)
    new_text, count = apply_exact_map(text, replacements, label=label)
    if new_text != text:
        ensure_backup(path)
        write_text(path, new_text)
    return count


def compile_check(paths: list[Path]) -> None:
    for path in paths:
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=r"F:\repos\hitech-os")
    args = parser.parse_args()

    root = Path(args.root)
    base = root / "forgeos" / "shared" / "pyside6_glass"

    targets = {
        "theme.py": (base / "theme.py", THEME_REPLACEMENTS),
        "atlas_theme_bridge.py": (base / "atlas_theme_bridge.py", ATLAS_BRIDGE_REPLACEMENTS),
        "backdrop.py": (base / "backdrop.py", BACKDROP_REPLACEMENTS),
        "atlas_styles.py": (base / "atlas_styles.py", ATLAS_STYLES_REPLACEMENTS),
        "examples\\catalog_shell.py": (base / "examples" / "catalog_shell.py", CATALOG_SHELL_REPLACEMENTS),
        "examples\\demo_app.py": (base / "examples" / "demo_app.py", DEMO_APP_REPLACEMENTS),
        "examples\\compositions.py": (base / "examples" / "compositions.py", COMPOSITIONS_REPLACEMENTS),
    }

    missing = [str(path) for path, _ in targets.values() if not path.exists()]
    if missing:
        raise PatchError("Missing expected files:\n- " + "\n- ".join(missing))

    results: list[tuple[str, int]] = []
    patched_paths: list[Path] = []

    for label, (path, replacements) in targets.items():
        count = patch_file(path, replacements, label=label)
        results.append((label, count))
        patched_paths.append(path)

    compile_check(patched_paths)

    print(f"[APPLIED] Code Atlas parity patch finished for: {base}")
    for label, count in results:
        print(f"  - {label} ({count} substitutions)")
    print(f"[INFO] Backup suffix: {BACKUP_SUFFIX}")
    print("[NOTE] This patch pushes Browse Content toward Code Atlas glass parity.")
    print("[NOTE] If a specific widget still paints itself inline, it will need a second surgical patch.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PatchError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(2)
