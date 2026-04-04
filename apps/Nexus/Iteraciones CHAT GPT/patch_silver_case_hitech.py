from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

DEFAULT_ROOT = Path(r"F:\repos\hitech-os\forgeos\shared\pyside6_glass")
BACKUP_SUFFIX = ".bak_silver_case"


class PatchError(RuntimeError):
    pass


RGBA_CYAN_PATTERN = re.compile(r"rgba\(\s*140\s*,\s*235\s*,\s*255\s*,\s*([01](?:\.\d+)?)\s*\)")
RGBA_BLUE_PATTERN = re.compile(r"rgba\(\s*143\s*,\s*188\s*,\s*213\s*,\s*([01](?:\.\d+)?)\s*\)")


SILVER_REPLACEMENTS = {
    'shell_top="rgba(13, 14, 18, 0.9)",': 'shell_top="rgba(78, 80, 86, 0.90)",',
    'shell_bottom="rgba(7, 8, 11, 0.93)",': 'shell_bottom="rgba(54, 56, 61, 0.93)",',
    'shell_border="rgba(245, 248, 252, 0.2)",': 'shell_border="rgba(245, 248, 252, 0.22)",',
    'shell_border_hover="rgba(245, 248, 252, 0.3)",': 'shell_border_hover="rgba(245, 248, 252, 0.34)",',
    'chrome_top="rgba(255, 255, 255, 0.035)",': 'chrome_top="rgba(255, 255, 255, 0.11)",',
    'chrome_bottom="rgba(255, 255, 255, 0.012)",': 'chrome_bottom="rgba(214, 220, 228, 0.06)",',
    'chrome_border="rgba(245, 248, 252, 0.08)",': 'chrome_border="rgba(245, 248, 252, 0.12)",',
    'card_top="rgba(255, 255, 255, 0.032)",': 'card_top="rgba(255, 255, 255, 0.10)",',
    'card_bottom="rgba(255, 255, 255, 0.014)",': 'card_bottom="rgba(216, 221, 228, 0.05)",',
    'card_border="rgba(245, 248, 252, 0.06)",': 'card_border="rgba(245, 248, 252, 0.10)",',
    'text_primary="#e7edf4",': 'text_primary="#f1f4f8",',
    'text_muted="#b5bfcb",': 'text_muted="#c9d0d8",',
    'text_inverse="#081018",': 'text_inverse="#1f2329",',
    'accent="#dfe5ee",': 'accent="#e2e6eb",',
    'accent_soft="rgba(245, 248, 252, 0.07)",': 'accent_soft="rgba(245, 248, 252, 0.10)",',
    'button_top="rgba(255, 255, 255, 0.02)",': 'button_top="rgba(255, 255, 255, 0.08)",',
    'button_bottom="rgba(255, 255, 255, 0.008)",': 'button_bottom="rgba(208, 213, 220, 0.05)",',
    'button_border="rgba(245, 248, 252, 0.10)",': 'button_border="rgba(245, 248, 252, 0.14)",',
    'input_bg="rgba(5, 6, 10, 0.56)",': 'input_bg="rgba(42, 44, 49, 0.58)",',
    'input_border="rgba(245, 248, 252, 0.13)",': 'input_border="rgba(245, 248, 252, 0.16)",',
    'input_border_hover="rgba(245, 248, 252, 0.25)",': 'input_border_hover="rgba(245, 248, 252, 0.28)",',
    'progress_bg="rgba(5, 6, 10, 0.76)",': 'progress_bg="rgba(44, 46, 51, 0.78)",',
    'progress_chunk_top="#d8dfe9",': 'progress_chunk_top="#eceff3",',
    'progress_chunk_bottom="#c2cbd8",': 'progress_chunk_bottom="#d9dfe7",',
    'tab_bg="rgba(255, 255, 255, 0.03)",': 'tab_bg="rgba(255, 255, 255, 0.06)",',
    'tab_active_bg="rgba(255, 255, 255, 0.06)",': 'tab_active_bg="rgba(255, 255, 255, 0.12)",',
    'tab_hold_bg="rgba(255, 255, 255, 0.04)",': 'tab_hold_bg="rgba(255, 255, 255, 0.08)",',
    'tab_border="rgba(245, 248, 252, 0.14)",': 'tab_border="rgba(245, 248, 252, 0.16)",',
    'tab_text="#e8edf4",': 'tab_text="#f2f5f9",',
    'tab_text_muted="#a7b0be",': 'tab_text_muted="#bcc5cf",',
    'panel_form_border="rgba(140, 235, 255, 0.12)",': 'panel_form_border="rgba(245, 248, 252, 0.14)",',
    'panel_data_border="rgba(140, 235, 255, 0.15)",': 'panel_data_border="rgba(245, 248, 252, 0.16)",',
    'panel_metrics_border="rgba(140, 235, 255, 0.14)",': 'panel_metrics_border="rgba(245, 248, 252, 0.15)",',
    'panel_detail_border="rgba(140, 235, 255, 0.16)",': 'panel_detail_border="rgba(245, 248, 252, 0.17)",',
    'panel_summary_border="rgba(140, 235, 255, 0.14)",': 'panel_summary_border="rgba(245, 248, 252, 0.15)",',
    'panel_aux_border="rgba(140, 235, 255, 0.12)",': 'panel_aux_border="rgba(245, 248, 252, 0.14)",',
}

