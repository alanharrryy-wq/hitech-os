from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from capatch_contracts.operations import MUTATING_OPERATION_TYPES, READ_ONLY_OPERATION_TYPES, OperationSpec, SEMANTIC_OPERATION_TYPES
from capatch_fs.guards import ensure_directory
from capatch_fs.paths import resolve_target_path
from capatch_ops.composite_ops import flatten_operation_specs

from .result_models import PreflightReport
from .syntax_validation import build_syntax_validation_plan


_LINE_RANGE_OPS = {"ReplaceLineRange", "DeleteLineRange"}
_EXACT_TEXT_OPS = {"ReplaceExactOnce", "EnsureReplaceExactOnce"}
_ANCHOR_OPS = {
    "ReplaceExactOnce",
    "ReplaceExactMany",
    "EnsureReplaceExactOnce",
    "ReplaceNearestExact",
    "MoveBlockExactOnce",
    "ReplaceBetweenExactAnchors",
    "DeleteBetweenExactAnchors",
    "DeleteExactOnce",
    "EnsureInsertAfterExact",
    "EnsureInsertBeforeExact",
    "InsertAfterExact",
    "InsertBeforeExact",
}
_REGEX_OPS = {"DeleteRegexMany", "DeleteRegexOnce", "ReplaceRegexOnce", "ReplaceRegexMany", "ReplaceRegexCount", "EnsureReplaceRegexOnce", "AssertRegexCount"}
_STRUCTURAL_SUFFIXES = {".ts", ".tsx", ".js", ".jsx"}
_LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".md": "markdown",
}


def _risk_summary(operations: list[OperationSpec], target_files: list[str]) -> dict[str, object]:
    file_count = len(set(target_files))
    mutating_count = sum(1 for op in operations if op.type in MUTATING_OPERATION_TYPES)
    reversible = all(op.reversibility in {"full", "partial"} for op in operations)
    if file_count <= 1 and mutating_count <= 3 and reversible:
        tier = "safe"
        level = "low"
    elif file_count <= 4 and mutating_count <= 12 and reversible:
        tier = "guarded"
        level = "medium"
    else:
        tier = "high-risk"
        level = "high"
    return {"risk_tier": tier, "risk_level": level, "file_count": file_count, "mutating_operation_count": mutating_count}


def _range_tuple(operation: OperationSpec) -> tuple[int, int] | None:
    if operation.type not in _LINE_RANGE_OPS:
        return None
    try:
        return int(operation.payload["start_line"]), int(operation.payload["end_line"])
    except Exception:
        return None


def _exact_text_signature(operation: OperationSpec) -> tuple[str, str] | None:
    if operation.type not in _EXACT_TEXT_OPS:
        return None
    old_text = operation.payload.get("old_text")
    if not isinstance(old_text, str) or not old_text:
        return None
    return operation.type, old_text


def _append_conflict(conflicts: list[dict[str, Any]], payload: dict[str, Any]) -> None:
    token = tuple(sorted((key, repr(value)) for key, value in payload.items()))
    if any(tuple(sorted((k, repr(v)) for k, v in item.items())) == token for item in conflicts):
        return
    conflicts.append(payload)


def _classify_language(path_value: str) -> str:
    suffix = Path(str(path_value or "")).suffix.lower()
    return _LANGUAGE_BY_SUFFIX.get(suffix, "text")


def _anchor_fragility_notes(text: str | None, *, field_name: str) -> list[str]:
    candidate = str(text or "")
    normalized = candidate.strip()
    notes: list[str] = []
    if not normalized:
        return [f"{field_name}:empty"]
    if len(normalized) < 12:
        notes.append(f"{field_name}:very_short")
    elif len(normalized) < 24:
        notes.append(f"{field_name}:short")
    if normalized.count("\n") == 0:
        notes.append(f"{field_name}:single_line")
    if normalized.startswith(('{', '[', '(', ',', ':')) or normalized.endswith(('{', '[', '(', ',', ':')):
        notes.append(f"{field_name}:boundary_like")
    return notes


