#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import importlib
import os
import subprocess
import sys
import traceback
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent / "tools" / "graphviz" / "repo_analizer"
MAIN_FILE = APP_DIR / "main.py"
REQUIRED_IMPORTS = [
    "tkinter",
    "app.config",
    "app.helpers",
    "app.gui.app_gui",
]


def print_banner() -> None:
    print("=" * 72)
    print("Repo Analyzer Launcher")
    print("=" * 72)


def fail(msg: str, exit_code: int = 1) -> int:
    print(f"\n[ERROR] {msg}")
    return exit_code


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


def ok(msg: str) -> None:
    print(f"[OK]   {msg}")


def detect_repo_analyzer_dir() -> Path | None:
    candidates = []

    env_path = os.environ.get("REPO_ANALYZER_DIR", "").strip()
    if env_path:
        candidates.append(Path(env_path))

    cwd = Path.cwd().resolve()
    script_dir = Path(__file__).resolve().parent

    candidates.extend([
        cwd,
        cwd / "repo_analizer",
        cwd / "tools" / "graphviz" / "repo_analizer",
        script_dir,
        script_dir / "repo_analizer",
        APP_DIR,
        Path(r"F:\repos\hitech-os\tools\graphviz\repo_analizer"),
    ])

    seen: set[str] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except Exception:
            resolved = candidate
        key = str(resolved).lower()
        if key in seen:
            continue
        seen.add(key)

        if (resolved / "main.py").exists() and (resolved / "app").is_dir():
            return resolved

    return None


def verify_structure(app_dir: Path) -> list[str]:
    required = [
        app_dir / "main.py",
        app_dir / "app",
        app_dir / "app" / "config.py",
        app_dir / "app" / "helpers.py",
        app_dir / "app" / "gui" / "app_gui.py",
    ]
    missing = [str(p) for p in required if not p.exists()]
    return missing


def verify_imports(app_dir: Path) -> bool:
    sys.path.insert(0, str(app_dir))
    ok_all = True

    for mod_name in REQUIRED_IMPORTS:
        try:
            importlib.import_module(mod_name)
            ok(f"Import OK: {mod_name}")
        except Exception:
            ok_all = False
            print(f"[FAIL] Import failed: {mod_name}")
            traceback.print_exc()

    return ok_all


def launch_main(app_dir: Path) -> int:
    cmd = [sys.executable, "main.py"]
    info(f"Launching GUI from: {app_dir}")
    info(f"Command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=str(app_dir))
    return int(proc.returncode)


def main() -> int:
    print_banner()
    info(f"Python: {sys.executable}")
    info(f"Version: {sys.version.split()[0]}")

    app_dir = detect_repo_analyzer_dir()
    if app_dir is None:
        return fail(
            "No encontré la carpeta de repo_analizer. Ejecuta este archivo desde F:\\repos\\hitech-os o define REPO_ANALYZER_DIR."
        )

    ok(f"Proyecto detectado: {app_dir}")

    missing = verify_structure(app_dir)
    if missing:
        print("[FAIL] Faltan archivos requeridos:")
        for item in missing:
            print(f"       - {item}")
        return 2
    ok("Estructura base verificada")

    info("Verificando imports...")
    if not verify_imports(app_dir):
        return fail("Falló la verificación de imports. Revisa el traceback de arriba.", exit_code=3)

    ok("Todos los imports críticos cargaron bien")
    returncode = launch_main(app_dir)
    if returncode != 0:
        return fail(f"La GUI terminó con código {returncode}", exit_code=returncode)

    ok("La GUI cerró normalmente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