OBSIDIAN_REPLACEMENTS = {
    'shell_top="rgba(21, 29, 44, 0.93)",': 'shell_top="rgba(67, 69, 75, 0.93)",',
    'shell_bottom="rgba(8, 13, 24, 0.95)",': 'shell_bottom="rgba(42, 44, 49, 0.95)",',
    'shell_border="rgba(136, 162, 193, 0.28)",': 'shell_border="rgba(209, 216, 226, 0.28)",',
    'shell_border_hover="rgba(171, 196, 224, 0.40)",': 'shell_border_hover="rgba(229, 234, 240, 0.40)",',
    'chrome_top="rgba(57, 67, 87, 0.34)",': 'chrome_top="rgba(112, 116, 124, 0.26)",',
    'chrome_bottom="rgba(29, 36, 52, 0.31)",': 'chrome_bottom="rgba(74, 77, 84, 0.24)",',
    'chrome_border="rgba(176, 200, 228, 0.19)",': 'chrome_border="rgba(220, 226, 234, 0.20)",',
    'card_top="rgba(63, 74, 95, 0.35)",': 'card_top="rgba(103, 106, 114, 0.24)",',
    'card_bottom="rgba(36, 44, 61, 0.34)",': 'card_bottom="rgba(70, 73, 80, 0.22)",',
    'card_border="rgba(137, 161, 188, 0.24)",': 'card_border="rgba(213, 219, 228, 0.24)",',
    'text_primary="#e4ebf5",': 'text_primary="#eef2f6",',
    'text_muted="#b2bfce",': 'text_muted="#c6ced7",',
    'text_inverse="#0b121c",': 'text_inverse="#1c2025",',
    'accent="#9abdf3",': 'accent="#dde2e8",',
    'accent_soft="rgba(154, 189, 243, 0.24)",': 'accent_soft="rgba(221, 226, 232, 0.20)",',
    'button_top="rgba(117, 153, 214, 0.30)",': 'button_top="rgba(159, 167, 178, 0.18)",',
    'button_bottom="rgba(85, 119, 177, 0.24)",': 'button_bottom="rgba(118, 125, 136, 0.16)",',
    'button_border="rgba(154, 188, 231, 0.34)",': 'button_border="rgba(221, 226, 232, 0.28)",',
    'input_bg="rgba(18, 25, 39, 0.75)",': 'input_bg="rgba(36, 39, 44, 0.74)",',
    'input_border="rgba(126, 149, 177, 0.24)",': 'input_border="rgba(214, 220, 229, 0.24)",',
    'input_border_hover="rgba(155, 181, 214, 0.40)",': 'input_border_hover="rgba(236, 240, 245, 0.36)",',
    'progress_bg="rgba(16, 24, 38, 0.84)",': 'progress_bg="rgba(34, 36, 41, 0.84)",',
    'progress_chunk_top="#9abdf3",': 'progress_chunk_top="#dfe4ea",',
    'progress_chunk_bottom="#84a4d5",': 'progress_chunk_bottom="#cfd6de",',
    'tab_bg="rgba(30, 40, 56, 0.66)",': 'tab_bg="rgba(73, 76, 83, 0.62)",',
    'tab_active_bg="rgba(70, 94, 132, 0.52)",': 'tab_active_bg="rgba(122, 127, 137, 0.42)",',
    'tab_hold_bg="rgba(39, 51, 69, 0.52)",': 'tab_hold_bg="rgba(82, 85, 92, 0.44)",',
    'tab_border="rgba(131, 154, 183, 0.33)",': 'tab_border="rgba(214, 220, 229, 0.30)",',
    'tab_text="#dbe7f7",': 'tab_text="#eef2f6",',
    'tab_text_muted="#a6b4c7",': 'tab_text_muted="#c2cad3",',
    'panel_form_border="rgba(142, 173, 207, 0.35)",': 'panel_form_border="rgba(225, 230, 236, 0.28)",',
    'panel_data_border="rgba(119, 190, 168, 0.30)",': 'panel_data_border="rgba(220, 225, 232, 0.26)",',
    'panel_metrics_border="rgba(217, 181, 126, 0.30)",': 'panel_metrics_border="rgba(220, 225, 232, 0.27)",',
    'panel_detail_border="rgba(178, 155, 218, 0.28)",': 'panel_detail_border="rgba(220, 225, 232, 0.27)",',
    'panel_summary_border="rgba(131, 176, 214, 0.28)",': 'panel_summary_border="rgba(220, 225, 232, 0.27)",',
    'panel_aux_border="rgba(139, 157, 182, 0.26)",': 'panel_aux_border="rgba(214, 220, 229, 0.24)",',
}