def _collect_conflicts(flattened: list[OperationSpec]) -> list[dict[str, object]]:
    conflicts: list[dict[str, Any]] = []
    seen_targets: dict[str, list[OperationSpec]] = defaultdict(list)
    for operation in flattened:
        if operation.type in MUTATING_OPERATION_TYPES:
            seen_targets[operation.file].append(operation)

    for file_name, items in sorted(seen_targets.items()):
        if len(items) > 8:
            _append_conflict(
                conflicts,
                {"file": file_name, "reason": "high_operation_density", "operation_labels": [item.label for item in items]},
            )

        line_ranges = []
        for item in items:
            bounds = _range_tuple(item)
            if bounds is not None:
                line_ranges.append((bounds[0], bounds[1], item))
        line_ranges.sort(key=lambda row: (row[0], row[1], row[2].label))
        for index in range(1, len(line_ranges)):
            prev_start, prev_end, prev_item = line_ranges[index - 1]
            start, end, item = line_ranges[index]
            if start <= prev_end:
                _append_conflict(
                    conflicts,
                    {
                        "file": file_name,
                        "reason": "overlapping_line_ranges",
                        "first_operation": prev_item.label,
                        "second_operation": item.label,
                        "first_range": [prev_start, prev_end],
                        "second_range": [start, end],
                    },
                )

        normalize_ops = [item.label for item in items if item.type == "NormalizeFile"]
        if normalize_ops and len(items) > 1:
            _append_conflict(
                conflicts,
                {
                    "file": file_name,
                    "reason": "normalize_with_additional_mutations",
                    "operation_labels": [item.label for item in items],
                },
            )

        seen_exact: dict[tuple[str, str], OperationSpec] = {}
        for item in items:
            signature = _exact_text_signature(item)
            if signature is None:
                continue
            previous = seen_exact.get(signature)
            if previous is None:
                seen_exact[signature] = item
                continue
            _append_conflict(
                conflicts,
                {
                    "file": file_name,
                    "reason": "duplicate_exact_text_match",
                    "first_operation": previous.label,
                    "second_operation": item.label,
                    "match_type": signature[0],
                    "old_text_excerpt": signature[1][:120],
                },
            )
    return conflicts


def _build_surface_summary(flattened: list[OperationSpec], target_files: list[str]) -> dict[str, Any]:
    language_counts: dict[str, int] = defaultdict(int)
    structural_candidate_files: list[str] = []
    semantic_operation_count = 0
    regex_operation_count = 0
    anchor_operation_count = 0
    exact_operation_count = 0
    line_operation_count = 0

    for file_name in sorted(set(target_files)):
        language = _classify_language(file_name)
        language_counts[language] += 1
        if Path(file_name).suffix.lower() in _STRUCTURAL_SUFFIXES:
            structural_candidate_files.append(file_name)

    for operation in flattened:
        if operation.type in SEMANTIC_OPERATION_TYPES:
            semantic_operation_count += 1
        if operation.type in _REGEX_OPS:
            regex_operation_count += 1
        if operation.type in _ANCHOR_OPS:
            anchor_operation_count += 1
        if operation.type in _EXACT_TEXT_OPS:
            exact_operation_count += 1
        if operation.type in _LINE_RANGE_OPS:
            line_operation_count += 1

    dominant_language = max(language_counts.items(), key=lambda item: item[1])[0] if language_counts else "text"
    return {
        "language_counts": dict(sorted(language_counts.items())),
        "dominant_language": dominant_language,
        "structural_candidate_files": structural_candidate_files,
        "structural_candidate_count": len(structural_candidate_files),
        "semantic_operation_count": semantic_operation_count,
        "regex_operation_count": regex_operation_count,
        "anchor_operation_count": anchor_operation_count,
        "exact_operation_count": exact_operation_count,
        "line_operation_count": line_operation_count,
        "multi_file": len(set(target_files)) > 1,
    }


