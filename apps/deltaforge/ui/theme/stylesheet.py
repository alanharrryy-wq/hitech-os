from __future__ import annotations

from dataclasses import dataclass
import sys
from pathlib import Path

from .theme_api import ThemeSpec, resolve_theme

_REPO_ROOT = Path(__file__).resolve().parents[4]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)

from forgeos.shared.pyside6_glass.theme import (
    build_stylesheet as build_shared_glass_stylesheet,
)


@dataclass(frozen=True)
class StyleFragments:
    shell: str
    command_bar: str
    tab_bar: str
    surface: str
    input_field: str
    button_primary: str
    button_secondary: str
    status_chip: str
    text_area: str


def _pick(theme: ThemeSpec, *names: str, default: str) -> str:
    for name in names:
        value = theme.roles.get(name)
        if isinstance(value, str) and value.strip():
            return value
        value = theme.tokens.get(name)
        if isinstance(value, str) and value.strip():
            return value
    return default


def build_fragments(theme_name: str = 'dark') -> StyleFragments:
    theme = resolve_theme(theme_name)
    bg = _pick(theme, 'window_bg', 'canvas_bg', default='#11141a')
    surface = _pick(theme, 'surface_bg', 'panel_bg', default='#171b23')
    elevated = _pick(theme, 'surface_elevated', 'panel_bg_elevated', default='#1d2330')
    border = _pick(theme, 'border_default', 'stroke', default='#2d3646')
    text = _pick(theme, 'text_primary', 'fg', default='#eef2ff')
    text_muted = _pick(theme, 'text_muted', 'muted_text', default='#96a0b5')
    accent = _pick(theme, 'accent', 'focus', default='#5d88ff')
    accent_text = _pick(theme, 'accent_text', default='#08111f')
    warning = _pick(theme, 'warning', default='#f6c86e')
    danger = _pick(theme, 'danger', default='#ff7d7d')
    success = _pick(theme, 'success', default='#73d6ad')
    input_bg = _pick(theme, 'input_bg', 'base_bg', default='#10151d')

    return StyleFragments(
        shell=f"""
        QWidget#DeltaForgeShell {{
            background: {bg};
            color: {text};
        }}
        QMainWindow#DeltaForgeMainWindow {{
            background: {bg};
        }}
        QSplitter::handle {{
            background: {border};
            width: 1px;
            height: 1px;
        }}
        """,
        command_bar=f"""
        QWidget[role="command-bar"] {{
            background: transparent;
            border: none;
        }}
        """,
        tab_bar=f"""
        QWidget[role="session-tabs"] {{
            background: transparent;
        }}
        QWidget[role="session-tabs"] QTabBar::tab {{
            background: {surface};
            color: {text_muted};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 8px 12px;
            margin-right: 6px;
        }}
        QWidget[role="session-tabs"] QTabBar::tab:selected {{
            background: {elevated};
            color: {text};
            border-color: {accent};
        }}
        QWidget[role="session-tabs"] QTabBar::tab:hover {{
            color: {text};
        }}
        """,
        surface=f"""
        QFrame[role="surface"] {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 16px;
        }}
        QLabel[role="surface-title"] {{
            color: {text};
            font-size: 14px;
            font-weight: 700;
        }}
        QLabel[role="surface-meta"] {{
            color: {text_muted};
            font-size: 11px;
        }}
        """,
        input_field=f"""
        QLineEdit, QTextEdit, QPlainTextEdit, QListWidget, QTreeWidget {{
            background: {input_bg};
            border: 1px solid {border};
            border-radius: 12px;
            color: {text};
            padding: 8px;
            selection-background-color: {accent};
            selection-color: {accent_text};
        }}
        """,
        button_primary=f"""
        QPushButton[kind="primary"] {{
            background: {accent};
            color: {accent_text};
            border: 1px solid {accent};
            border-radius: 12px;
            padding: 8px 12px;
            font-weight: 700;
        }}
        QPushButton[kind="primary"]:disabled {{
            opacity: 0.6;
        }}
        """,
        button_secondary=f"""
        QPushButton[kind="secondary"], QPushButton[kind="ghost"] {{
            background: {surface};
            color: {text};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 8px 12px;
        }}
        QPushButton[kind="ghost"] {{
            background: transparent;
        }}
        """,
        status_chip=f"""
        QLabel[role="status-chip"] {{
            border-radius: 10px;
            padding: 4px 10px;
            background: {elevated};
            border: 1px solid {border};
            color: {text};
        }}
        QLabel[tone="accent"] {{ border-color: {accent}; }}
        QLabel[tone="warning"] {{ border-color: {warning}; }}
        QLabel[tone="danger"] {{ border-color: {danger}; }}
        QLabel[tone="success"] {{ border-color: {success}; }}
        """,
        text_area=f"""
        QTextBrowser, QTextEdit[readonly="true"], QPlainTextEdit[readonly="true"] {{
            background: {input_bg};
            border: 1px solid {border};
            border-radius: 12px;
            color: {text};
            padding: 10px;
        }}
        """,
    )


def build_stylesheet(theme_name: str = 'dark') -> str:
    fragments = build_fragments(theme_name)
    local_styles = "\n".join(
        [
            fragments.shell,
            fragments.command_bar,
            fragments.tab_bar,
            fragments.surface,
            fragments.input_field,
            fragments.button_primary,
            fragments.button_secondary,
            fragments.status_chip,
            fragments.text_area,
        ]
    )
    # Shared visual base first, tool-specific stylesheet second for parity-safe overrides.
    return f"{build_shared_glass_stylesheet('silver_frost_cyan')}\n{local_styles}"
