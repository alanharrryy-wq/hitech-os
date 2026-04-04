"""
Generate a new governed screen from the approved scaffold.

Usage:
    python tools/new_ui_screen.py CustomersDashboard
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


TEMPLATE = """from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ui_foundation.visual_screen_template import VisualScreenTemplate


class {class_name}(VisualScreenTemplate):
    visual_role = "workspace"
    visual_variant = "{variant}"
    visual_emphasis = "{emphasis}"
    visual_fx_level = "{fx}"

    def subtitle_text(self) -> str:
        return "{subtitle}"

    def build_primary_actions(self):
        return [QPushButton("Refresh"), QPushButton("Create")]

    def build_main_content(self) -> QWidget:
        host = QWidget()
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        intro = QLabel("{intro}")
        intro.setWordWrap(True)

        notes = QTextEdit()
        notes.setPlaceholderText("Put your widgets here...")

        layout.addWidget(intro)
        layout.addWidget(notes, 1)
        return host
"""


def to_snake(name: str) -> str:
    text = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    text = re.sub(r"[^a-z0-9_]+", "_", text).strip("_")
    return text


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python tools/new_ui_screen.py CustomersDashboard")
        return 1

    raw_name = sys.argv[1].strip()
    class_name = raw_name if raw_name.endswith("Screen") else f"{raw_name}Screen"
    file_name = to_snake(class_name) + ".py"

    destination = Path("src") / "screens"
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / file_name

    if target.exists():
        print(f"[SKIP] {target} already exists")
        return 0

    text = TEMPLATE.format(
        class_name=class_name,
        variant="data-heavy",
        emphasis="high",
        fx="subtle",
        subtitle="Generated from the mandatory UI scaffold.",
        intro="This screen was created from the approved path, so the shell and visual defaults are already wired.",
    )
    target.write_text(text, encoding="utf-8")
    print(f"[OK] wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
