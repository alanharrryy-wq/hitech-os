#!/usr/bin/env python3
from __future__ import annotations
import runpy
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "policy" / "validate_docs_architecture_guard.py"
runpy.run_path(str(TARGET), run_name="__main__")
