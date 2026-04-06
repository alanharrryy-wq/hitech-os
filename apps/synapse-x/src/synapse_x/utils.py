from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any


UTC = dt.timezone.utc

PATH_PATTERN = re.compile(r"(?:[A-Za-z]:\\[^\s\"']+|/(?:[^\s/]+/)*[^\s\"']+)")
UUID_PATTERN = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I)
HEX_PATTERN = re.compile(r"\b0x[0-9a-f]+\b", re.I)
LONG_NUMBER_PATTERN = re.compile(r"\b\d{2,}\b")
WHITESPACE_PATTERN = re.compile(r"\s+")
TOKEN_PATTERN = re.compile(r"[a-z][a-z0-9_+.-]{2,}")
TOKEN_STOPWORDS = {
    "the", "and", "for", "with", "from", "into", "while", "when", "then", "line", "file", "most", "recent",
    "call", "last", "module", "main", "error", "errors", "warning", "warnings", "exception", "traceback",
    "failed", "failure", "fatal", "during", "after", "before", "could", "would", "should", "have", "has",
    "had", "this", "that", "those", "these", "onto", "through", "there", "their", "about", "just",
}


def utc_now_iso() -> str:
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def file_mtime_iso(path: Path) -> str:
    return dt.datetime.fromtimestamp(path.stat().st_mtime, UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return compact_json(value)
    except Exception:
        return str(value)


def slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return value.strip("_") or "unknown"


def normalize_whitespace(text: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", text.strip())


def semantic_text_normalize(text: Any) -> str:
    normalized = coerce_text(text).lower()
    normalized = PATH_PATTERN.sub("<path>", normalized)
    normalized = UUID_PATTERN.sub("<id>", normalized)
    normalized = HEX_PATTERN.sub("<hex>", normalized)
    normalized = LONG_NUMBER_PATTERN.sub("<n>", normalized)
    normalized = re.sub(r'".*?"', '"<str>"', normalized)
    normalized = normalize_whitespace(normalized)
    return normalized


def semantic_text_fingerprint(text: Any, *, max_tokens: int = 16) -> str:
    normalized = semantic_text_normalize(text)
    tokens: list[str] = []
    for token in TOKEN_PATTERN.findall(normalized):
        if token in TOKEN_STOPWORDS:
            continue
        if token not in tokens:
            tokens.append(token)
        if len(tokens) >= max_tokens:
            break
    if tokens:
        return slugify("-".join(tokens))
    return slugify(normalized[:80])


def keyword_tokens(text: Any, *, max_tokens: int = 12) -> list[str]:
    normalized = semantic_text_normalize(text)
    out: list[str] = []
    for token in TOKEN_PATTERN.findall(normalized):
        if token in TOKEN_STOPWORDS:
            continue
        if token not in out:
            out.append(token)
        if len(out) >= max_tokens:
            break
    return out
