# PRISMO Learning Core V1.2 F3 fix1
# Generated package: prismo learn3 3005 1128 fix1
# Operation model: local, read-only runtime. Standard library only.

"""Markdown report helpers.

Fix1 accepts two safe usages:
1. write_markdown_report(name, title, payload_dict, base)
2. write_markdown_report(name, raw_markdown_text, base)

The original F3 package used form #2, while the helper only supported #1.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
from .atomic_io import atomic_write_text
from .paths import ensure_store
from .clock import sortable_stamp


def to_markdown_report(title: str, payload: dict[str, Any]) -> str:
    payload = payload or {}
    lines = [
        f"# {title}",
        "",
        f"- ok: `{payload.get('ok')}`",
        f"- read_only: `{payload.get('read_only', True)}`",
        f"- mutation_allowed: `{payload.get('mutation_allowed', False)}`",
        "",
    ]
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)):
            lines.append(f"- **{key}:** `{value}`")
    return "\n".join(lines) + "\n"


def write_markdown_report(name: str, title: str, payload: dict[str, Any] | str | Path | None = None, base=None) -> Path:
    # Backward-compatible raw markdown mode:
    # write_markdown_report(name, raw_markdown, base)
    if payload is None or not isinstance(payload, dict):
        actual_base = payload if isinstance(payload, (str, Path)) else base
        root = ensure_store(actual_base) / "05_REPORTS"
        root.mkdir(parents=True, exist_ok=True)
        content = str(title)
        if not content.lstrip().startswith("#"):
            content = f"# {name}\n\n{content}"
        latest = root / f"{name}.md"
        atomic_write_text(latest, content if content.endswith("\n") else content + "\n")
        stamped = root / f"{name}_{sortable_stamp()}.md"
        atomic_write_text(stamped, content if content.endswith("\n") else content + "\n")
        return latest

    root = ensure_store(base) / "05_REPORTS"
    root.mkdir(parents=True, exist_ok=True)
    content = to_markdown_report(title, payload)
    latest = root / f"{name}.md"
    atomic_write_text(latest, content)
    stamped = root / f"{name}_{sortable_stamp()}.md"
    atomic_write_text(stamped, content)
    return latest
