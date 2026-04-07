#!/usr/bin/env python3
"""
capatch.py

Motor de parches declarativos para editar archivos de un repo sin andar
pegando tijeretazos manuales. Pensado para ser simple de extender.

Mejoras vNext incluidas en esta version:
- dry-run consistente con su ayuda
- no-op writes evitados
- EnsureInsertAfterExact / EnsureInsertBeforeExact validan contexto local
- validacion temprana del esquema por tipo de operacion
- ejecucion unificada para preview y apply
- sugerencias de match mas acotadas para archivos grandes
- smoke test opcional
- EnsureReplaceRegexOnce admite confirmacion idempotente mas segura
- capa de auto-soporte para resolver desajustes minimos recuperables
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


DEFAULT_ROOT_DIR = Path(r"F:\repos\hitech-os\apps\code-atlas")
BACKUP_DIR_NAME = "_chatgpt_patch_backups"


class CapatchError(Exception):
    """Error controlado del motor."""


@dataclass(slots=True, frozen=True)
class PatchContext:
    root_dir: Path
    backup_dir: Path
    checkpoint_dir: Path
    dry_run: bool = False
    auto_support: bool = True


@dataclass(slots=True, frozen=True)
class OperationSpec:
    type: str
    label: str
    file: str
    payload: dict[str, Any]


@dataclass(slots=True)
class ExecutionResult:
    target: Path
    original_content: str | None
    final_text: str | None
    message: str
    mutates_file: bool


@dataclass(slots=True, frozen=True)
class SupportResolution:
    field_name: str
    original_value: str
    resolved_value: str
    strategy: str


class Operation:
    spec: OperationSpec

    def apply(self, ctx: PatchContext) -> str:
        raise NotImplementedError


MUTATING_OPERATION_TYPES = {
    "ReplaceLineRange",
    "DeleteLineRange",
    "InsertAtLine",
    "ReplaceExactOnce",
    "ReplaceExactMany",
    "EnsureReplaceExactOnce",
    "ReplaceNearestExact",
    "MoveBlockExactOnce",
    "ReplaceBetweenExactAnchors",
    "DeleteBetweenExactAnchors",
    "NormalizeFile",
    "DeleteExactOnce",
    "DeleteRegexMany",
    "DeleteRegexOnce",
    "EnsureInsertAfterExact",
    "EnsureInsertBeforeExact",
    "InsertAfterExact",
    "InsertBeforeExact",
    "ReplaceRegexOnce",
    "ReplaceRegexMany",
    "ReplaceRegexCount",
    "EnsureReplaceRegexOnce",
}

CONTENT_OPERATION_TYPES = MUTATING_OPERATION_TYPES | {
    "AssertContains",
    "AssertNotContains",
    "AssertRegexCount",
}

REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "ReplaceLineRange": ("start_line", "end_line"),
    "DeleteLineRange": ("start_line", "end_line"),
    "InsertAtLine": ("line_number",),
    "ReplaceExactOnce": ("old_text",),
    "ReplaceExactMany": ("old_text",),
    "EnsureReplaceExactOnce": ("old_text", "new_text"),
    "ReplaceNearestExact": ("old_text", "near_anchor"),
    "MoveBlockExactOnce": ("old_text", "anchor", "insert_position"),
    "ReplaceBetweenExactAnchors": ("start_anchor", "end_anchor"),
    "DeleteBetweenExactAnchors": ("start_anchor", "end_anchor"),
    "DeleteExactOnce": ("old_text",),
    "DeleteRegexMany": ("pattern",),
    "DeleteRegexOnce": ("pattern",),
    "AssertContains": ("text",),
    "AssertNotContains": ("text",),
    "AssertRegexCount": ("pattern", "expected_count"),
    "EnsureInsertAfterExact": ("anchor", "insert_text"),
    "EnsureInsertBeforeExact": ("anchor", "insert_text"),
    "InsertAfterExact": ("anchor", "insert_text"),
    "InsertBeforeExact": ("anchor", "insert_text"),
    "ReplaceRegexOnce": ("pattern",),
    "ReplaceRegexMany": ("pattern",),
    "ReplaceRegexCount": ("pattern", "expected_count"),
    "EnsureReplaceRegexOnce": ("pattern", "new_text"),
    "AssertFileExists": (),
    "AssertFileNotExists": (),
    "NormalizeFile": (),
    "ApplySet": ("operations",),
}

TEXT_FIELDS = {
    "file",
    "old_text",
    "new_text",
    "pattern",
    "anchor",
    "near_anchor",
    "start_anchor",
    "end_anchor",
    "text",
    "insert_text",
    "line_ending",
    "insert_position",
    "already_applied_text",
    "already_applied_regex",
}

INT_FIELDS = {
    "start_line",
    "end_line",
    "line_number",
    "expected_count",
}

FLAG_NAMES = {
    "ASCII",
    "DOTALL",
    "IGNORECASE",
    "MULTILINE",
    "VERBOSE",
}


class BaseOperation(Operation):
    def __init__(self, spec: OperationSpec) -> None:
        self.spec = spec

    @property
    def label(self) -> str:
        return self.spec.label or self.spec.type

    def target_path(self, ctx: PatchContext) -> Path:
        return resolve_target_path(ctx.root_dir, self.spec.file)

    def target_file(self, ctx: PatchContext) -> Path:
        return resolve_target_file(ctx.root_dir, self.spec.file)


class GenericOperation(BaseOperation):
    def apply(self, ctx: PatchContext) -> str:
        execution = execute_operation(ctx, self)
        return execution.message


class ApplySetOperation(BaseOperation):
    def __init__(self, spec: OperationSpec, operations: list[Operation]) -> None:
        super().__init__(spec)
        self.operations = operations

    def apply(self, ctx: PatchContext) -> str:
        for operation in self.operations:
            operation.apply(ctx)
        return f"{self.label}: ApplySet OK ({len(self.operations)} operacion(es))"


def info(message: str) -> None:
    print(f"[INFO] {message}")


def ok(message: str) -> None:
    print(f"[OK] {message}")


def fail(message: str) -> None:
    raise CapatchError(message)


def normalize_match_candidate(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized_lines = [" ".join(line.split()) for line in normalized.split("\n")]
    return "\n".join(normalized_lines).strip()


def build_match_candidates(
    content: str,
    max_lines: int = 8,
    target_line_count: int | None = None,
    max_candidates: int = 2400,
) -> list[str]:
    lines = content.splitlines()
    if not lines:
        return []

    upper = min(max_lines, len(lines))
    if target_line_count is not None:
        sizes = sorted(
            {
                size
                for delta in (-2, -1, 0, 1, 2)
                for size in [target_line_count + delta]
                if 1 <= size <= upper
            }
        )
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



def normalize_trailing_spaces_per_line(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip(" \t") for line in normalized.split("\n")).strip()


def build_support_candidates(
    content: str,
    max_lines: int = 8,
    target_line_count: int | None = None,
    max_candidates: int = 3200,
) -> list[str]:
    lines = content.splitlines()
    if not lines:
        return []

    upper = min(max_lines, len(lines))
    if target_line_count is not None:
        sizes = sorted(
            {
                size
                for delta in (-2, -1, 0, 1, 2)
                for size in [target_line_count + delta]
                if 1 <= size <= upper
            }
        )
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
            if not normalized_key.strip():
                continue
            if normalized_key in seen:
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


def find_support_resolution(content: str, field_name: str, needle: str) -> SupportResolution | None:
    if needle == "":
        return None

    needle_line_count = max(1, needle.count("\n") + 1)
    candidates = build_support_candidates(
        content,
        max_lines=max(needle_line_count + 2, 8),
        target_line_count=needle_line_count,
        max_candidates=3200,
    )
    if not candidates:
        return None

    strategies: list[tuple[str, Any]] = [
        ("trim_bordes", lambda value: value.strip()),
        ("rstrip_por_linea", normalize_trailing_spaces_per_line),
        ("blank_lines_borde", strip_outer_blank_lines),
        ("whitespace_colapsado", normalize_match_candidate),
    ]

    for strategy_name, normalizer in strategies:
        normalized_needle = normalizer(needle)
        if normalized_needle == "":
            continue

        matches: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            if normalizer(candidate) != normalized_needle:
                continue
            if candidate in seen:
                continue
            seen.add(candidate)
            if content.count(candidate) != 1:
                continue
            matches.append(candidate)

        if len(matches) == 1:
            candidate = matches[0]
            if candidate != needle:
                return SupportResolution(
                    field_name=field_name,
                    original_value=needle,
                    resolved_value=candidate,
                    strategy=strategy_name,
                )

    return None

def has_partial_whitespace_overlap(content: str, needle: str) -> bool:
    if needle == "":
        return False

    first = content.find(needle)
    if first < 0:
        return False

    second = content.find(needle, first + len(needle))
    if second >= 0:
        return False

    before = content[first - 1] if first > 0 else ""
    after_index = first + len(needle)
    after = content[after_index] if after_index < len(content) else ""

    return before in {" ", "\t"} or after in {" ", "\t"}




SUPPORT_FIELDS_BY_OPERATION: dict[str, tuple[str, ...]] = {
    "ReplaceExactOnce": ("old_text",),
    "ReplaceExactMany": ("old_text",),
    "EnsureReplaceExactOnce": ("old_text",),
    "ReplaceNearestExact": ("old_text", "near_anchor"),
    "MoveBlockExactOnce": ("old_text", "anchor"),
    "ReplaceBetweenExactAnchors": ("start_anchor", "end_anchor"),
    "DeleteBetweenExactAnchors": ("start_anchor", "end_anchor"),
    "DeleteExactOnce": ("old_text",),
    "InsertAfterExact": ("anchor",),
    "EnsureInsertAfterExact": ("anchor",),
    "InsertBeforeExact": ("anchor",),
    "EnsureInsertBeforeExact": ("anchor",),
    "AssertContains": ("text",),
}


def materialize_support_payload(
    ctx: PatchContext,
    target: Path,
    content: str,
    operation: BaseOperation,
) -> tuple[dict[str, Any], list[str]]:
    if not ctx.auto_support:
        return dict(operation.spec.payload), []

    payload = dict(operation.spec.payload)
    notes: list[str] = []

    preferred_partial_strategies = {"rstrip_por_linea", "blank_lines_borde"}

    for field_name in SUPPORT_FIELDS_BY_OPERATION.get(operation.spec.type, ()):
        raw_value = payload.get(field_name)
        if raw_value is None:
            continue

        field_value = str(raw_value)
        resolution = find_support_resolution(content, field_name, field_value)
        if resolution is None:
            continue

        should_apply = field_value not in content
        if not should_apply and resolution.strategy in preferred_partial_strategies:
            should_apply = True
        if not should_apply and resolution.strategy == "trim_bordes" and has_partial_whitespace_overlap(content, field_value):
            should_apply = True

        if not should_apply:
            continue

        payload[field_name] = resolution.resolved_value
        notes.append(
            f"{field_name}:{resolution.strategy} ({format_suggestion_preview(field_value)} -> "
            f"{format_suggestion_preview(resolution.resolved_value)})"
        )

    return payload, notes


def format_suggestion_preview(text: str, max_length: int = 220) -> str:
    preview = text.strip().replace("\n", "\\n")
    if len(preview) > max_length:
        return preview[: max_length - 3] + "..."
    return preview


def find_closest_match(content: str, needle: str) -> str | None:
    normalized_needle = normalize_match_candidate(needle)
    if not normalized_needle:
        return None

    needle_line_count = max(1, needle.count("\n") + 1)
    candidates = build_match_candidates(
        content,
        max_lines=max(needle_line_count + 2, 8),
        target_line_count=needle_line_count,
    )
    if not candidates:
        return None

    best_score = 0.0
    best_candidate: str | None = None

    for candidate in candidates:
        normalized_candidate = normalize_match_candidate(candidate)
        score = difflib.SequenceMatcher(
            a=normalized_needle,
            b=normalized_candidate,
        ).ratio()

        if (
            normalized_needle in normalized_candidate
            or normalized_candidate in normalized_needle
        ):
            score += 0.15

        line_penalty = abs(needle_line_count - max(1, candidate.count("\n") + 1)) * 0.03
        score -= line_penalty

        if score > best_score:
            best_score = score
            best_candidate = candidate

    if best_score < 0.45:
        return None
    return best_candidate


def fail_not_found_with_suggestion(
    target: Path,
    content: str,
    needle: str,
    label: str,
    kind: str,
) -> None:
    suggestion = find_closest_match(content, needle)
    if suggestion is not None:
        fail(
            f"No encontre {kind} para: {label} en {target}. "
            f"Sugerencia mas cercana: {format_suggestion_preview(suggestion)}"
        )
    fail(f"No encontre {kind} para: {label} en {target}")


def ensure_path_within_root(root_dir: Path, path_value: Path) -> None:
    root_resolved = root_dir.resolve()
    path_resolved = path_value.resolve()

    try:
        path_resolved.relative_to(root_resolved)
    except ValueError:
        fail(
            f"La ruta objetivo se sale de root_dir: {path_resolved} "
            f"(root_dir: {root_resolved})"
        )


def ensure_directory(path_value: Path) -> None:
    if not path_value.exists():
        fail(f"No existe la ruta: {path_value}")
    if not path_value.is_dir():
        fail(f"La ruta no es carpeta: {path_value}")


def resolve_target_path(base_dir: Path, relative_file: str) -> Path:
    relative = (relative_file or "").strip()
    if not relative:
        fail("La operacion no trae file.")

    target = (base_dir / relative).resolve()
    ensure_path_within_root(base_dir, target)
    return target


def resolve_target_file(base_dir: Path, relative_file: str) -> Path:
    target = resolve_target_path(base_dir, relative_file)
    if not target.exists():
        fail(f"No encontre el archivo objetivo: {target}")
    if not target.is_file():
        fail(f"Se esperaba archivo, no carpeta: {target}")
    return target


def read_file_utf8(path_value: Path) -> str:
    return path_value.read_text(encoding="utf-8")


def write_file_utf8_no_bom(path_value: Path, content: str) -> None:
    path_value.write_text(content, encoding="utf-8", newline="")


def write_file_if_changed(path_value: Path, original_content: str, final_text: str) -> bool:
    if original_content == final_text:
        return False
    write_file_utf8_no_bom(path_value, final_text)
    return True


def sanitize_checkpoint_label(raw_value: str | None) -> str:
    label = (raw_value or "").strip()
    if not label:
        label = datetime.now().strftime("session_%Y%m%d_%H%M%S")

    safe = "".join(
        char if char.isalnum() or char in {"-", "_", "."} else "_"
        for char in label
    ).strip("._")
    return safe or datetime.now().strftime("session_%Y%m%d_%H%M%S")


def make_checkpoint_backup(path_value: Path, checkpoint_root: Path, root_dir: Path) -> Path:
    ensure_path_within_root(root_dir, path_value)
    relative_path = path_value.resolve().relative_to(root_dir.resolve())
    backup_path = checkpoint_root / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path_value, backup_path)
    return backup_path


def render_replace_nearest_exact(
    target: Path,
    content: str,
    old_text: str,
    new_text: str,
    near_anchor: str,
    label: str,
) -> str:
    if old_text == "":
        fail(f"old_text no puede venir vacio para {label} en {target}")

    anchor_first = content.find(near_anchor)
    if anchor_first < 0:
        fail_not_found_with_suggestion(target, content, near_anchor, label, "near_anchor")

    anchor_second = content.find(near_anchor, anchor_first + len(near_anchor))
    if anchor_second >= 0:
        fail(f"near_anchor para {label} aparece mas de una vez en {target}")

    positions: list[int] = []
    search_from = 0
    step = max(len(old_text), 1)

    while True:
        position = content.find(old_text, search_from)
        if position < 0:
            break
        positions.append(position)
        search_from = position + step

    if not positions:
        fail_not_found_with_suggestion(target, content, old_text, label, "el bloque exacto")

    best_position = min(positions, key=lambda pos: (abs(pos - anchor_first), pos))
    return content[:best_position] + new_text + content[best_position + len(old_text):]


def render_assert_file_exists(target: Path, label: str) -> None:
    if not target.exists():
        fail(f"No existe el archivo requerido para: {label} en {target}")
    if not target.is_file():
        fail(f"Se esperaba archivo para: {label}, no carpeta: {target}")


def render_assert_file_not_exists(target: Path, label: str) -> None:
    if target.exists():
        fail(f"El archivo no deberia existir para: {label} en {target}")


def flatten_operations(operations: Iterable[Operation]) -> list[Operation]:
    flattened: list[Operation] = []
    for operation in operations:
        if isinstance(operation, ApplySetOperation):
            flattened.extend(flatten_operations(operation.operations))
        else:
            flattened.append(operation)
    return flattened


def operation_writes_file(operation: Operation) -> bool:
    return operation.spec.type in MUTATING_OPERATION_TYPES


def count_mutating_ops_for_target(
    ctx: PatchContext,
    operations: Iterable[Operation],
    target: Path,
) -> int:
    count = 0
    for operation in flatten_operations(operations):
        if not operation_writes_file(operation):
            continue
        if resolve_target_file(ctx.root_dir, operation.spec.file) == target:
            count += 1
    return count


def build_preview_diff_summary(
    ctx: PatchContext,
    operations: Iterable[Operation],
    preview_content_by_target: dict[Path, str],
) -> list[str]:
    summaries: list[str] = []

    for target in sorted(preview_content_by_target):
        original = read_file_utf8(target)
        final = preview_content_by_target[target]
        if original == final:
            continue

        line_delta = len(final.splitlines()) - len(original.splitlines())
        char_delta = len(final) - len(original)
        op_count = count_mutating_ops_for_target(ctx, operations, target)
        relative = target.resolve().relative_to(ctx.root_dir.resolve()).as_posix()
        summaries.append(
            f"{relative} | ops={op_count} | line_delta={line_delta:+d} | char_delta={char_delta:+d}"
        )

    if not summaries:
        summaries.append("sin cambios materiales.")

    return summaries


def simulate_operations_with_state(
    ctx: PatchContext,
    operations: Iterable[Operation],
) -> tuple[list[str], dict[Path, str]]:
    results: list[str] = []
    content_by_target: dict[Path, str] = {}

    for operation in operations:
        result = simulate_operation(ctx, operation, content_by_target)
        results.append(result)

    return results, content_by_target


def build_session_checkpoints(
    ctx: PatchContext,
    operations: Iterable[Operation],
) -> dict[Path, Path]:
    ctx.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoints: dict[Path, Path] = {}

    for operation in flatten_operations(operations):
        if not operation_writes_file(operation):
            continue
        target = resolve_target_file(ctx.root_dir, operation.spec.file)
        if target not in checkpoints:
            backup = make_checkpoint_backup(target, ctx.checkpoint_dir, ctx.root_dir)
            checkpoints[target] = backup

    return checkpoints


def restore_session_checkpoints(checkpoints: dict[Path, Path]) -> list[Path]:
    restored: list[Path] = []
    for target, backup in checkpoints.items():
        shutil.copy2(backup, target)
        restored.append(target)
    return restored


def render_replace_line_range(
    target: Path,
    content: str,
    start_line: int,
    end_line: int,
    new_text: str,
) -> str:
    if start_line < 1 or end_line < start_line:
        fail(f"Rango invalido en {target}: {start_line}-{end_line}")

    lines = content.splitlines()
    if end_line > len(lines):
        fail(
            f"El rango {start_line}-{end_line} se sale del archivo "
            f"({len(lines)} lineas): {target}"
        )

    before = lines[: start_line - 1]
    after = lines[end_line:]
    replacement = new_text.splitlines() if new_text else []
    final_lines = before + replacement + after
    final_text = "\n".join(final_lines)
    if content.endswith("\n"):
        final_text += "\n"
    return final_text


def render_delete_line_range(
    target: Path,
    content: str,
    start_line: int,
    end_line: int,
) -> str:
    return render_replace_line_range(target, content, start_line, end_line, "")


def render_replace_exact_once(
    target: Path,
    content: str,
    old_text: str,
    new_text: str,
    label: str,
) -> str:
    first = content.find(old_text)
    if first < 0:
        fail_not_found_with_suggestion(target, content, old_text, label, "el bloque exacto")

    second = content.find(old_text, first + len(old_text))
    if second >= 0:
        fail(f"El bloque exacto para {label} aparece mas de una vez en {target}")

    return content.replace(old_text, new_text)


def render_delete_exact_once(
    target: Path,
    content: str,
    old_text: str,
    label: str,
) -> str:
    return render_replace_exact_once(target, content, old_text, "", label)


def render_insert_after_exact(
    target: Path,
    content: str,
    anchor: str,
    insert_text: str,
    label: str,
) -> str:
    first = content.find(anchor)
    if first < 0:
        fail_not_found_with_suggestion(target, content, anchor, label, "el ancla")

    second = content.find(anchor, first + len(anchor))
    if second >= 0:
        fail(f"El ancla para {label} aparece mas de una vez en {target}")

    pos = first + len(anchor)
    return content[:pos] + insert_text + content[pos:]


def render_insert_before_exact(
    target: Path,
    content: str,
    anchor: str,
    insert_text: str,
    label: str,
) -> str:
    first = content.find(anchor)
    if first < 0:
        fail_not_found_with_suggestion(target, content, anchor, label, "el ancla")

    second = content.find(anchor, first + len(anchor))
    if second >= 0:
        fail(f"El ancla para {label} aparece mas de una vez en {target}")

    return content[:first] + insert_text + content[first:]


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


def render_replace_regex_once(
    target: Path,
    content: str,
    pattern: str,
    new_text: str,
    label: str,
    raw_flags: Any,
) -> str:
    try:
        regex = re.compile(pattern, compile_regex_flags(raw_flags))
    except re.error as exc:
        fail(f"Regex invalido para {label} en {target}: {exc}")

    matches = list(regex.finditer(content))
    if not matches:
        fail(f"No encontre regex para: {label} en {target}")
    if len(matches) > 1:
        fail(f"El regex para {label} aparece mas de una vez en {target}")

    return regex.sub(new_text, content, count=1)


def render_replace_regex_many(
    target: Path,
    content: str,
    pattern: str,
    new_text: str,
    label: str,
    raw_flags: Any,
    expected_count: Any,
) -> tuple[str, int]:
    try:
        regex = re.compile(pattern, compile_regex_flags(raw_flags))
    except re.error as exc:
        fail(f"Regex invalido para {label} en {target}: {exc}")

    matches = list(regex.finditer(content))
    actual_count = len(matches)

    if actual_count == 0:
        fail(f"No encontre regex para: {label} en {target}")

    if expected_count is not None:
        expected = int(expected_count)
        if expected < 1:
            fail(f"expected_count invalido para {label} en {target}: {expected}")
        if actual_count != expected:
            fail(
                f"El regex para {label} esperaba {expected} coincidencia(s) "
                f"y encontro {actual_count} en {target}"
            )

    return regex.sub(new_text, content), actual_count


def render_delete_regex_many(
    target: Path,
    content: str,
    pattern: str,
    label: str,
    raw_flags: Any,
    expected_count: Any,
) -> tuple[str, int]:
    return render_replace_regex_many(
        target,
        content,
        pattern,
        "",
        label,
        raw_flags,
        expected_count,
    )


def render_assert_contains(
    target: Path,
    content: str,
    text: str,
    label: str,
) -> str:
    if text not in content:
        fail_not_found_with_suggestion(target, content, text, label, "el texto requerido")
    return content


def render_assert_not_contains(
    target: Path,
    content: str,
    text: str,
    label: str,
) -> str:
    if text in content:
        fail(f"Se encontro texto prohibido para: {label} en {target}")
    return content


def render_assert_regex_count(
    target: Path,
    content: str,
    pattern: str,
    label: str,
    raw_flags: Any,
    expected_count: Any,
) -> tuple[str, int]:
    if expected_count is None:
        fail(f"expected_count es requerido para {label} en {target}")

    try:
        expected = int(expected_count)
    except (TypeError, ValueError):
        fail(f"expected_count invalido para {label} en {target}: {expected_count}")

    if expected < 0:
        fail(f"expected_count invalido para {label} en {target}: {expected}")

    try:
        regex = re.compile(pattern, compile_regex_flags(raw_flags))
    except re.error as exc:
        fail(f"Regex invalido para {label} en {target}: {exc}")

    actual_count = len(list(regex.finditer(content)))
    if actual_count != expected:
        fail(
            f"El regex para {label} esperaba {expected} coincidencia(s) "
            f"y encontro {actual_count} en {target}"
        )

    return content, actual_count


def render_ensure_insert_after_exact(
    target: Path,
    content: str,
    anchor: str,
    insert_text: str,
    label: str,
) -> str:
    if insert_text == "":
        return content

    first = content.find(anchor)
    if first < 0:
        fail_not_found_with_suggestion(target, content, anchor, label, "el ancla")

    second = content.find(anchor, first + len(anchor))
    if second >= 0:
        fail(f"El ancla para {label} aparece mas de una vez en {target}")

    pos = first + len(anchor)
    if content[pos:pos + len(insert_text)] == insert_text:
        return content

    if insert_text in content:
        fail(
            f"El bloque para {label} ya existe en {target}, pero no esta inmediatamente "
            f"despues del ancla. Estado ambiguo."
        )

    return content[:pos] + insert_text + content[pos:]


def render_ensure_insert_before_exact(
    target: Path,
    content: str,
    anchor: str,
    insert_text: str,
    label: str,
) -> str:
    if insert_text == "":
        return content

    first = content.find(anchor)
    if first < 0:
        fail_not_found_with_suggestion(target, content, anchor, label, "el ancla")

    second = content.find(anchor, first + len(anchor))
    if second >= 0:
        fail(f"El ancla para {label} aparece mas de una vez en {target}")

    start = max(0, first - len(insert_text))
    if content[start:first] == insert_text:
        return content

    if insert_text in content:
        fail(
            f"El bloque para {label} ya existe en {target}, pero no esta inmediatamente "
            f"antes del ancla. Estado ambiguo."
        )

    return content[:first] + insert_text + content[first:]


def render_delete_regex_once(
    target: Path,
    content: str,
    pattern: str,
    label: str,
    raw_flags: Any,
) -> str:
    final_text, _ = render_delete_regex_many(
        target,
        content,
        pattern,
        label,
        raw_flags,
        1,
    )
    return final_text


def render_replace_exact_many(
    target: Path,
    content: str,
    old_text: str,
    new_text: str,
    label: str,
    expected_count: Any,
) -> tuple[str, int]:
    if old_text == "":
        fail(f"old_text no puede venir vacio para {label} en {target}")

    actual_count = content.count(old_text)
    if actual_count == 0:
        fail_not_found_with_suggestion(target, content, old_text, label, "el bloque exacto")

    if expected_count is not None:
        expected = int(expected_count)
        if expected < 1:
            fail(f"expected_count invalido para {label} en {target}: {expected}")
        if actual_count != expected:
            fail(
                f"El bloque exacto para {label} esperaba {expected} coincidencia(s) "
                f"y encontro {actual_count} en {target}"
            )

    return content.replace(old_text, new_text), actual_count


def render_replace_between_exact_anchors(
    target: Path,
    content: str,
    start_anchor: str,
    end_anchor: str,
    new_text: str,
    label: str,
) -> str:
    start_first = content.find(start_anchor)
    if start_first < 0:
        fail_not_found_with_suggestion(target, content, start_anchor, label, "start_anchor")

    start_second = content.find(start_anchor, start_first + len(start_anchor))
    if start_second >= 0:
        fail(f"start_anchor para {label} aparece mas de una vez en {target}")

    end_first = content.find(end_anchor)
    if end_first < 0:
        fail_not_found_with_suggestion(target, content, end_anchor, label, "end_anchor")

    end_second = content.find(end_anchor, end_first + len(end_anchor))
    if end_second >= 0:
        fail(f"end_anchor para {label} aparece mas de una vez en {target}")

    start_pos = start_first + len(start_anchor)
    end_pos = end_first

    if end_pos < start_pos:
        fail(f"Las anclas para {label} estan fuera de orden o se traslapan en {target}")

    return content[:start_pos] + new_text + content[end_pos:]


def render_normalize_file(
    target: Path,
    content: str,
    label: str,
    line_ending: Any,
    ensure_final_newline: Any,
    strip_trailing_spaces: Any,
) -> str:
    normalized_line_ending = str(line_ending or "LF").upper()
    if normalized_line_ending == "LF":
        separator = "\n"
    elif normalized_line_ending == "CRLF":
        separator = "\r\n"
    else:
        fail(
            f"line_ending invalido para {label} en {target}: {line_ending}. "
            f"Soportados: LF, CRLF"
        )

    final_newline = True if ensure_final_newline is None else bool(ensure_final_newline)
    trim_spaces = False if strip_trailing_spaces is None else bool(strip_trailing_spaces)

    if content == "":
        return ""

    lines = content.splitlines()
    if trim_spaces:
        lines = [line.rstrip(" \t") for line in lines]

    final_text = separator.join(lines)
    if final_newline:
        final_text += separator

    return final_text


def render_replace_regex_count(
    target: Path,
    content: str,
    pattern: str,
    new_text: str,
    label: str,
    raw_flags: Any,
    expected_count: Any,
) -> tuple[str, int]:
    if expected_count is None:
        fail(f"expected_count es requerido para {label} en {target}")

    return render_replace_regex_many(
        target,
        content,
        pattern,
        new_text,
        label,
        raw_flags,
        expected_count,
    )


def render_ensure_replace_exact_once(
    target: Path,
    content: str,
    old_text: str,
    new_text: str,
    label: str,
) -> tuple[str, str]:
    if old_text == "":
        fail(f"old_text no puede venir vacio para {label} en {target}")
    if new_text == "":
        fail(
            f"new_text no puede venir vacio para {label} en {target}. "
            f"Usa DeleteExactOnce si quieres borrar."
        )
    if old_text == new_text:
        return content, "ya estaba aplicado"

    old_count = content.count(old_text)
    new_count = content.count(new_text)

    if old_count == 0:
        if new_count == 1:
            suggestion = find_closest_match(content, old_text)
            if suggestion is None or normalize_match_candidate(suggestion) == normalize_match_candidate(new_text):
                return content, "ya estaba aplicado"
            fail(
                f"No encontre el bloque viejo para {label} en {target}, pero el bloque nuevo ya existe "
                f"y hay un candidato parecido al bloque viejo. Estado ambiguo."
            )
        if new_count > 1:
            fail(f"El bloque nuevo para {label} aparece mas de una vez en {target}")
        fail_not_found_with_suggestion(target, content, old_text, label, "el bloque exacto")

    if old_count > 1:
        fail(f"El bloque exacto para {label} aparece mas de una vez en {target}")

    if new_count > 1:
        fail(f"El bloque nuevo para {label} aparece mas de una vez en {target}")

    if new_count == 1:
        fail(f"El bloque viejo y el bloque nuevo ya conviven para {label} en {target}")

    return content.replace(old_text, new_text), "reemplazo aplicado"


def render_ensure_replace_regex_once(
    target: Path,
    content: str,
    pattern: str,
    new_text: str,
    label: str,
    raw_flags: Any,
    already_applied_text: str | None = None,
    already_applied_regex: str | None = None,
) -> tuple[str, str]:
    if new_text == "":
        fail(
            f"new_text no puede venir vacio para {label} en {target}. "
            f"Usa DeleteRegexOnce si quieres borrar."
        )

    try:
        regex = re.compile(pattern, compile_regex_flags(raw_flags))
    except re.error as exc:
        fail(f"Regex invalido para {label} en {target}: {exc}")

    matches = list(regex.finditer(content))
    literal_new_count = content.count(new_text)
    applied_text = (already_applied_text or "").strip()
    applied_regex = (already_applied_regex or "").strip()

    if not matches:
        if applied_text:
            applied_text_count = content.count(applied_text)
            if applied_text_count == 1:
                return content, "ya estaba aplicado"
            if applied_text_count > 1:
                fail(
                    f"already_applied_text para {label} aparece mas de una vez en {target}"
                )

        if applied_regex:
            try:
                applied_regex_compiled = re.compile(
                    applied_regex,
                    compile_regex_flags(raw_flags),
                )
            except re.error as exc:
                fail(f"already_applied_regex invalido para {label} en {target}: {exc}")

            applied_matches = list(applied_regex_compiled.finditer(content))
            if len(applied_matches) == 1:
                return content, "ya estaba aplicado"
            if len(applied_matches) > 1:
                fail(
                    f"already_applied_regex para {label} aparece mas de una vez en {target}"
                )

        if literal_new_count > 1:
            fail(f"El texto nuevo para {label} aparece mas de una vez en {target}")

        if literal_new_count == 1:
            if regex_replacement_uses_backrefs(new_text) or regex_pattern_is_likely_complex(pattern):
                fail(
                    f"No encontre regex para: {label} en {target}, pero el texto nuevo ya existe "
                    f"una vez. No puedo confirmar idempotencia de forma segura con este patron. "
                    f"Usa already_applied_text o already_applied_regex."
                )
            return content, "ya estaba aplicado"

        fail(f"No encontre regex para: {label} en {target}")

    if len(matches) > 1:
        fail(f"El regex para {label} aparece mas de una vez en {target}")

    prospective_text = regex.sub(new_text, content, count=1)
    if prospective_text == content:
        return content, "ya estaba aplicado"

    if literal_new_count > 1:
        fail(f"El texto nuevo para {label} aparece mas de una vez en {target}")

    if literal_new_count == 1:
        fail(f"El regex viejo y el texto nuevo ya conviven para {label} en {target}")

    return prospective_text, "reemplazo aplicado"


def render_move_block_exact_once(
    target: Path,
    content: str,
    old_text: str,
    anchor: str,
    insert_position: Any,
    label: str,
) -> str:
    if old_text == "":
        fail(f"old_text no puede venir vacio para {label} en {target}")

    normalized_position = str(insert_position or "").strip().lower()
    if normalized_position not in {"before", "after"}:
        fail(
            f"insert_position invalido para {label} en {target}: {insert_position}. "
            f"Soportados: before, after"
        )

    first = content.find(old_text)
    if first < 0:
        fail_not_found_with_suggestion(target, content, old_text, label, "el bloque exacto")

    second = content.find(old_text, first + len(old_text))
    if second >= 0:
        fail(f"El bloque exacto para {label} aparece mas de una vez en {target}")

    without_block = content[:first] + content[first + len(old_text):]
    if normalized_position == "before":
        return render_insert_before_exact(target, without_block, anchor, old_text, label)
    return render_insert_after_exact(target, without_block, anchor, old_text, label)


def render_delete_between_exact_anchors(
    target: Path,
    content: str,
    start_anchor: str,
    end_anchor: str,
    label: str,
) -> str:
    return render_replace_between_exact_anchors(
        target,
        content,
        start_anchor,
        end_anchor,
        "",
        label,
    )


def render_insert_at_line(
    target: Path,
    content: str,
    line_number: int,
    insert_text: str,
    label: str,
) -> str:
    if line_number < 1:
        fail(f"line_number invalido para {label} en {target}: {line_number}")

    lines = content.splitlines(keepends=True)
    max_allowed = len(lines) + 1
    if line_number > max_allowed:
        fail(
            f"line_number invalido para {label} en {target}: {line_number}. "
            f"Maximo permitido: {max_allowed}"
        )

    if insert_text == "":
        return content

    position = sum(len(line) for line in lines[: line_number - 1])
    return content[:position] + insert_text + content[position:]


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
        if part.upper() not in FLAG_NAMES:
            supported = ", ".join(sorted(FLAG_NAMES))
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


def validate_optional_already_applied_markers(
    label: str,
    payload: dict[str, Any],
) -> None:
    has_text = bool(str(payload.get("already_applied_text") or ""))
    has_regex = bool(str(payload.get("already_applied_regex") or ""))
    if has_text and has_regex:
        fail(
            f"La operacion {label} no debe traer already_applied_text y "
            f"already_applied_regex al mismo tiempo."
        )


def validate_operation_payload(op_type: str, label: str, file_value: str, payload: dict[str, Any]) -> None:
    if op_type != "ApplySet" and not file_value:
        fail(f"La operacion {label or op_type} no trae file.")

    required = REQUIRED_FIELDS.get(op_type)
    if required is None:
        supported = ", ".join(sorted(REQUIRED_FIELDS))
        fail(f"Tipo de operacion no soportado: {op_type}. Soportados: {supported}")

    for field_name in required:
        if field_name not in payload:
            fail(f"La operacion {label or op_type} requiere {field_name}.")

    for key, value in payload.items():
        if key in TEXT_FIELDS and value is not None and not isinstance(value, str):
            fail(f"{key} invalido para {label or op_type}: debe ser string o null.")
        if key in INT_FIELDS and value is not None:
            try:
                int(value)
            except (TypeError, ValueError):
                fail(f"{key} invalido para {label or op_type}: {value}")

    if "start_line" in payload:
        validate_positive_intish("start_line", payload["start_line"], label or op_type)
    if "end_line" in payload:
        validate_positive_intish("end_line", payload["end_line"], label or op_type)
        if "start_line" in payload and int(payload["end_line"]) < int(payload["start_line"]):
            fail(f"Rango invalido para {label or op_type}: end_line < start_line")
    if "line_number" in payload:
        validate_positive_intish("line_number", payload["line_number"], label or op_type)
    if "expected_count" in payload and payload["expected_count"] is not None:
        validate_positive_intish(
            "expected_count",
            payload["expected_count"],
            label or op_type,
            allow_zero=(op_type == "AssertRegexCount"),
        )

    if "flags" in payload:
        validate_flag_value(payload.get("flags"), label or op_type)

    if op_type == "EnsureReplaceRegexOnce":
        validate_optional_already_applied_markers(label or op_type, payload)

    if op_type == "ApplySet":
        raw_operations = payload.get("operations")
        if not isinstance(raw_operations, list) or not raw_operations:
            fail(f"La operacion {label or op_type} debe traer operations como lista no vacia.")

    if op_type == "MoveBlockExactOnce":
        insert_position = str(payload.get("insert_position", "")).strip().lower()
        if insert_position not in {"before", "after"}:
            fail(
                f"insert_position invalido para {label or op_type}: {payload.get('insert_position')}. "
                f"Soportados: before, after"
            )

    if op_type == "NormalizeFile" and payload.get("line_ending") is not None:
        line_ending = str(payload.get("line_ending", "")).upper()
        if line_ending not in {"LF", "CRLF"}:
            fail(
                f"line_ending invalido para {label or op_type}: {payload.get('line_ending')}. "
                f"Soportados: LF, CRLF"
            )

    non_empty_fields = {
        "old_text",
        "pattern",
        "anchor",
        "near_anchor",
        "start_anchor",
        "end_anchor",
        "text",
    }
    for field_name in non_empty_fields:
        if field_name in payload and str(payload[field_name]) == "":
            fail(f"{field_name} no puede venir vacio para {label or op_type}.")


def execute_single_operation(
    ctx: PatchContext,
    target: Path,
    content: str | None,
    operation: BaseOperation,
) -> ExecutionResult:
    op_type = operation.spec.type
    payload = operation.spec.payload

    if op_type == "AssertFileExists":
        render_assert_file_exists(target, operation.label)
        return ExecutionResult(target, None, None, f"{target.name}: assert file exists OK", False)

    if op_type == "AssertFileNotExists":
        render_assert_file_not_exists(target, operation.label)
        return ExecutionResult(target, None, None, f"{target.name}: assert file not exists OK", False)

    if content is None:
        fail(f"No hay contenido cargado para {operation.label} en {target}")

    payload, support_notes = materialize_support_payload(ctx, target, content, operation)

    if op_type == "ReplaceLineRange":
        start_line = int(payload["start_line"])
        end_line = int(payload["end_line"])
        new_text = str(payload.get("new_text", ""))
        final_text = render_replace_line_range(target, content, start_line, end_line, new_text)
        message = f"{target.name}: reemplazadas lineas {start_line}-{end_line}"
    elif op_type == "DeleteLineRange":
        start_line = int(payload["start_line"])
        end_line = int(payload["end_line"])
        final_text = render_delete_line_range(target, content, start_line, end_line)
        message = f"{target.name}: borradas lineas {start_line}-{end_line}"
    elif op_type == "InsertAtLine":
        line_number = int(payload["line_number"])
        insert_text = str(payload.get("insert_text", ""))
        final_text = render_insert_at_line(target, content, line_number, insert_text, operation.label)
        message = f"{target.name}: insercion aplicada en linea {line_number}"
    elif op_type == "ReplaceExactOnce":
        old_text = str(payload["old_text"])
        new_text = str(payload.get("new_text", ""))
        final_text = render_replace_exact_once(target, content, old_text, new_text, operation.label)
        message = f"{target.name}: reemplazo exacto aplicado"
    elif op_type == "EnsureReplaceExactOnce":
        old_text = str(payload["old_text"])
        new_text = str(payload["new_text"])
        final_text, state = render_ensure_replace_exact_once(target, content, old_text, new_text, operation.label)
        message = f"{target.name}: ensure replace exact once OK ({state})"
    elif op_type == "ReplaceExactMany":
        old_text = str(payload["old_text"])
        new_text = str(payload.get("new_text", ""))
        expected_count = payload.get("expected_count")
        final_text, actual_count = render_replace_exact_many(target, content, old_text, new_text, operation.label, expected_count)
        message = f"{target.name}: reemplazo exacto multiple aplicado ({actual_count} coincidencia(s))"
    elif op_type == "ReplaceNearestExact":
        old_text = str(payload["old_text"])
        new_text = str(payload.get("new_text", ""))
        near_anchor = str(payload["near_anchor"])
        final_text = render_replace_nearest_exact(target, content, old_text, new_text, near_anchor, operation.label)
        message = f"{target.name}: replace nearest exact OK"
    elif op_type == "DeleteExactOnce":
        old_text = str(payload["old_text"])
        final_text = render_delete_exact_once(target, content, old_text, operation.label)
        message = f"{target.name}: borrado exacto aplicado"
    elif op_type == "DeleteRegexOnce":
        pattern = str(payload["pattern"])
        flags = payload.get("flags")
        final_text = render_delete_regex_once(target, content, pattern, operation.label, flags)
        message = f"{target.name}: borrado regex exacto aplicado (1 coincidencia)"
    elif op_type == "DeleteRegexMany":
        pattern = str(payload["pattern"])
        flags = payload.get("flags")
        expected_count = payload.get("expected_count")
        final_text, actual_count = render_delete_regex_many(target, content, pattern, operation.label, flags, expected_count)
        message = f"{target.name}: borrado regex multiple aplicado ({actual_count} coincidencia(s))"
    elif op_type == "AssertContains":
        text = str(payload["text"])
        final_text = render_assert_contains(target, content, text, operation.label)
        message = f"{target.name}: assert contains OK"
    elif op_type == "AssertNotContains":
        text = str(payload["text"])
        final_text = render_assert_not_contains(target, content, text, operation.label)
        message = f"{target.name}: assert not contains OK"
    elif op_type == "AssertRegexCount":
        pattern = str(payload["pattern"])
        flags = payload.get("flags")
        expected_count = payload.get("expected_count")
        final_text, actual_count = render_assert_regex_count(target, content, pattern, operation.label, flags, expected_count)
        message = f"{target.name}: assert regex count OK ({actual_count} coincidencia(s))"
    elif op_type == "EnsureInsertAfterExact":
        anchor = str(payload["anchor"])
        insert_text = str(payload.get("insert_text", ""))
        final_text = render_ensure_insert_after_exact(target, content, anchor, insert_text, operation.label)
        message = f"{target.name}: ensure insert after exact OK"
    elif op_type == "EnsureInsertBeforeExact":
        anchor = str(payload["anchor"])
        insert_text = str(payload.get("insert_text", ""))
        final_text = render_ensure_insert_before_exact(target, content, anchor, insert_text, operation.label)
        message = f"{target.name}: ensure insert before exact OK"
    elif op_type == "MoveBlockExactOnce":
        old_text = str(payload["old_text"])
        anchor = str(payload["anchor"])
        insert_position = payload.get("insert_position")
        final_text = render_move_block_exact_once(target, content, old_text, anchor, insert_position, operation.label)
        message = f"{target.name}: move block exact once OK"
    elif op_type == "DeleteBetweenExactAnchors":
        start_anchor = str(payload["start_anchor"])
        end_anchor = str(payload["end_anchor"])
        final_text = render_delete_between_exact_anchors(target, content, start_anchor, end_anchor, operation.label)
        message = f"{target.name}: borrado entre anclas exactas aplicado"
    elif op_type == "ReplaceBetweenExactAnchors":
        start_anchor = str(payload["start_anchor"])
        end_anchor = str(payload["end_anchor"])
        new_text = str(payload.get("new_text", ""))
        final_text = render_replace_between_exact_anchors(target, content, start_anchor, end_anchor, new_text, operation.label)
        message = f"{target.name}: reemplazo entre anclas exactas aplicado"
    elif op_type == "NormalizeFile":
        line_ending = payload.get("line_ending")
        ensure_final_newline = payload.get("ensure_final_newline")
        strip_trailing_spaces = payload.get("strip_trailing_spaces")
        final_text = render_normalize_file(target, content, operation.label, line_ending, ensure_final_newline, strip_trailing_spaces)
        message = f"{target.name}: archivo normalizado"
    elif op_type == "InsertAfterExact":
        anchor = str(payload["anchor"])
        insert_text = str(payload.get("insert_text", ""))
        final_text = render_insert_after_exact(target, content, anchor, insert_text, operation.label)
        message = f"{target.name}: insercion aplicada despues del ancla"
    elif op_type == "InsertBeforeExact":
        anchor = str(payload["anchor"])
        insert_text = str(payload.get("insert_text", ""))
        final_text = render_insert_before_exact(target, content, anchor, insert_text, operation.label)
        message = f"{target.name}: insercion aplicada antes del ancla"
    elif op_type == "ReplaceRegexCount":
        pattern = str(payload["pattern"])
        new_text = str(payload.get("new_text", ""))
        flags = payload.get("flags")
        expected_count = payload.get("expected_count")
        final_text, actual_count = render_replace_regex_count(target, content, pattern, new_text, operation.label, flags, expected_count)
        message = f"{target.name}: reemplazo regex count aplicado ({actual_count} coincidencia(s))"
    elif op_type == "EnsureReplaceRegexOnce":
        pattern = str(payload["pattern"])
        new_text = str(payload["new_text"])
        flags = payload.get("flags")
        already_applied_text = payload.get("already_applied_text")
        already_applied_regex = payload.get("already_applied_regex")
        final_text, state = render_ensure_replace_regex_once(
            target,
            content,
            pattern,
            new_text,
            operation.label,
            flags,
            str(already_applied_text) if already_applied_text is not None else None,
            str(already_applied_regex) if already_applied_regex is not None else None,
        )
        message = f"{target.name}: ensure replace regex once OK ({state})"
    elif op_type == "ReplaceRegexOnce":
        pattern = str(payload["pattern"])
        new_text = str(payload.get("new_text", ""))
        flags = payload.get("flags")
        final_text = render_replace_regex_once(target, content, pattern, new_text, operation.label, flags)
        message = f"{target.name}: reemplazo regex aplicado"
    elif op_type == "ReplaceRegexMany":
        pattern = str(payload["pattern"])
        new_text = str(payload.get("new_text", ""))
        flags = payload.get("flags")
        expected_count = payload.get("expected_count")
        final_text, actual_count = render_replace_regex_many(target, content, pattern, new_text, operation.label, flags, expected_count)
        message = f"{target.name}: reemplazo regex multiple aplicado ({actual_count} coincidencia(s))"
    else:
        fail(f"No se puede ejecutar la operacion: {op_type}")

    if support_notes:
        message = f"{message} | auto-support: " + "; ".join(support_notes)

    return ExecutionResult(target, content, final_text, message, op_type in MUTATING_OPERATION_TYPES)


def execute_operation(ctx: PatchContext, operation: BaseOperation) -> ExecutionResult:
    if operation.spec.type in {"AssertFileExists", "AssertFileNotExists"}:
        target = operation.target_path(ctx)
        execution = execute_single_operation(ctx, target, None, operation)
        return execution

    target = operation.target_file(ctx)
    content = read_file_utf8(target) if operation.spec.type in CONTENT_OPERATION_TYPES else None
    execution = execute_single_operation(ctx, target, content, operation)

    if execution.mutates_file and not ctx.dry_run and execution.original_content is not None and execution.final_text is not None:
        write_file_if_changed(target, execution.original_content, execution.final_text)

    return execution


def simulate_operation(
    ctx: PatchContext,
    operation: Operation,
    content_by_target: dict[Path, str],
) -> str:
    if isinstance(operation, ApplySetOperation):
        for nested_operation in operation.operations:
            simulate_operation(ctx, nested_operation, content_by_target)
        return f"{operation.label}: ApplySet OK ({len(operation.operations)} operacion(es))"

    if not isinstance(operation, BaseOperation):
        fail("Operacion no soportada en simulate_operation")

    if operation.spec.type in {"AssertFileExists", "AssertFileNotExists"}:
        target = resolve_target_path(ctx.root_dir, operation.spec.file)
        execution = execute_single_operation(ctx, target, None, operation)
        return execution.message

    target = resolve_target_file(ctx.root_dir, operation.spec.file)
    if operation.spec.type in CONTENT_OPERATION_TYPES:
        content = content_by_target.get(target)
        if content is None:
            content = read_file_utf8(target)
        execution = execute_single_operation(ctx, target, content, operation)
        if execution.final_text is not None:
            content_by_target[target] = execution.final_text
        return execution.message

    execution = execute_single_operation(ctx, target, None, operation)
    return execution.message


def simulate_operations(ctx: PatchContext, operations: Iterable[Operation]) -> list[str]:
    results, _ = simulate_operations_with_state(ctx, operations)
    return results


def parse_operation(item: dict[str, Any]) -> Operation:
    op_type = str(item.get("type", "")).strip()
    label = str(item.get("label", op_type)).strip()
    file_value = str(item.get("file", "")).strip()

    if not op_type:
        fail("Una operacion no trae type.")

    payload = {k: v for k, v in item.items() if k not in {"type", "label", "file"}}
    validate_operation_payload(op_type, label, file_value, payload)

    if op_type == "ApplySet":
        raw_operations = payload.get("operations")
        assert isinstance(raw_operations, list)
        spec = OperationSpec(type=op_type, label=label, file=file_value, payload=payload)
        nested_operations = [parse_operation(child) for child in raw_operations]
        return ApplySetOperation(spec, nested_operations)

    spec = OperationSpec(type=op_type, label=label, file=file_value, payload=payload)
    return GenericOperation(spec)


def parse_operations(data: Any) -> list[Operation]:
    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        fail("El payload de operaciones debe ser una lista JSON o un objeto JSON.")
    if not data:
        fail("No mandaste operaciones.")
    if not all(isinstance(item, dict) for item in data):
        fail("Cada operacion debe ser un objeto JSON.")
    return [parse_operation(item) for item in data]


def load_operations_from_file(path_value: Path) -> list[Operation]:
    raw = path_value.read_text(encoding="utf-8")
    return parse_operations(json.loads(raw))


def load_operations_from_stdin() -> list[Operation]:
    raw = sys.stdin.read()
    if not raw.strip():
        fail("STDIN viene vacio. Pasa JSON por stdin o usa --ops-file.")
    return parse_operations(json.loads(raw))


def apply_operations(ctx: PatchContext, operations: Iterable[Operation]) -> list[str]:
    ensure_directory(ctx.root_dir)
    results: list[str] = []

    ops_list = list(operations)
    total = len(ops_list)
    if total == 0:
        fail("No hay operaciones para aplicar.")

    info(f"RootDir: {ctx.root_dir}")
    info(f"Backups: {ctx.backup_dir}")
    info(f"CheckpointDir: {ctx.checkpoint_dir}")

    preview_results, preview_content_by_target = simulate_operations_with_state(ctx, ops_list)
    info(f"Preflight OK: {len(preview_results)} operacion(es) validada(s)")
    for summary in build_preview_diff_summary(ctx, ops_list, preview_content_by_target):
        info(f"PreviewDiffSummary: {summary}")

    if ctx.dry_run:
        info("Modo dry-run activo: no se escribiran cambios ni se crearan checkpoints.")
        for result in preview_results:
            ok(f"[dry-run] {result}")
            results.append(result)
        return results

    checkpoints = build_session_checkpoints(ctx, ops_list)
    info(f"Checkpoint de sesion listo: {len(checkpoints)} archivo(s)")

    try:
        for index, operation in enumerate(ops_list, start=1):
            info(f"[{index}/{total}] {operation.spec.label} -> {operation.spec.file}")
            result = operation.apply(ctx)
            ok(result)
            results.append(result)
    except Exception as exc:
        restored = restore_session_checkpoints(checkpoints)
        info(f"Rollback de sesion aplicado sobre {len(restored)} archivo(s).")
        if isinstance(exc, CapatchError):
            raise CapatchError(f"{exc} | Rollback aplicado desde {ctx.checkpoint_dir}") from exc
        raise CapatchError(
            f"Error inesperado durante apply_operations: {exc} | "
            f"Rollback aplicado desde {ctx.checkpoint_dir}"
        ) from exc

    return results


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Motor de parches declarativos para Code Atlas y compas.",
    )
    parser.add_argument(
        "--root-dir",
        default=str(DEFAULT_ROOT_DIR),
        help="Carpeta raiz donde viven los archivos a tocar.",
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--ops-file",
        help="Ruta a archivo JSON con la lista de operaciones.",
    )
    group.add_argument(
        "--ops-stdin",
        action="store_true",
        help="Lee la lista de operaciones como JSON desde stdin.",
    )
    parser.add_argument(
        "--checkpoint-label",
        help="Nombre legible del checkpoint de sesion. Ej: pre-2.1",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ejecuta validaciones y preview, pero no escribe cambios ni crea checkpoints.",
    )
    parser.add_argument(
        "--no-auto-support",
        action="store_true",
        help="Desactiva la capa de auto-soporte para desajustes minimos recuperables.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Imprime un ejemplo minimo de operaciones y sale.",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Corre pruebas rapidas del motor y sale.",
    )
    return parser


def print_self_test() -> int:
    example = [
        {
            "type": "ReplaceLineRange",
            "label": "Ejemplo de reemplazo",
            "file": "code-atlas.py",
            "start_line": 1,
            "end_line": 1,
            "new_text": "# cambio ejemplo",
        }
    ]
    print(json.dumps(example, indent=2, ensure_ascii=False))
    return 0


def run_smoke_tests() -> int:
    with tempfile.TemporaryDirectory(prefix="capatch_smoke_") as tmp:
        root_dir = Path(tmp)
        target = root_dir / "demo.txt"
        target.write_text("uno\nANCHOR\ndos\n", encoding="utf-8", newline="")

        ctx = PatchContext(
            root_dir=root_dir,
            backup_dir=root_dir / BACKUP_DIR_NAME,
            checkpoint_dir=root_dir / BACKUP_DIR_NAME / "smoke",
            dry_run=False,
            auto_support=True,
        )

        ops = parse_operations(
            [
                {
                    "type": "EnsureInsertAfterExact",
                    "label": "insert local",
                    "file": "demo.txt",
                    "anchor": "ANCHOR",
                    "insert_text": "\nTRES",
                },
                {
                    "type": "EnsureReplaceExactOnce",
                    "label": "replace once",
                    "file": "demo.txt",
                    "old_text": "dos",
                    "new_text": "dos_mod",
                },
            ]
        )
        apply_operations(ctx, ops)
        final_text = target.read_text(encoding="utf-8")
        expected = "uno\nANCHOR\nTRES\ndos_mod\n"
        if final_text != expected:
            fail(f"Smoke test fallo. Esperado={expected!r} actual={final_text!r}")

        regex_target = root_dir / "regex_demo.txt"
        regex_target.write_text("valor=old\n", encoding="utf-8", newline="")
        regex_ops = parse_operations(
            [
                {
                    "type": "EnsureReplaceRegexOnce",
                    "label": "regex once",
                    "file": "regex_demo.txt",
                    "pattern": r"valor=old",
                    "new_text": "valor=new",
                    "already_applied_text": "valor=new",
                }
            ]
        )
        apply_operations(ctx, regex_ops)
        apply_operations(ctx, regex_ops)
        regex_final = regex_target.read_text(encoding="utf-8")
        if regex_final != "valor=new\n":
            fail(f"Smoke test regex fallo. Actual={regex_final!r}")

        support_target = root_dir / "support_demo.txt"
        support_target.write_text("header   \nbody\n", encoding="utf-8", newline="")
        support_ops = parse_operations(
            [
                {
                    "type": "InsertAfterExact",
                    "label": "support insert after",
                    "file": "support_demo.txt",
                    "anchor": "header",
                    "insert_text": "\nX",
                }
            ]
        )
        apply_operations(ctx, support_ops)
        support_final = support_target.read_text(encoding="utf-8")
        if support_final != "header   \nX\nbody\n":
            fail(f"Smoke test auto-support fallo. Actual={support_final!r}")

    ok("Smoke tests OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        return print_self_test()
    if args.smoke_test:
        return run_smoke_tests()

    if not args.ops_file and not args.ops_stdin:
        parser.error("Debes pasar --ops-file o --ops-stdin, o usar --self-test o --smoke-test.")

    root_dir = Path(args.root_dir).expanduser().resolve()
    backup_dir = root_dir / BACKUP_DIR_NAME
    checkpoint_label = sanitize_checkpoint_label(args.checkpoint_label)
    checkpoint_dir = backup_dir / checkpoint_label
    ctx = PatchContext(
        root_dir=root_dir,
        backup_dir=backup_dir,
        checkpoint_dir=checkpoint_dir,
        dry_run=bool(args.dry_run),
        auto_support=not bool(args.no_auto_support),
    )

    try:
        operations = (
            load_operations_from_file(Path(args.ops_file).expanduser().resolve())
            if args.ops_file
            else load_operations_from_stdin()
        )
        apply_operations(ctx, operations)
        ok("Cambios aplicados chido.")
        return 0
    except CapatchError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"[ERROR] JSON invalido: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"[ERROR] Error inesperado: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
