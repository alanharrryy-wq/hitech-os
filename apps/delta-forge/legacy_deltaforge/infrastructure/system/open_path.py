from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def open_path(path: str | Path) -> None:
    target = Path(path).expanduser().resolve(strict=False)
    if sys.platform.startswith("win"):
        os.startfile(str(target))  # type: ignore[attr-defined]
        return
    if sys.platform == "darwin":
        subprocess.run(["open", str(target)], check=True)
        return
    subprocess.run(["xdg-open", str(target)], check=True)


def reveal_in_file_manager(path: str | Path) -> None:
    target = Path(path).expanduser().resolve(strict=False)
    if sys.platform.startswith("win"):
        if target.exists():
            subprocess.run(["explorer", "/select,", str(target)], check=True)
        else:
            os.startfile(str(target.parent))  # type: ignore[attr-defined]
        return
    if sys.platform == "darwin":
        subprocess.run(["open", "-R", str(target)], check=True)
        return
    subprocess.run(["xdg-open", str(target.parent if target.suffix else target)], check=True)