ATLAS_THEME_BRIDGE_REPLACEMENTS = {
    '"canvas_bg": _resolve_palette_token(palette, "canvas_bg", _resolve_palette_token(palette, "shell_bottom", "#0f1824"))': '"canvas_bg": _resolve_palette_token(palette, "canvas_bg", _resolve_palette_token(palette, "shell_bottom", "#3d4046"))',
    '"header_fill": _resolve_palette_token(palette, "header_fill", _resolve_palette_token(palette, "shell_top", "#1a2836"))': '"header_fill": _resolve_palette_token(palette, "header_fill", _resolve_palette_token(palette, "shell_top", "#51545b"))',
    '"legend_fill": _resolve_palette_token(palette, "legend_fill", _resolve_palette_token(palette, "card_top", "#1f2f42"))': '"legend_fill": _resolve_palette_token(palette, "legend_fill", _resolve_palette_token(palette, "card_top", "#676b73"))',
    '"focus": _resolve_palette_token(palette, "focus", _resolve_palette_token(palette, "accent", "#7dd3fc"))': '"focus": _resolve_palette_token(palette, "focus", _resolve_palette_token(palette, "accent", "#e2e6eb"))',
    '"legend_stroke": _resolve_palette_token(palette, "legend_stroke", _resolve_palette_token(palette, "card_border", "#d5e2f4"))': '"legend_stroke": _resolve_palette_token(palette, "legend_stroke", _resolve_palette_token(palette, "card_border", "#e7ebf0"))',
    '"header_stroke": _resolve_palette_token(palette, "header_stroke", _resolve_palette_token(palette, "shell_border", "#d5e2f4"))': '"header_stroke": _resolve_palette_token(palette, "header_stroke", _resolve_palette_token(palette, "shell_border", "#e7ebf0"))',
    '"halo_a": _resolve_palette_token(palette, "halo_a", _resolve_palette_token(palette, "accent", "#22d3ee"))': '"halo_a": _resolve_palette_token(palette, "halo_a", _resolve_palette_token(palette, "accent", "#f2f4f7"))',
    '"halo_b": _resolve_palette_token(palette, "halo_b", _resolve_palette_token(palette, "button_border", "#8b5cf6"))': '"halo_b": _resolve_palette_token(palette, "halo_b", _resolve_palette_token(palette, "button_border", "#d8dde5"))',
    'canvas_top = _qcolor_from_value("#04070d", 1.0)': 'canvas_top = _qcolor_from_value("#51545b", 1.0)',
    'canvas_bottom = _qcolor_from_value("#0f1824", 1.0)': 'canvas_bottom = _qcolor_from_value("#3d4046", 1.0)',
    'wash = _qcolor_from_value("#eef6ff", 0.022 if selector_variant else 0.028)': 'wash = _qcolor_from_value("#ffffff", 0.050 if selector_variant else 0.066)',
    'border = _qcolor_from_value("#e8f6ff", 0.20 if selector_variant else 0.16)': 'border = _qcolor_from_value("#f2f5f8", 0.24 if selector_variant else 0.20)',
    'line = _qcolor_from_value("#8cefff", 0.05)': 'line = _qcolor_from_value("#d7dce4", 0.10)',
    'sheen = _qcolor_from_value("#ffffff", 0.08)': 'sheen = _qcolor_from_value("#ffffff", 0.14)',
    'orb_a = _qcolor_from_value("#eff7ff", 0.18 if selector_variant else 0.14)': 'orb_a = _qcolor_from_value("#f4f6f8", 0.20 if selector_variant else 0.16)',
    'orb_b = _qcolor_from_value("#8cefff", 0.15 if selector_variant else 0.12)': 'orb_b = _qcolor_from_value("#d7dce4", 0.16 if selector_variant else 0.12)',
    'orb_c = _qcolor_from_value("#d7e1ff", 0.10 if selector_variant else 0.08)': 'orb_c = _qcolor_from_value("#c7ccd4", 0.12 if selector_variant else 0.09)',
    'sparkle = _qcolor_from_value("#ffffff", 0.88)': 'sparkle = _qcolor_from_value("#ffffff", 0.82)',
    'star_soft = _qcolor_from_value("#eef6ff", 0.18)': 'star_soft = _qcolor_from_value("#f4f6f8", 0.22)',
    'star_bright = _qcolor_from_value("#ffffff", 0.62)': 'star_bright = _qcolor_from_value("#ffffff", 0.56)',
}


