# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Safe text extractors for supported evidence files."""
from __future__ import annotations
import csv, io, json, re
from pathlib import Path
from typing import Any
from .constants import MAX_TEXT_BYTES
from .safety import safe_open_text, SafetyViolation
from .sanitize import clean_text
from .secret_scanner import scan_text, redact

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)
HTML_TAG_RE = re.compile(r"<[^>]+>")
PASS_FAIL_RE = re.compile(r"\b(PASS|FAIL|WARN|ERROR|BLOCKED|PARTIAL)\b", re.I)


def extract_text(path: str | Path, max_bytes: int = MAX_TEXT_BYTES) -> dict[str, Any]:
    try:
        text = safe_open_text(path, max_bytes=max_bytes)
    except SafetyViolation as exc:
        return {"ok": False, "text": "", "metadata_only": True, "error": str(exc)}
    secret = scan_text(text)
    return {
        "ok": True,
        "text": redact(text),
        "raw_chars": len(text),
        "metadata_only": False,
        "secret_scan": secret,
        "signals": extract_log_signals_from_text(text),
    }


def extract_json(path: str | Path) -> dict[str, Any]:
    result = extract_text(path)
    if not result.get("ok"):
        return result
    try:
        data = json.loads(result.get("text") or "{}")
    except Exception as exc:
        result["json_error"] = str(exc)
        return result
    result["json_type"] = type(data).__name__
    if isinstance(data, dict):
        result["top_keys"] = sorted(str(k) for k in data.keys())[:80]
    elif isinstance(data, list):
        result["array_len"] = len(data)
    return result


def extract_markdown_outline(path: str | Path) -> dict[str, Any]:
    result = extract_text(path)
    text = result.get("text") or ""
    headings = [{"level": len(m.group(1)), "text": clean_text(m.group(2), 200)} for m in HEADING_RE.finditer(text)]
    result["headings"] = headings[:120]
    return result


def extract_html_summary(path: str | Path) -> dict[str, Any]:
    result = extract_text(path)
    text = result.get("text") or ""
    text = re.sub(r"(?is)<script.+?</script>", " ", text)
    text = re.sub(r"(?is)<style.+?</style>", " ", text)
    plain = HTML_TAG_RE.sub(" ", text)
    result["plain_preview"] = clean_text(" ".join(plain.split()), 4000)
    return result


def extract_log_signals(path: str | Path) -> dict[str, Any]:
    return extract_text(path).get("signals", {})


def extract_log_signals_from_text(text: str) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for match in PASS_FAIL_RE.finditer(text or ""):
        key = match.group(1).upper()
        counts[key] = counts.get(key, 0) + 1
    return {"status_counts": counts, "line_count": len((text or "").splitlines())}


def read_csv_preview(path: str | Path, max_rows: int = 25) -> dict[str, Any]:
    result = extract_text(path, max_bytes=min(MAX_TEXT_BYTES, 256 * 1024))
    if not result.get("ok"):
        return result
    buf = io.StringIO(result.get("text") or "")
    try:
        rows = list(csv.reader(buf))[:max_rows]
    except Exception as exc:
        result["csv_error"] = str(exc)
        return result
    result["rows_preview"] = rows
    return result
