from __future__ import annotations

from ui.theme.tokens import ThemeTokens


def build_app_stylesheet(theme: ThemeTokens) -> str:
    c = theme.colors
    r = theme.radius
    t = theme.typography

    return f"""
    QMainWindow {{
        background: {c['canvas']};
        color: {c['text']};
    }}

    QFrame#MainShell {{
        background: {c['shell']};
        border: 1px solid {c['hairline']};
        border-radius: {r['xl']}px;
    }}

    QFrame[card="section"] {{
        background: {c['panel']};
        border: 1px solid {c['hairline']};
        border-radius: {r['lg']}px;
    }}

    QFrame[card="section_alt"] {{
        background: {c['panel_alt']};
        border: 1px solid {c['hairline']};
        border-radius: {r['lg']}px;
    }}

    QLabel[role="title"] {{
        color: {c['text']};
        font-size: {t['title']}px;
        font-weight: 700;
    }}

    QLabel[role="subtitle"] {{
        color: {c['text_soft']};
        font-size: {t['subtitle']}px;
    }}

    QLabel[role="field"] {{
        color: {c['focus']};
        font-size: {t['small']}px;
        font-weight: 700;
        letter-spacing: 0.6px;
    }}

    QLabel[role="hint"] {{
        color: {c['text_muted']};
        font-size: {t['small']}px;
    }}

    QLabel[role="mono"] {{
        color: {c['text_soft']};
        font-size: {t['mono']}px;
        font-family: "Cascadia Code", "Consolas", monospace;
    }}

    QLineEdit, QPlainTextEdit, QListWidget, QTreeWidget, QTextEdit {{
        background: {c['mono_bg']};
        color: {c['text']};
        border: 1px solid {c['hairline']};
        border-radius: {r['md']}px;
        selection-background-color: {c['focus']};
        selection-color: #081119;
    }}

    QTabWidget::pane {{
        border: 1px solid {c['hairline']};
        border-radius: {r['md']}px;
        top: -1px;
        background: {c['panel']};
    }}

    QTabBar::tab {{
        background: {c['panel_alt']};
        color: {c['text_soft']};
        border: 1px solid {c['hairline']};
        border-bottom: none;
        border-top-left-radius: {r['md']}px;
        border-top-right-radius: {r['md']}px;
        padding: 8px 14px;
        margin-right: 2px;
    }}

    QTabBar::tab:selected {{
        background: {c['panel']};
        color: {c['text']};
        border-color: {c['focus_soft']};
    }}

    QSplitter::handle {{
        background: {c['hairline']};
    }}

    QStatusBar {{
        background: {c['panel']};
        border-top: 1px solid {c['hairline']};
        color: {c['text_soft']};
    }}

    QToolBar {{
        background: transparent;
        border: none;
        spacing: 6px;
    }}

    QToolButton {{
        background: {c['surface']};
        border: 1px solid {c['hairline']};
        color: {c['text']};
        border-radius: 10px;
        padding: 6px 11px;
        font-size: {t['body']}px;
        font-weight: 600;
        margin-right: 2px;
    }}

    QToolButton:hover {{
        background: {c['panel_alt']};
        border: 1px solid {c['focus_soft']};
    }}

    QToolButton:pressed {{
        background: {c['focus_soft']};
        color: #f0f7ff;
    }}

    QProgressBar {{
        border: 1px solid {c['hairline']};
        border-radius: {r['sm']}px;
        background: {c['mono_bg']};
        text-align: center;
    }}

    QProgressBar::chunk {{
        background: {c['focus']};
        border-radius: {r['sm']}px;
    }}
    """.strip()