BACKDROP_REPLACEMENTS = {
    'canvas_top=_qcolor_from_value("#04070d", 1.0),': 'canvas_top=_qcolor_from_value("#51545b", 1.0),',
    'canvas_bottom=_qcolor_from_value("#0f1824", 1.0),': 'canvas_bottom=_qcolor_from_value("#3d4046", 1.0),',
    'wash=_qcolor_from_value("#eef6ff", 0.022 if selector_variant else 0.028),': 'wash=_qcolor_from_value("#ffffff", 0.050 if selector_variant else 0.066),',
    'border=_qcolor_from_value("#e8f6ff", 0.20 if selector_variant else 0.16),': 'border=_qcolor_from_value("#f2f5f8", 0.24 if selector_variant else 0.20),',
    'line=_qcolor_from_value("#8cefff", 0.05),': 'line=_qcolor_from_value("#d7dce4", 0.10),',
    'sheen=_qcolor_from_value("#ffffff", 0.08),': 'sheen=_qcolor_from_value("#ffffff", 0.14),',
    'orb_a=_qcolor_from_value("#eff7ff", 0.18 if selector_variant else 0.14),': 'orb_a=_qcolor_from_value("#f4f6f8", 0.20 if selector_variant else 0.16),',
    'orb_b=_qcolor_from_value("#8cefff", 0.15 if selector_variant else 0.12),': 'orb_b=_qcolor_from_value("#d7dce4", 0.16 if selector_variant else 0.12),',
    'orb_c=_qcolor_from_value("#d7e1ff", 0.10 if selector_variant else 0.08),': 'orb_c=_qcolor_from_value("#c7ccd4", 0.12 if selector_variant else 0.09),',
    'sparkle=_qcolor_from_value("#ffffff", 0.88),': 'sparkle=_qcolor_from_value("#ffffff", 0.82),',
    'star_soft=_qcolor_from_value("#eef6ff", 0.18),': 'star_soft=_qcolor_from_value("#f4f6f8", 0.22),',
    'star_bright=_qcolor_from_value("#ffffff", 0.62),': 'star_bright=_qcolor_from_value("#ffffff", 0.56),',
    'vignette.setColorAt(1.0, QColor(0, 0, 0, 76 if self._variant == "selector" else 58))': 'vignette.setColorAt(1.0, QColor(38, 40, 45, 58 if self._variant == "selector" else 42))',
}


ATLAS_STYLES_REPLACEMENTS = {
    'background: rgba(12, 21, 32, 0.20);': 'background: rgba(255, 255, 255, 0.08);',
}


DEMO_APP_REPLACEMENTS = {
    'color: #dce8f3;': 'color: #eef2f6;',
    'color: #8cbcd5;': 'color: #d8dee6;',
    'color: #ebf4ff;': 'color: #f5f7fa;',
    'background: rgba(12, 21, 32, 0.44);': 'background: rgba(255, 255, 255, 0.08);',
}


CATALOG_SHELL_REPLACEMENTS = {
    'color: rgba(244, 247, 252, 0.95);': 'color: rgba(247, 249, 252, 0.95);',
}


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
    already_applied = 0
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            count += 1
        elif new in text:
            already_applied += 1
    if count == 0 and already_applied == 0:
        raise PatchError(f"No expected anchors found while patching {label}.")
    return text, count