def _build_anchor_diagnostics(flattened: list[OperationSpec], conflicts: list[dict[str, Any]], target_files: list[str]) -> dict[str, Any]:
    fragile_notes: list[str] = []
    fragile_by_file: dict[str, list[str]] = defaultdict(list)
    high_density_files = sorted({str(item.get("file") or "") for item in conflicts if str(item.get("reason") or "") == "high_operation_density" and str(item.get("file") or "")})
    exact_anchor_operation_count = 0
    fragile_anchor_operation_count = 0

    for operation in flattened:
        if operation.type not in _ANCHOR_OPS:
            continue
        exact_anchor_operation_count += 1
        candidate_notes: list[str] = []
        payload = dict(operation.payload or {})
        for field_name in ("old_text", "anchor", "near_anchor", "start_anchor", "end_anchor"):
            if field_name in payload:
                candidate_notes.extend(_anchor_fragility_notes(payload.get(field_name), field_name=field_name))
        if candidate_notes:
            fragile_anchor_operation_count += 1
            preview = ",".join(candidate_notes[:4])
            fragile_notes.append(f"{operation.label}:{preview}")
            fragile_by_file[operation.file].append(operation.label)

    return {
        "exact_anchor_operation_count": exact_anchor_operation_count,
        "fragile_anchor_operation_count": fragile_anchor_operation_count,
        "fragile_anchor_notes": fragile_notes[:20],
        "fragile_anchor_files": {key: value[:8] for key, value in sorted(fragile_by_file.items())},
        "high_density_files": high_density_files,
        "target_file_count": len(set(target_files)),
    }


def _build_strategy_hints(
    flattened: list[OperationSpec],
    target_files: list[str],
    *,
    path_violations: list[dict[str, Any]],
    conflicts: list[dict[str, Any]],
    surface_summary: dict[str, Any],
    anchor_diagnostics: dict[str, Any],
) -> dict[str, Any]:
    file_count = len(set(target_files))
    mutating_count = sum(1 for item in flattened if item.type in MUTATING_OPERATION_TYPES)
    structural_candidate_files = list(surface_summary.get("structural_candidate_files") or [])
    fragile_anchor_count = int(anchor_diagnostics.get("fragile_anchor_operation_count", 0) or 0)
    high_density_files = list(anchor_diagnostics.get("high_density_files") or [])
    hints = {
        "prefer_exact": file_count == 1 and fragile_anchor_count == 0 and not structural_candidate_files and int(surface_summary.get("anchor_operation_count", 0) or 0) > 0,
        "prefer_structural": bool(structural_candidate_files) and (fragile_anchor_count > 0 or int(surface_summary.get("regex_operation_count", 0) or 0) > 0),
        "prefer_guarded": bool(high_density_files) or fragile_anchor_count > 1,
        "prefer_transactional": file_count > 1 and mutating_count > 0,
        "force_probe_only": bool(path_violations),
        "structural_candidate_files": structural_candidate_files,
        "high_density_files": high_density_files,
        "planner_stub": {"enabled": False, "hint": None, "source": None},
    }
    if conflicts and not hints["prefer_guarded"]:
        hints["prefer_guarded"] = True
    return hints


def preflight(ctx, operations):
    ensure_directory(Path(ctx.root_dir))
    run_id = datetime.now().strftime("preflight_%Y%m%d_%H%M%S")
    path_violations = []
    target_files: list[str] = []
    flattened = flatten_operation_specs(operations)
    for operation in flattened:
        try:
            if operation.type != "ApplySet":
                target = resolve_target_path(Path(ctx.root_dir), operation.file)
                target_files.append(target.relative_to(Path(ctx.root_dir)).as_posix())
        except Exception as exc:
            path_violations.append({"operation_label": operation.label, "file": operation.file, "error": str(exc)})
    conflicts = _collect_conflicts(flattened)
    syntax_validation_plan = build_syntax_validation_plan(sorted(set(target_files)))
    risk_summary = _risk_summary(flattened, target_files)
    surface_summary = _build_surface_summary(flattened, target_files)
    anchor_diagnostics = _build_anchor_diagnostics(flattened, conflicts, target_files)
    strategy_hints = _build_strategy_hints(
        flattened,
        target_files,
        path_violations=path_violations,
        conflicts=conflicts,
        surface_summary=surface_summary,
        anchor_diagnostics=anchor_diagnostics,
    )
    return PreflightReport(
        ok=not path_violations and not conflicts,
        run_id=run_id,
        target_files=sorted(set(target_files)),
        operation_count=len(flattened),
        mutating_operation_count=sum(1 for op in flattened if op.type in MUTATING_OPERATION_TYPES),
        read_only_operation_count=sum(1 for op in flattened if op.type in READ_ONLY_OPERATION_TYPES),
        conflicts=conflicts,
        path_violations=path_violations,
        schema_violations=[],
        syntax_validation_plan=syntax_validation_plan,
        risk_summary=risk_summary,
        surface_summary=surface_summary,
        anchor_diagnostics=anchor_diagnostics,
        strategy_hints=strategy_hints,
    )
