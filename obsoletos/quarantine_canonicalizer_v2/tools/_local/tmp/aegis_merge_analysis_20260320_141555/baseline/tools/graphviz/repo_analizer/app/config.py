#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

APP_TITLE = "HITECH Repo Analyzer"
APP_VERSION = "3.0 Qt"
DEFAULT_SEARCH_EXTS = {
    ".ts", ".tsx", ".js", ".jsx",
    ".py", ".json", ".md", ".mdx",
    ".css", ".scss", ".html", ".htm",
    ".yml", ".yaml", ".txt", ".sql",
    ".sh", ".bat", ".ps1",
}
CODE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".py"}
IMPORT_SCAN_EXTS = {".ts", ".tsx", ".js", ".jsx"}
EXCLUDED_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "coverage",
    ".turbo", ".cache", ".vscode", ".idea", "__pycache__", ".venv",
    "venv", "out", "target", "bin", "obj"
}
SETTINGS_FILE = ".repo_analyzer_settings.json"
MAX_PREVIEW_FILE_SIZE = 2_000_000
DEFAULT_MAX_RESULTS = 500
