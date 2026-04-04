from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QVBoxLayout, QWidget

from ui_foundation.ui_runtime import get_visual_runtime
from ui_foundation.visual_screen_template import VisualScreenTemplate


class CustomersDashboardScreen(VisualScreenTemplate):
    visual_role = "workspace"
    visual_variant = "data-heavy"
    visual_emphasis = "high"
    visual_fx_level = "subtle"

    def subtitle_text(self) -> str:
        return "Example dashboard created from the mandatory scaffold."

    def build_main_content(self) -> QWidget:
        host = QWidget()
        layout = QVBoxLayout(host)

        intro = QLabel("This exists to prove the default path is already structured.")
        intro.setWordWrap(True)

        data = QListWidget()
        data.addItems(
            [
                "Customer 001 - Active",
                "Customer 002 - Waiting approval",
                "Customer 003 - Missing documents",
            ]
        )

        layout.addWidget(intro)
        layout.addWidget(data, 1)
        return host


def main() -> int:
    app = QApplication(sys.argv)
    runtime = get_visual_runtime()
    runtime.apply_app_defaults(app)
    runtime.configure_optional_integrations()

    window = CustomersDashboardScreen()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
