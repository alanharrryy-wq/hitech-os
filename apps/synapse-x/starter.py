from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parent


def _main() -> int:
    root = _root()
    target = root / ".synapse_hidden" / "entrypoints" / "run_ui_real.py"
    if not target.exists():
        raise SystemExit(
            f"Missing UI entrypoint: {target}\n"
            "Run the repo maintenance patch that rehomes internal entrypoints."
        )

    src_dir = root / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))
    sys.path.insert(0, str(root))

    argv = [str(target)]
    argv.extend(sys.argv[1:])
    if "--root" not in argv:
        argv.extend(["--root", str(root)])

    old_argv = sys.argv[:]
    old_env = os.environ.get("SYNAPSE_X_ROOT")
    sys.argv = argv
    os.environ["SYNAPSE_X_ROOT"] = str(root)
    try:
        runpy.run_path(str(target), run_name="__main__")
        return 0
    finally:
        sys.argv = old_argv
        if old_env is None:
            os.environ.pop("SYNAPSE_X_ROOT", None)
        else:
            os.environ["SYNAPSE_X_ROOT"] = old_env


if __name__ == "__main__":
    raise SystemExit(_main())
