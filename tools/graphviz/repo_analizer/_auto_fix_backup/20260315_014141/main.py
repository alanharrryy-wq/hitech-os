#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from app.gui.app_gui import RepoAnalyzerApp
from app.cli.cli_mode import run_cli


def main() -> None:
    if "--cli" in sys.argv:
        run_cli()
        return

    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass

    try:
        RepoAnalyzerApp(root)
    except Exception as exc:
        messagebox.showerror("HITECH Repo Analyzer", f"No se pudo iniciar la GUI:\n{exc}")
        raise

    root.mainloop()


if __name__ == "__main__":
    main()
