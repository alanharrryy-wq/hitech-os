from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any, Iterable

from synapse_x.models import CanonicalRecord
from synapse_x.utils import (
    coerce_text,
    file_mtime_iso,
    keyword_tokens,
    normalize_whitespace,
    semantic_text_fingerprint,
    semantic_text_normalize,
    sha256_text,
    slugify,
)

SESSION_KEYS = (
    "session_id",
    "sessionid",
    "conversation_id",
    "conversationid",
    "run_id",
    "runid",
    "rollout_id",
    "job_id",
    "build_id",
    "trace_id",
    "request_id",
    "id",
)

TIMESTAMP_KEYS = (
    "timestamp",
    "time",
    "datetime",
    "created_at",
    "createdat",
    "updated_at",
    "started_at",
    "finished_at",
    "date",
)

EXPLICIT_SESSION_PATTERNS = [
    re.compile(r"\b(?:session|conversation|run|rollout|job|build|trace|request)[_\s-]*id\s*[:=]\s*([A-Za-z0-9][A-Za-z0-9._:-]{2,})", re.I),
    re.compile(r"\b(rollout[-_][A-Za-z0-9._:-]+)\b", re.I),
    re.compile(r"\b(run[-_][A-Za-z0-9._:-]+)\b", re.I),
    re.compile(r"\b([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})\b", re.I),
]

FILENAME_SESSION_PATTERNS = [
    re.compile(r"(rollout[-_]\d{4}[-_]\d{2}[-_]\d{2})(?=$|[^A-Za-z0-9])", re.I),
    re.compile(r"\b(run[-_][A-Za-z0-9.-]+)\b", re.I),
    re.compile(r"\b(build[-_][A-Za-z0-9.-]+)\b", re.I),
    re.compile(r"\b(session[-_][A-Za-z0-9.-]+)\b", re.I),
]

ISO_TS_PATTERN = re.compile(
    r"\b(20\d{2}-\d{2}-\d{2}(?:[T\s]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)\b"
)
SLASH_TS_PATTERN = re.compile(
    r"\b(20\d{2})[/-](\d{2})[/-](\d{2})(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?)?\b"
)
DMY_TS_PATTERN = re.compile(
    r"\b(\d{2})/(\d{2})/(20\d{2})(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?)?\b"
)
TIME_ONLY_PATTERN = re.compile(r"\b(\d{2}):(\d{2})(?::(\d{2}))?\b")
DATE_ONLY_PATTERN = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
FILENAME_DATE_PATTERN = re.compile(r"(20\d{2}[-_]\d{2}[-_]\d{2})(?=$|[^A-Za-z0-9])")

ERROR_TRIGGER_PATTERN = re.compile(
    r"\b(traceback|exception|fatal|error|failed|failure|segmentation fault|crash|panic|assertionerror|runtimeerror|valueerror|typeerror|keyerror|indexerror)\b",
    re.I,
)
WARNING_TRIGGER_PATTERN = re.compile(r"\b(warn|warning|deprecated)\b", re.I)
STACK_CONTINUATION_PATTERN = re.compile(
    r"^(\s+File\s+|\s+[A-Za-z_][A-Za-z0-9_]*Error:|\s+[A-Za-z_][A-Za-z0-9_]*Exception:|\s*Caused by:|\s*at\s+|\s*\^|\s*\.\.\.|\s+)",
    re.I,
)
EXIT_CODE_PATTERN = re.compile(r"\b(?:exit(?:ed)?\s+with\s+code|code=)(\d+)\b", re.I)
EXCEPTION_NAME_PATTERN = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*(?:Error|Exception))\b")

