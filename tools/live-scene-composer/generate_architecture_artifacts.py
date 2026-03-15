#!/usr/bin/env python3
from __future__ import annotations
import runpy
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "architecture" / "generate_architecture_artifacts.py"
runpy.run_path(str(TARGET), run_name="__main__")
