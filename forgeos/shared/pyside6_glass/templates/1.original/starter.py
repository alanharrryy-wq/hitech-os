#!/usr/bin/env python
"""PySide6 Glass Template Console - Open with double-click"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure sys.path includes current directory
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Check if we have a display
has_display = bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY') or
                  os.name == 'nt')  # Windows always has display

if not has_display or os.environ.get('QT_QPA_PLATFORM') == 'offscreen':
    print("ERROR: No graphical display available.")
    print("This application requires a graphical desktop environment.")
    print("")
    print("To run from command line:")
    print('  cd "F:\repos\hitech-os\forgeos\shared\pyside6_glass\templates\1.original"')
    print("  py -3 starter.py")
    input("Press Enter to continue...")
    sys.exit(1)

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QFrame, QLabel, QVBoxLayout

    from visuals.common.helpers import ensure_app
    from visuals.common.types import ActionSpec, ChipSpec, TemplateConsoleConfig
    from visuals.screens.template_console import TemplateConsoleWindow
    from visuals.widgets.primitives import make_placeholder

    def _build_custom_main_slot() -> QFrame:
        frame = QFrame()
        frame.setProperty("card", "muted")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("Live Output Slot")
        title.setProperty("role", "section")
        layout.addWidget(title, 0, Qt.AlignLeft)

        body = QLabel(
            "This is an injected widget. Replace it with charts, logs, terminal output, "
            "data grids, inspectors, or any project-specific panel."
        )
        body.setProperty("role", "hint")
        body.setWordWrap(True)
        layout.addWidget(body)
        layout.addWidget(
            make_placeholder(
                "Nested Placeholder",
                "Slot composition is fully modular. You can swap this block without touching the shell.",
                icon="output",
            )
        )
        return frame

    def main() -> int:
        app: QApplication = ensure_app()

        config = TemplateConsoleConfig(
            window_title="Template Console",
            theme_id="silver_frost_cyan",
            ui_scale="100",
            hero_eyebrow="Workspace",
            hero_title="Template Console",
            hero_subtitle=(
                "Reusable frameless glass console with configurable actions, "
                "panel order, optional icons, and content slots."
            ),
            hero_icon="workspace",
            hero_chips=[
                ChipSpec("Template", tone="accent", icon="spark"),
                ChipSpec("Neutral Demo", tone="neutral", icon="overview"),
            ],
            toolbar_actions=[
                ActionSpec("refresh", "Refresh", icon="refresh", variant="secondary"),
                ActionSpec("open_selector", "Workspace", icon="workspace", variant="secondary"),
                ActionSpec("open_progress", "Progress", icon="play", variant="primary"),
                ActionSpec("toggle_sidebar", "Sidebar", icon="panel", variant="secondary"),
            ],
            panel_order=("sidebar", "main", "aux"),
            show_sidebar=True,
            show_aux=True,
            footer_hint=(
                "Starter ready: reorder toolbar actions, toggle panels, replace slots, and switch themes."
            ),
        )

        window = TemplateConsoleWindow(config=config)
        window.set_slot_widget("main", _build_custom_main_slot())
        window.show()
        return app.exec()

    if __name__ == "__main__":
        raise SystemExit(main())

except ImportError as e:
    print(f"ERROR: Import failed: {e}", file=sys.stderr)
    input("Press any key to continue...")
    raise SystemExit(1)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    input("Press any key to continue...")
    raise SystemExit(1)
