from __future__ import annotations

from pathlib import Path

from synapse_x.config import Settings
from synapse_x.engine import SynapseEngine


def launch_ui(root: str | None = None) -> int:
    try:
        from PySide6.QtWidgets import QApplication
    except Exception as exc:  # noqa: BLE001
        print(f"PySide6 is not available: {exc}")
        return 2

    from synapse_x.ui.main_window import SynapseMainWindow

    settings = Settings(root=Path(root).expanduser().resolve()) if root else Settings()
    engine = SynapseEngine(settings=settings)
    app = QApplication.instance() or QApplication([])
    window = SynapseMainWindow(engine)
    window.show()
    return int(app.exec())


def main() -> int:
    return launch_ui()


if __name__ == "__main__":
    raise SystemExit(main())