def replace_pattern(text: str, pattern: re.Pattern[str], repl: str) -> tuple[str, int]:
    return pattern.subn(repl, text)



def patch_theme_py(text: str) -> tuple[str, int]:
    total = 0
    text, count = apply_exact_map(text, SILVER_REPLACEMENTS, label="theme.py silver palette")
    total += count
    text, count = apply_exact_map(text, OBSIDIAN_REPLACEMENTS, label="theme.py obsidian palette")
    total += count
    text, count = replace_pattern(text, RGBA_CYAN_PATTERN, r"rgba(245, 248, 252, \1)")
    total += count
    if "rgba(0, 0, 0, 0.0)" in text:
        text = text.replace("rgba(0, 0, 0, 0.0)", "transparent")
        total += 1
    return text, total



def patch_atlas_theme_bridge(text: str) -> tuple[str, int]:
    return apply_exact_map(text, ATLAS_THEME_BRIDGE_REPLACEMENTS, label="atlas_theme_bridge.py")



def patch_backdrop(text: str) -> tuple[str, int]:
    return apply_exact_map(text, BACKDROP_REPLACEMENTS, label="backdrop.py")



def patch_atlas_styles(text: str) -> tuple[str, int]:
    total = 0
    text, count = apply_exact_map(text, ATLAS_STYLES_REPLACEMENTS, label="atlas_styles.py")
    total += count
    text, count = replace_pattern(text, RGBA_CYAN_PATTERN, r"rgba(245, 248, 252, \1)")
    total += count
    return text, total



def patch_demo_app(text: str) -> tuple[str, int]:
    total = 0
    text, count = apply_exact_map(text, DEMO_APP_REPLACEMENTS, label="examples/demo_app.py")
    total += count
    text, count = replace_pattern(text, RGBA_BLUE_PATTERN, r"rgba(245, 248, 252, \1)")
    total += count
    return text, total



def patch_catalog_shell(text: str) -> tuple[str, int]:
    total = 0
    text, count = apply_exact_map(text, CATALOG_SHELL_REPLACEMENTS, label="examples/catalog_shell.py")
    total += count
    text, count = replace_pattern(text, RGBA_CYAN_PATTERN, r"rgba(245, 248, 252, \1)")
    total += count
    return text, total


PATCHERS = {
    Path("theme.py"): patch_theme_py,
    Path("atlas_theme_bridge.py"): patch_atlas_theme_bridge,
    Path("backdrop.py"): patch_backdrop,
    Path("atlas_styles.py"): patch_atlas_styles,
    Path("examples/demo_app.py"): patch_demo_app,
    Path("examples/catalog_shell.py"): patch_catalog_shell,
}



def patch_file(root: Path, relative: Path, dry_run: bool) -> tuple[bool, int]:
    path = root / relative
    if not path.exists():
        return False, 0
    original = read_text(path)
    updated, change_count = PATCHERS[relative](original)
    changed = updated != original
    if changed and not dry_run:
        ensure_backup(path)
        write_text(path, updated)
    return changed, change_count



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replicate the silver case across the app and remove blue/black object backgrounds.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help=f"Project root. Default: {DEFAULT_ROOT}")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files.")
    return parser.parse_args()



def main() -> int:
    args = parse_args()
    root = args.root.expanduser()
    if not root.exists():
        print(f"[ERROR] Project root not found: {root}")
        return 2

    touched: list[tuple[str, int]] = []
    skipped: list[str] = []

    for relative in PATCHERS:
        try:
            changed, change_count = patch_file(root, relative, args.dry_run)
        except PatchError as exc:
            print(f"[ERROR] {exc}")
            return 3
        if changed:
            touched.append((str(relative), change_count))
        else:
            skipped.append(str(relative))

    if not touched:
        print("[OK] No new edits were needed. The patch looks already applied.")
        if skipped:
            print("[INFO] Reviewed:")
            for item in skipped:
                print(f"  - {item}")
        return 0

    mode = "DRY RUN" if args.dry_run else "APPLIED"
    print(f"[{mode}] Silver case patch finished for: {root}")
    for relative, change_count in touched:
        print(f"  - {relative} ({change_count} substitutions)")
    if skipped:
        print("[INFO] Unchanged:")
        for item in skipped:
            print(f"  - {item}")
    print(f"[INFO] Backup suffix: {BACKUP_SUFFIX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