TOOL_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bpython\s+-m\s+pytest\b", re.I), "pytest"),
    (re.compile(r"\bpytest\b", re.I), "pytest"),
    (re.compile(r"\bpyside6\b", re.I), "pyside6"),
    (re.compile(r"\bpython(?:3(?:\.\d+)?)?\b", re.I), "python"),
    (re.compile(r"\bpip(?:3)?\b", re.I), "pip"),
    (re.compile(r"\buv\b", re.I), "uv"),
    (re.compile(r"\bpoetry\b", re.I), "poetry"),
    (re.compile(r"\bgit\b", re.I), "git"),
    (re.compile(r"\bdocker(?:\s+compose)?\b", re.I), "docker"),
    (re.compile(r"\bsqlite(?:3)?\b", re.I), "sqlite"),
    (re.compile(r"\bpowershell(?:\.exe)?\b", re.I), "powershell"),
    (re.compile(r"\bpwsh\b", re.I), "powershell"),
    (re.compile(r"\bbash\b", re.I), "bash"),
    (re.compile(r"\bnpm\b", re.I), "npm"),
    (re.compile(r"\bpnpm\b", re.I), "pnpm"),
    (re.compile(r"\byarn\b", re.I), "yarn"),
    (re.compile(r"\bnode\b", re.I), "node"),
    (re.compile(r"\bcurl\b", re.I), "curl"),
    (re.compile(r"\bwget\b", re.I), "wget"),
    (re.compile(r"\bcmake\b", re.I), "cmake"),
    (re.compile(r"\bmake\b", re.I), "make"),
]

GENERIC_SESSION_VALUES = {
    "id",
    "unknown",
    "null",
    "none",
    "session",
    "run",
    "job",
    "build",
    "trace",
    "request",
    "payload",
    "event",
}


def normalize_raw(raw: dict[str, Any], source_path: Path) -> CanonicalRecord:
    payload = raw.get("payload")
    record_type = raw.get("kind", "unknown")
    source_text = coerce_text(payload)

    session_id, session_strategy, session_confidence = _extract_session_identity(payload, source_text, source_path)
    record_timestamp, timestamp_strategy = _extract_record_timestamp(payload, source_text, source_path)
    events = _extract_events(payload, source_text, record_timestamp, session_id, source_path)
    errors = _extract_errors(payload, source_text, record_timestamp, session_id, source_path)
    tools = _extract_tools(payload, source_text, record_timestamp, session_id, source_path)
    summary = _extract_summary(payload, source_text, errors, tools)
    title = source_path.stem

    metadata = {
        "source_name": source_path.name,
        "source_suffix": source_path.suffix.lower(),
        "line_count": len(source_text.splitlines()) if source_text else 0,
        "event_count": len(events),
        "error_count": len(errors),
        "tool_count": len(tools),
        "heuristics": {
            "session_strategy": session_strategy,
            "session_confidence": session_confidence,
            "timestamp_strategy": timestamp_strategy,
            "primary_error": errors[0]["error_type"] if errors else None,
            "primary_tool": tools[0]["tool_name"] if tools else None,
        },
        "correlation": _build_correlation_metadata(
            payload=payload,
            source_text=source_text,
            source_path=source_path,
            record_timestamp=record_timestamp,
            session_id=session_id,
            errors=errors,
            tools=tools,
            summary=summary,
        ),
    }

    return CanonicalRecord(
        session_id=session_id,
        timestamp_utc=record_timestamp,
        record_type=record_type,
        source_path=str(source_path),
        source_hash=sha256_text(source_text),
        title=title,
        summary=summary,
        events=events,
        errors=errors,
        tools=tools,
        metadata=metadata,
    )


def _extract_session_identity(payload: Any, source_text: str, source_path: Path) -> tuple[str, str, str]:
    candidates: list[tuple[int, str, str, str]] = []

    for key, value in _iter_key_values(payload, max_depth=6, max_items=250):
        leaf_key = key.split('.')[-1].split('[')[0]
        normalized_key = leaf_key.replace("-", "").replace("_", "").lower()
        if normalized_key in SESSION_KEYS:
            candidate = _clean_session_candidate(value)
            if candidate:
                priority = 100 - SESSION_KEYS.index(normalized_key)
                if normalized_key == 'id' and not re.search(r"(?:run|rollout|session|conversation|job|build|trace|request)", candidate, re.I):
                    priority -= 60
                candidates.append((priority, candidate, f"payload:{key}", "high" if priority >= 60 else "medium"))

    for pattern in EXPLICIT_SESSION_PATTERNS:
        match = pattern.search(source_text)
        if match:
            candidate = _clean_session_candidate(match.group(1))
            if candidate:
                candidates.append((80, candidate, f"text:{pattern.pattern[:20]}", "medium"))

    stem = source_path.stem
    for pattern in FILENAME_SESSION_PATTERNS:
        match = pattern.search(stem)
        if match:
            candidate = _clean_session_candidate(match.group(1))
            if candidate:
                candidates.append((70, candidate, "filename-pattern", "medium"))

    if candidates:
        candidates.sort(key=lambda item: (-item[0], -len(item[1]), item[1]))
        _, best, strategy, confidence = candidates[0]
        return best, strategy, confidence

    date_hint = _extract_date_hint_from_filename(source_path) or source_path.stem
    return f"derived-{slugify(date_hint)}", "derived-from-filename", "low"


