from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication


APP_ROOT = Path(__file__).resolve().parent
REPO_ROOT = APP_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from nexus.host.window import NexusGlassDesktopWindow  # noqa: E402


def run_smoke() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    window = NexusGlassDesktopWindow(enable_http_bridge=False)
    report = window.run_smoke_cycle()
    window.close()
    app.processEvents()
    print("NEXUS_SMOKE_OK", json.dumps(report, ensure_ascii=True))
    if not (report.get("upsert_ok") and report.get("summary_ok") and report.get("snapshot_ok")):
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Hitech Nexus desktop host on the glass platform.")
    parser.add_argument("--smoke", action="store_true", help="Run non-interactive integration smoke and exit.")
    parser.add_argument("--enable-http-bridge", action="store_true", help="Start optional local HTTP adapter.")
    parser.add_argument("--http-port", type=int, default=0, help="Port for optional local HTTP bridge.")
    args = parser.parse_args()

    if args.smoke:
        return run_smoke()

    app = QApplication.instance() or QApplication(sys.argv)
    window = NexusGlassDesktopWindow(
        enable_http_bridge=bool(args.enable_http_bridge),
        http_port=int(args.http_port),
    )
    window.resize(1540, 940)
    window.setWindowTitle("Hitech Nexus - Glass Host")
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

