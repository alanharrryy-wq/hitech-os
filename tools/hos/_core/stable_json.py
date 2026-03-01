#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Any

COMMENT_LINE_PATTERN = re.compile(r"//.*?$", re.MULTILINE)
TRAILING_COMMA_PATTERN = re.compile(r",(?=\s*[}\]])")


def _strip_block_comments(text: str) -> str:
    out: list[str] = []
    in_string = False
    escaped = False
    i = 0
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        if ch == "/" and nxt == "*":
            i += 2
            while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def load_json_text(text: str, allow_relaxed: bool = True) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        if not allow_relaxed:
            raise
    without_block = _strip_block_comments(text)
    without_line = COMMENT_LINE_PATTERN.sub("", without_block)
    normalized = TRAILING_COMMA_PATTERN.sub("", without_line)
    return json.loads(normalized)


def load_json(path: Path, allow_relaxed: bool = True) -> Any:
    raw = path.read_text(encoding="utf-8")
    return load_json_text(raw, allow_relaxed=allow_relaxed)


def dump_json(data: Any, indent: int = 2, sort_keys: bool = True) -> str:
    rendered = json.dumps(
        data,
        ensure_ascii=False,
        indent=indent,
        sort_keys=sort_keys,
        separators=(",", ": "),
    )
    return rendered + "\n"


def write_json(path: Path, data: Any, indent: int = 2, sort_keys: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_json(data, indent=indent, sort_keys=sort_keys), encoding="utf-8", newline="\n")


def hash_json(data: Any) -> str:
    return sha256(dump_json(data, indent=2, sort_keys=True).encode("utf-8")).hexdigest()

