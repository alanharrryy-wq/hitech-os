from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..engine.context import ScanConfig


@dataclass(slots=True)
class ConfigLoadResult:
    config: ScanConfig
    source_path: Path
    raw: dict[str, Any] = field(default_factory=dict)


_DEFAULT_CONFIG: dict[str, Any] = {
    "version": "3.0.0-proto1",
    "repo_markers": [".git", "package.json"],
    "include_extensions": [".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"],
    "max_file_bytes": 1500000,
    "exclude_dir_names": [
        ".git",
        ".next",
        "dist",
        "build",
        "coverage",
        "node_modules",
        "out",
        "tmp",
        "temp",
        ".turbo",
        ".cache",
    ],
    "exclude_path_substrings": [],
    "probable_tooling_path_markers": ["/app/dev/", "/debug/", "/storybook/", "/scene-studio/", "/tools/", "/__tests__/", "/playground/"],
    "serverish_path_markers": ["/app/", "/page.", "/layout.", "/route.", "/api/"],
    "browser_api_tokens": [
        "window",
        "document",
        "navigator",
        "location",
        "history",
        "localStorage",
        "sessionStorage",
        "matchMedia",
    ],
    "hydration_keywords": ["hydrate", "hydration", "mismatch", "suppressHydrationWarning", "ssr: false"],
    "diff_mode": {
        "enabled": False,
        "base_ref": "HEAD",
        "include_untracked": True,
        "staged_only": False,
    },
    "line_context_radius": 1,
    "client_directive_window": 6,
    "ignore_minified_lines_over": 300,
    "finding_limit_per_rule_per_file": 200,
}


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _ensure_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError(f"Config field '{field_name}' must be a list.")
    return [str(item) for item in value]


def load_config(path: str | Path | None = None) -> ConfigLoadResult:
    source_path = Path(path).resolve() if path else Path(__file__).resolve().parents[1] / 'config.json'
    raw: dict[str, Any] = {}
    if source_path.exists():
        raw = json.loads(source_path.read_text(encoding='utf-8'))
    merged = _merge(_DEFAULT_CONFIG, raw)
    diff_mode = merged.get('diff_mode', {})
    config = ScanConfig(
        version=str(merged['version']),
        repo_markers=_ensure_list(merged.get('repo_markers'), 'repo_markers'),
        include_extensions=tuple(_ensure_list(merged.get('include_extensions'), 'include_extensions')),
        max_file_bytes=int(merged.get('max_file_bytes', 1500000)),
        exclude_dir_names=frozenset(_ensure_list(merged.get('exclude_dir_names'), 'exclude_dir_names')),
        exclude_path_substrings=tuple(_ensure_list(merged.get('exclude_path_substrings'), 'exclude_path_substrings')),
        probable_tooling_path_markers=tuple(_ensure_list(merged.get('probable_tooling_path_markers'), 'probable_tooling_path_markers')),
        serverish_path_markers=tuple(_ensure_list(merged.get('serverish_path_markers'), 'serverish_path_markers')),
        browser_api_tokens=tuple(_ensure_list(merged.get('browser_api_tokens'), 'browser_api_tokens')),
        hydration_keywords=tuple(_ensure_list(merged.get('hydration_keywords'), 'hydration_keywords')),
        diff_enabled=bool(diff_mode.get('enabled', False)),
        diff_base_ref=str(diff_mode.get('base_ref', 'HEAD')),
        diff_include_untracked=bool(diff_mode.get('include_untracked', True)),
        diff_staged_only=bool(diff_mode.get('staged_only', False)),
        line_context_radius=int(merged.get('line_context_radius', 1)),
        client_directive_window=int(merged.get('client_directive_window', 6)),
        ignore_minified_lines_over=int(merged.get('ignore_minified_lines_over', 300)),
        finding_limit_per_rule_per_file=int(merged.get('finding_limit_per_rule_per_file', 200)),
    )
    return ConfigLoadResult(config=config, source_path=source_path, raw=raw)
