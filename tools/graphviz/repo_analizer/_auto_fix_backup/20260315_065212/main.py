#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import tkinter as tk
from tkinter import ttk


def main() -> None:
    if "--cli" in sys.argv:
        try:
            from app.cli.cli_mode import run_cli
            run_cli()
        except Exception as exc:
            print(f"[ERROR] No se pudo arrancar CLI: {exc}")
        return

    from app.gui.app_gui import RepoAnalyzerApp

    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass

    RepoAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
