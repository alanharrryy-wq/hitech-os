from __future__ import annotations

import ast
import difflib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from capatch_contracts.enums import REGEX_FLAG_NAMES


class CapatchError(Exception):
    """Error controlado del engine."""


@dataclass(slots=True)
class OperationExecution:
    target: Path
    original_content: str | None
    final_text: str | None
    message: str
    mutates_file: bool
    metadata: dict[str, Any] = field(default_factory=dict)


def fail(message: str) -> None:
    raise CapatchError(message)


def normalize_match_candidate(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized_lines = [" ".join(line.split()) for line in normalized.split("\n")]
    return "\n".join(normalized_lines).strip()


def normalize_trailing_spaces_per_line(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip(" \t") for line in normalized.split("\n")).strip()


def build_match_candidates(content: str, max_lines: int = 8, target_line_count: int | None = None, max_candidates: int = 2400) -> list[str]:
    lines = content.splitlines()
    if not lines:
        return []
    upper = min(max_lines, len(lines))
    if target_line_count is not None:
        sizes = sorted({size for delta in (-2, -1, 0, 1, 2) for size in [target_line_count + delta] if 1 <= size <= upper})
        if not sizes:
            sizes = list(range(1, upper + 1))
    else:
        sizes = list(range(1, upper + 1))
    base_step = max(1, len(lines) // 1200)
    seen: set[str] = set()
    candidates: list[str] = []
    for size in sizes:
        if len(lines) - size + 1 <= 0:
            continue
        step = max(1, base_step)
        for index in range(0, len(lines) - size + 1, step):
            candidate = "\n".join(lines[index:index + size]).strip()
            normalized_candidate = normalize_match_candidate(candidate)
            if not normalized_candidate or normalized_candidate in seen:
                continue
            seen.add(normalized_candidate)
            candidates.append(candidate)
            if len(candidates) >= max_candidates:
                return candidates
        last_index = len(lines) - size
        if last_index >= 0:
            candidate = "\n".join(lines[last_index:last_index + size]).strip()
            normalized_candidate = normalize_match_candidate(candidate)
            if normalized_candidate and normalized_candidate not in seen:
                seen.add(normalized_candidate)
                candidates.append(candidate)
                if len(candidates) >= max_candidates:
                    return candidates
    return candidates


def build_support_candidates(content: str, max_lines: int = 8, target_line_count: int | None = None, max_candidates: int = 3200) -> list[str]:
    lines = content.splitlines()
    if not lines:
        return []
    upper = min(max_lines, len(lines))
    if target_line_count is not None:
        sizes = sorted({size for delta in (-2, -1, 0, 1, 2) for size in [target_line_count + delta] if 1 <= size <= upper})
        if not sizes:
            sizes = list(range(1, upper + 1))
    else:
        sizes = list(range(1, upper + 1))
    base_step = max(1, len(lines) // 1200)
    candidates: list[str] = []
    seen: set[str] = set()
    for size in sizes:
        if len(lines) - size + 1 <= 0:
            continue
        step = max(1, base_step)
        for index in range(0, len(lines) - size + 1, step):
            candidate = "\n".join(lines[index:index + size])
            normalized_key = candidate.replace("\r\n", "\n").replace("\r", "\n")
            if not normalized_key.strip() or normalized_key in seen:
                continue
            seen.add(normalized_key)
            candidates.append(candidate)
            if len(candidates) >= max_candidates:
                return candidates
        last_index = len(lines) - size
        if last_index >= 0:
            candidate = "\n".join(lines[last_index:last_index + size])
            normalized_key = candidate.replace("\r\n", "\n").replace("\r", "\n")
            if normalized_key.strip() and normalized_key not in seen:
                seen.add(normalized_key)
                candidates.append(candidate)
                if len(candidates) >= max_candidates:
                    return candidates
    return candidates


def strip_outer_blank_lines(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    while lines and lines[0].strip() == "":
        lines = lines[1:]
    while lines and lines[-1].strip() == "":
        lines = lines[:-1]
    return "\n".join(lines)


def find_closest_match(content: str, needle: str) -> str | None:
    normalized_needle = normalize_match_candidate(needle)
    if not normalized_needle:
        return None
    needle_line_count = max(1, needle.count("\n") + 1)
    candidates = build_match_candidates(content, max_lines=max(needle_line_count + 2, 8), target_line_count=needle_line_count)
    if not candidates:
        return None
    best_score = 0.0
    best_candidate: str | None = None
    for candidate in candidates:
        normalized_candidate = normalize_match_candidate(candidate)
        score = difflib.SequenceMatcher(a=normalized_needle, b=normalized_candidate).ratio()
        if normalized_needle in normalized_candidate or normalized_candidate in normalized_needle:
            score += 0.15
        line_penalty = abs(needle_line_count - max(1, candidate.count("\n") + 1)) * 0.03
        score -= line_penalty
        if score > best_score:
            best_score = score
            best_candidate = candidate
    if best_score < 0.45:
        return None
    return best_candidate


def format_suggestion_preview(text: str, max_length: int = 220) -> str:
    preview = text.strip().replace("\n", "\\n")
    if len(preview) > max_length:
        return preview[: max_length - 3] + "..."
    return preview


def fail_not_found_with_suggestion(target: Path, content: str, needle: str, label: str, kind: str) -> None:
    suggestion = find_closest_match(content, needle)
    if suggestion is not None:
        fail(f"No encontre {kind} para: {label} en {target}. Sugerencia mas cercana: {format_suggestion_preview(suggestion)}")
    fail(f"No encontre {kind} para: {label} en {target}")


def compile_regex_flags(raw_flags: Any) -> int:
    if raw_flags is None:
        return 0
    if isinstance(raw_flags, str):
        flag_names = [part for part in re.split(r"[\s,|]+", raw_flags) if part]
    elif isinstance(raw_flags, list):
        flag_names = [str(part).strip() for part in raw_flags if str(part).strip()]
    else:
        fail("flags debe venir como string, lista o null.")
    mapping = {
        "ASCII": re.ASCII,
        "DOTALL": re.DOTALL,
        "IGNORECASE": re.IGNORECASE,
        "MULTILINE": re.MULTILINE,
        "VERBOSE": re.VERBOSE,
    }
    value = 0
    for name in flag_names:
        upper_name = name.upper()
        if upper_name not in mapping:
            supported = ", ".join(sorted(mapping))
            fail(f"Flag regex no soportado: {name}. Soportados: {supported}")
        value |= mapping[upper_name]
    return value


def validate_flag_value(flags: Any, label: str) -> None:
    if flags is None:
        return
    if isinstance(flags, str):
        parts = [part for part in re.split(r"[\s,|]+", flags) if part]
    elif isinstance(flags, list):
        parts = [str(part).strip() for part in flags if str(part).strip()]
    else:
        fail(f"flags invalido para {label}: debe ser string, lista o null.")
    for part in parts:
        if part.upper() not in REGEX_FLAG_NAMES:
            supported = ", ".join(sorted(REGEX_FLAG_NAMES))
            fail(f"Flag regex no soportado: {part}. Soportados: {supported}")


def validate_positive_intish(field_name: str, value: Any, label: str, allow_zero: bool = False) -> None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        fail(f"{field_name} invalido para {label}: {value}")
    if allow_zero:
        if parsed < 0:
            fail(f"{field_name} invalido para {label}: {parsed}")
    else:
        if parsed < 1:
            fail(f"{field_name} invalido para {label}: {parsed}")


def regex_replacement_uses_backrefs(new_text: str) -> bool:
    return re.search(r"\\[1-9]|\\g<", new_text) is not None


def regex_pattern_is_likely_complex(pattern: str) -> bool:
    return re.search(r"(?<!\\)[.^$*+?{}\[\]|()]|\\[AbBdDsSwWZ]", pattern) is not None


def python_literal(value: Any) -> str:
    return repr(value)


def ast_parse_with_message(content: str, target: Path) -> ast.AST:
    try:
        return ast.parse(content)
    except SyntaxError as exc:
        fail(f"Python invalido en {target}: {exc}")