def _extract_record_timestamp(payload: Any, source_text: str, source_path: Path) -> tuple[str, str]:
    candidates: list[tuple[dt.datetime, str]] = []

    for key, value in _iter_key_values(payload, max_depth=6, max_items=500):
        leaf_key = key.split('.')[-1].split('[')[0]
        normalized_key = leaf_key.replace("-", "").replace("_", "").lower()
        if normalized_key in TIMESTAMP_KEYS and isinstance(value, str):
            parsed = _parse_timestamp_candidate(value, source_path)
            if parsed:
                candidates.append((parsed, f"payload:{key}"))

    if isinstance(payload, list):
        for item in payload[:200]:
            parsed = _extract_timestamp_from_value(item, source_path)
            if parsed:
                candidates.append((parsed, "list-item"))

    for text_candidate, strategy in _collect_text_timestamp_candidates(source_text, source_path):
        candidates.append((text_candidate, strategy))

    if candidates:
        best_dt, strategy = min(candidates, key=lambda item: item[0])
        return _isoformat_utc(best_dt), strategy

    return file_mtime_iso(source_path), "file-mtime"


def _extract_summary(payload: Any, source_text: str, errors: list[dict[str, Any]], tools: list[dict[str, Any]]) -> str:
    if isinstance(payload, dict):
        for key in ("summary", "message", "title", "description"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()[:240]

    if errors:
        summary = errors[0]["message"].splitlines()[0].strip()
        if summary:
            return summary[:240]

    lines = [line.strip() for line in source_text.splitlines() if line.strip()]
    if lines:
        return lines[0][:240]

    if tools:
        return f"Observed tool activity: {tools[0]['tool_name']}"[:240]

    return "No summary"


def _extract_events(
    payload: Any,
    source_text: str,
    record_timestamp: str,
    session_id: str,
    source_path: Path,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    if isinstance(payload, dict) and isinstance(payload.get("events"), list):
        for idx, item in enumerate(payload["events"][:800]):
            item_text = coerce_text(item)
            item_timestamp = _timestamp_for_item(item, source_path, record_timestamp)
            item_tool = _first_tool_name(item_text)
            events.append({
                "timestamp_utc": item_timestamp,
                "category": _infer_event_category(item_text, default=item.get("type", item.get("category", "event")) if isinstance(item, dict) else "event"),
                "message": item_text[:2000],
                "tool_name": item_tool,
                "session_id": session_id,
                "raw_ref": f"events[{idx}]",
            })
        return _dedupe_event_like(events)

    if isinstance(payload, list):
        for idx, item in enumerate(payload[:1200]):
            item_text = coerce_text(item)
            if not item_text.strip():
                continue
            item_timestamp = _timestamp_for_item(item, source_path, record_timestamp)
            item_tool = _first_tool_name(item_text)
            default_category = "event"
            if isinstance(item, dict):
                default_category = str(item.get("type", item.get("level", item.get("event", "event"))))
            events.append({
                "timestamp_utc": item_timestamp,
                "category": _infer_event_category(item_text, default=default_category),
                "message": item_text[:2000],
                "tool_name": item_tool,
                "session_id": session_id,
                "raw_ref": f"rows[{idx}]",
            })
        return _dedupe_event_like(events)

    previous_normalized = ""
    for idx, line in enumerate(source_text.splitlines()[:3000]):
        stripped = line.strip()
        if not stripped:
            continue
        normalized_line = re.sub(r"\s+", " ", stripped)
        if normalized_line == previous_normalized:
            continue
        previous_normalized = normalized_line
        line_timestamp = _extract_line_timestamp(line, source_path, record_timestamp)
        line_tool = _first_tool_name(line)
        events.append({
            "timestamp_utc": line_timestamp,
            "category": _infer_event_category(line),
            "message": stripped[:2000],
            "tool_name": line_tool,
            "session_id": session_id,
            "raw_ref": f"line:{idx + 1}",
        })
    return _dedupe_event_like(events)


def _extract_errors(
    payload: Any,
    source_text: str,
    record_timestamp: str,
    session_id: str,
    source_path: Path,
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def add_error(message: str, raw_ref: str, error_type: str | None = None, severity: str | None = None, ts: str | None = None) -> None:
        cleaned = message.strip()
        if not cleaned:
            return
        inferred_type = error_type or _infer_error_type(cleaned)
        inferred_severity = severity or _infer_severity(cleaned)
        signature = _error_signature(cleaned, inferred_type)
        key = (inferred_type, signature)
        if key in seen:
            for existing in errors:
                if existing.get("error_type") == inferred_type and existing.get("error_signature") == signature:
                    if len(cleaned) > len(existing.get("message", "")):
                        existing["message"] = cleaned[:4000]
                    if inferred_severity == "fatal":
                        existing["severity"] = "fatal"
                    return
            return
        seen.add(key)
        errors.append({
            "timestamp_utc": ts or _extract_line_timestamp(cleaned, source_path, record_timestamp),
            "error_type": inferred_type,
            "message": cleaned[:4000],
            "severity": inferred_severity,
            "session_id": session_id,
            "raw_ref": raw_ref,
            "error_signature": signature,
        })

    if isinstance(payload, dict):
        for key, value in _iter_key_values(payload, max_depth=6, max_items=300):
            if key.lower() in {"error", "errors", "exception", "failure", "fatal", "stderr", "traceback"}:
                text = coerce_text(value)
                if text.strip():
                    add_error(text, f"payload:{key}")

    if isinstance(payload, list):
        for idx, item in enumerate(payload[:1200]):
            text = coerce_text(item)
            if ERROR_TRIGGER_PATTERN.search(text):
                add_error(text, f"rows[{idx}]")

    if isinstance(payload, dict):
        errors.sort(key=lambda item: (item["timestamp_utc"], item["severity"], item["error_type"]))
        return errors[:500]

    lines = source_text.splitlines()
    idx = 0
    while idx < min(len(lines), 4000):
        raw_line = lines[idx]
        stripped = raw_line.strip()
        if not stripped:
            idx += 1
            continue

        if ERROR_TRIGGER_PATTERN.search(stripped) or EXIT_CODE_PATTERN.search(stripped):
            block = [stripped]
            start = idx + 1
            j = idx + 1
            while j < min(len(lines), idx + 12):
                candidate = lines[j].rstrip("\n")
                if not candidate.strip():
                    if block and len(block) > 1:
                        block.append("")
                    j += 1
                    continue
                if STACK_CONTINUATION_PATTERN.match(candidate) or candidate.startswith("Traceback"):
                    block.append(candidate.strip("\n"))
                    j += 1
                    continue
                if EXCEPTION_NAME_PATTERN.search(candidate) and len(block) < 8:
                    block.append(candidate.strip("\n"))
                    j += 1
                    continue
                break
            add_error("\n".join(block), f"line:{start}-{j}")
            idx = j
            continue
        idx += 1

    errors.sort(key=lambda item: (item["timestamp_utc"], item["severity"], item["error_type"]))
    return errors[:500]


def _extract_tools(
    payload: Any,
    source_text: str,
    record_timestamp: str,
    session_id: str,
    source_path: Path,
) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def add_tool(tool_name: str, raw_ref: str, action: str = "observed", ts: str | None = None) -> None:
        normalized = _normalize_tool_name(tool_name)
        if not normalized:
            return
        key = (normalized, raw_ref)
        if key in seen:
            return
        seen.add(key)
        tools.append({
            "timestamp_utc": ts or record_timestamp,
            "tool_name": normalized,
            "action": action,
            "session_id": session_id,
            "raw_ref": raw_ref,
        })

    if isinstance(payload, dict):
        for key, value in _iter_key_values(payload, max_depth=6, max_items=300):
            lowered = key.lower()
            if lowered in {"tool", "tools", "command", "cmd", "argv", "process", "program"}:
                text = coerce_text(value)
                for tool_name in _extract_tool_names(text):
                    add_tool(tool_name, f"payload:{key}", action="structured", ts=_extract_line_timestamp(text, source_path, record_timestamp))

    iterable: Iterable[Any]
    if isinstance(payload, list):
        iterable = payload[:1200]
        for idx, item in enumerate(iterable):
            text = coerce_text(item)
            ts = _extract_line_timestamp(text, source_path, record_timestamp)
            for tool_name in _extract_tool_names(text):
                add_tool(tool_name, f"rows[{idx}]", ts=ts)
    else:
        for idx, line in enumerate(source_text.splitlines()[:3000]):
            ts = _extract_line_timestamp(line, source_path, record_timestamp)
            for tool_name in _extract_tool_names(line):
                add_tool(tool_name, f"line:{idx + 1}", ts=ts)

    tools.sort(key=lambda item: (item["timestamp_utc"], item["tool_name"], item["raw_ref"]))
    return tools[:500]


def _iter_key_values(value: Any, *, max_depth: int, max_items: int) -> Iterable[tuple[str, Any]]:
    count = 0

    def walk(current: Any, prefix: str, depth: int) -> Iterable[tuple[str, Any]]:
        nonlocal count
        if depth > max_depth or count >= max_items:
            return
        if isinstance(current, dict):
            for key, child in current.items():
                if count >= max_items:
                    return
                count += 1
                key_str = f"{prefix}.{key}" if prefix else str(key)
                yield key_str, child
                yield from walk(child, key_str, depth + 1)
        elif isinstance(current, list):
            for idx, child in enumerate(current[:50]):
                if count >= max_items:
                    return
                yield from walk(child, f"{prefix}[{idx}]", depth + 1)

    yield from walk(value, "", 0)


def _clean_session_candidate(value: Any) -> str | None:
    text = coerce_text(value).strip().strip('"\'')
    if not text:
        return None
    lowered = text.lower()
    if lowered in GENERIC_SESSION_VALUES:
        return None
    if len(text) < 3:
        return None
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^A-Za-z0-9._:-]+", "-", text)
    text = text.strip("-._:")
    return text or None


def _extract_timestamp_from_value(value: Any, source_path: Path) -> dt.datetime | None:
    if isinstance(value, dict):
        for key in TIMESTAMP_KEYS:
            raw_value = value.get(key)
            if isinstance(raw_value, str):
                parsed = _parse_timestamp_candidate(raw_value, source_path)
                if parsed:
                    return parsed
    text = coerce_text(value)
    for parsed, _strategy in _collect_text_timestamp_candidates(text, source_path):
        return parsed
    return None


def _collect_text_timestamp_candidates(text: str, source_path: Path) -> list[tuple[dt.datetime, str]]:
    candidates: list[tuple[dt.datetime, str]] = []

    for match in ISO_TS_PATTERN.finditer(text):
        parsed = _parse_timestamp_candidate(match.group(1), source_path)
        if parsed:
            candidates.append((parsed, "text-iso"))

    for match in SLASH_TS_PATTERN.finditer(text):
        candidate = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        if match.group(4):
            candidate += f"T{match.group(4)}:{match.group(5)}:{match.group(6) or '00'}"
        parsed = _parse_timestamp_candidate(candidate, source_path)
        if parsed:
            candidates.append((parsed, "text-yyyy-slash"))

    for match in DMY_TS_PATTERN.finditer(text):
        day, month, year, hour, minute, second = match.groups()
        candidate = f"{year}-{month}-{day}"
        if hour:
            candidate += f"T{hour}:{minute}:{second or '00'}"
        parsed = _parse_timestamp_candidate(candidate, source_path)
        if parsed:
            candidates.append((parsed, "text-dmy"))

    if not candidates:
        date_hint = _extract_date_hint_from_filename(source_path)
        if date_hint:
            for match in TIME_ONLY_PATTERN.finditer(text):
                hour, minute, second = match.groups()
                candidate = f"{date_hint}T{hour}:{minute}:{second or '00'}"
                parsed = _parse_timestamp_candidate(candidate, source_path)
                if parsed:
                    candidates.append((parsed, "text-time-with-file-date"))
                    break

    if not candidates:
        for match in DATE_ONLY_PATTERN.finditer(text):
            parsed = _parse_timestamp_candidate(match.group(1), source_path)
            if parsed:
                candidates.append((parsed, "text-date-only"))
                break

    return candidates


def _parse_timestamp_candidate(raw_value: str, source_path: Path) -> dt.datetime | None:
    candidate = raw_value.strip()
    if not candidate:
        return None

    candidate = candidate.replace("/", "-")
    candidate = re.sub(r"\s+", "T", candidate)
    if re.fullmatch(r"20\d{2}-\d{2}-\d{2}", candidate):
        candidate = candidate + "T00:00:00"
    elif re.fullmatch(r"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}", candidate):
        candidate = candidate + ":00"
    elif re.fullmatch(r"\d{2}:\d{2}(?::\d{2})?", candidate):
        date_hint = _extract_date_hint_from_filename(source_path)
        if not date_hint:
            return None
        if len(candidate.split(":")) == 2:
            candidate = f"{date_hint}T{candidate}:00"
        else:
            candidate = f"{date_hint}T{candidate}"

    try:
        if candidate.endswith("Z"):
            parsed = dt.datetime.fromisoformat(candidate[:-1] + "+00:00")
        else:
            parsed = dt.datetime.fromisoformat(candidate)
    except ValueError:
        return None

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(dt.timezone.utc).replace(tzinfo=None)
    return parsed.replace(microsecond=0)


def _extract_date_hint_from_filename(source_path: Path) -> str | None:
    match = FILENAME_DATE_PATTERN.search(source_path.stem)
    if not match:
        return None
    return match.group(1).replace("_", "-")


def _timestamp_for_item(item: Any, source_path: Path, fallback: str) -> str:
    parsed = _extract_timestamp_from_value(item, source_path)
    return _isoformat_utc(parsed) if parsed else fallback


def _extract_line_timestamp(line: str, source_path: Path, fallback: str) -> str:
    for parsed, _strategy in _collect_text_timestamp_candidates(line, source_path):
        return _isoformat_utc(parsed)
    return fallback


def _isoformat_utc(value: dt.datetime) -> str:
    return value.replace(microsecond=0).isoformat() + "Z"


def _infer_event_category(text: str, default: str = "event") -> str:
    lowered = text.lower()
    if ERROR_TRIGGER_PATTERN.search(text):
        return "error"
    if WARNING_TRIGGER_PATTERN.search(text):
        return "warning"
    if "build" in lowered:
        return "build"
    if "test" in lowered or "pytest" in lowered:
        return "test"
    if _extract_tool_names(text):
        return "tool"
    if "start" in lowered or "begin" in lowered:
        return "start"
    if "finish" in lowered or "complete" in lowered or "done" in lowered:
        return "finish"
    return str(default or "event")


def _infer_error_type(text: str) -> str:
    match = EXCEPTION_NAME_PATTERN.search(text)
    if match:
        return match.group(1)
    exit_match = EXIT_CODE_PATTERN.search(text)
    if exit_match:
        return f"exit_code_{exit_match.group(1)}"
    lowered = text.lower()
    if "traceback" in lowered:
        return "traceback"
    if "segmentation fault" in lowered:
        return "segmentation_fault"
    if "fatal" in lowered:
        return "fatal_error"
    if "assert" in lowered:
        return "assertion_failure"
    if "fail" in lowered:
        return "failure"
    return "error"


def _infer_severity(text: str) -> str:
    lowered = text.lower()
    if "fatal" in lowered or "panic" in lowered or "segmentation fault" in lowered:
        return "fatal"
    if WARNING_TRIGGER_PATTERN.search(text):
        return "warning"
    return "error"


def _error_signature(text: str, error_type: str) -> str:
    base = semantic_text_normalize(text)
    base = re.sub(r"\bline\s+<n>\b", "line", base)
    return slugify(f"{error_type.lower()}-{semantic_text_fingerprint(base, max_tokens=12)}")


def _normalize_tool_name(value: str) -> str | None:
    text = value.strip()
    if not text:
        return None
    for pattern, canonical in TOOL_RULES:
        if pattern.search(text):
            return canonical
    token = text.split()[0].strip().lower()
    token = re.sub(r"[^a-z0-9+_.-]+", "", token)
    return token or None


def _extract_tool_names(text: str) -> list[str]:
    tools: list[str] = []
    seen: set[str] = set()
    for pattern, canonical in TOOL_RULES:
        if pattern.search(text) and canonical not in seen:
            seen.add(canonical)
            tools.append(canonical)
    return tools


def _first_tool_name(text: str) -> str | None:
    tools = _extract_tool_names(text)
    return tools[0] if tools else None



def _build_correlation_metadata(
    *,
    payload: Any,
    source_text: str,
    source_path: Path,
    record_timestamp: str,
    session_id: str,
    errors: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    summary: str,
) -> dict[str, Any]:
    stem_tokens = _extract_stem_tokens(source_path)
    signal_keywords = _extract_signal_keywords(source_text, summary)
    error_types = _unique_preserve([error.get("error_type", "") for error in errors if error.get("error_type")])
    tool_names = _unique_preserve([tool.get("tool_name", "") for tool in tools if tool.get("tool_name")])

    return {
        "date_bucket": record_timestamp[:10] if record_timestamp else None,
        "time_bucket": record_timestamp[:13] if len(record_timestamp) >= 13 else None,
        "source_family": _derive_source_family(source_path),
        "stem_tokens": stem_tokens,
        "signal_keywords": signal_keywords,
        "topic_tokens": keyword_tokens(summary + "\n" + source_text[:2000], max_tokens=10),
        "error_types": error_types,
        "error_signatures": _unique_preserve([error.get("error_signature", "") for error in errors if error.get("error_signature")]),
        "tool_names": tool_names,
        "summary_signature": semantic_text_fingerprint(summary or source_path.stem, max_tokens=10),
        "session_root": _session_root(session_id),
        "payload_shape": type(payload).__name__,
    }


def _extract_stem_tokens(source_path: Path) -> list[str]:
    parts = re.split(r"[^A-Za-z0-9]+", source_path.stem.lower())
    blacklist = {"log", "logs", "txt", "md", "report", "engine", "output", "trace", "run", "session"}
    tokens: list[str] = []
    for token in parts:
        if not token or token in blacklist:
            continue
        if re.fullmatch(r"20\d{2}|\d{2}|\d{8}", token):
            continue
        tokens.append(token)
    return _unique_preserve(tokens)


def _extract_signal_keywords(source_text: str, summary: str) -> list[str]:
    return keyword_tokens(f"{summary}\n{source_text[:4000]}", max_tokens=8)


def _derive_source_family(source_path: Path) -> str:
    tokens = _extract_stem_tokens(source_path)
    if not tokens:
        return slugify(source_path.stem.lower())
    return slugify("-".join(tokens[:2]))


def _session_root(session_id: str) -> str:
    base = session_id.strip().lower()
    if base.startswith("derived-"):
        base = base[len("derived-"):]
    for prefix in ("rollout-", "run-", "session-", "build-", "job-", "trace-", "request-"):
        if base.startswith(prefix):
            return prefix.rstrip("-")
    return slugify(base.split("-", 1)[0])


def _unique_preserve(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append(normalized)
    return out

def _dedupe_event_like(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (
            item.get("timestamp_utc", ""),
            item.get("category", ""),
            re.sub(r"\s+", " ", item.get("message", "").strip().lower())[:400],
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped
