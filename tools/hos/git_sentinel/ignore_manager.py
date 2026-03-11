#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.hos._core.stable_json import load_json, write_json

from .config import SentinelConfig
from .utils import now_utc_iso, path_matches_any


def _safe_pattern_from_file(rel_path: str) -> str:
    normalized = rel_path.replace("\\", "/").strip("/")
    parent = normalized.rsplit("/", 1)[0] if "/" in normalized else ""
    extension = Path(normalized).suffix
    if parent and extension:
        return f"{parent}/**/*{extension}"
    if parent:
        return f"{parent}/**/*"
    if extension:
        return f"*{extension}"
    return normalized


def _is_safe_for_ignore_generation(pattern: str, config: SentinelConfig) -> bool:
    normalized = pattern.replace("\\", "/").strip("/")
    if path_matches_any(normalized, list(config.ignore_whitelist_globs)):
        return False
    for prefix in config.safe_ignore_prefixes:
        prefix_norm = prefix.replace("\\", "/").strip("/")
        if normalized == prefix_norm or normalized.startswith(prefix_norm + "/"):
            return True
    if normalized.startswith("*.") and any(
        ext in normalized for ext in (".tmp", ".temp", ".bak", ".log", ".cache")
    ):
        return True
    return False


def generate_ignore_rules(
    config: SentinelConfig,
    artifact_result: dict[str, Any],
    learned_patterns: list[dict[str, Any]],
) -> dict[str, Any]:
    rules: set[str] = set()
    rejected: list[dict[str, str]] = []

    rules.add("tools/_local/git_sentinel/")
    for runtime_dir in config.runtime_artifact_dirs:
        runtime_norm = runtime_dir.replace("\\", "/").strip("/")
        if runtime_norm:
            rules.add(f"{runtime_norm}/**")

    for row in artifact_result.get("cleanupCandidates", []):
        rel_path = str(row.get("path", ""))
        pattern = _safe_pattern_from_file(rel_path)
        if _is_safe_for_ignore_generation(pattern, config):
            rules.add(pattern)
        else:
            rejected.append({"pattern": pattern, "reason": "not in safe prefix/whitelist blocked"})

    for row in learned_patterns:
        pattern = str(row.get("pattern", "")).replace("\\", "/").strip("/")
        if not pattern:
            continue
        if int(row.get("count", 0)) < 2:
            continue
        if _is_safe_for_ignore_generation(pattern, config):
            rules.add(pattern)
        else:
            rejected.append({"pattern": pattern, "reason": "learned pattern blocked by safety policy"})

    sorted_rules = sorted({rule for rule in rules if rule.strip()})
    return {
        "rules": sorted_rules,
        "rejected": rejected,
        "count": len(sorted_rules),
    }


def _update_managed_block(
    original_text: str,
    rules: list[str],
    start_marker: str,
    end_marker: str,
) -> tuple[str, bool]:
    managed_block_lines = [start_marker, *rules, end_marker]
    managed_block = "\n".join(managed_block_lines) + "\n"

    if start_marker in original_text and end_marker in original_text:
        start_idx = original_text.index(start_marker)
        end_idx = original_text.index(end_marker, start_idx) + len(end_marker)
        if end_idx < len(original_text) and original_text[end_idx] == "\n":
            end_idx += 1
        updated = original_text[:start_idx] + managed_block + original_text[end_idx:]
    else:
        separator = "" if original_text.endswith("\n") else "\n"
        updated = original_text + separator + "\n" + managed_block
    return updated, updated != original_text


def apply_ignore_rules(
    config: SentinelConfig,
    rules: list[str],
    apply_changes: bool,
) -> dict[str, Any]:
    gitignore_path = (config.repo_root / ".gitignore").resolve()
    if not gitignore_path.exists():
        original = ""
    else:
        original = gitignore_path.read_text(encoding="utf-8")

    updated_text, changed = _update_managed_block(
        original_text=original,
        rules=rules,
        start_marker=config.managed_ignore_start,
        end_marker=config.managed_ignore_end,
    )

    history_path_raw = config.ignore_history_path
    history_path = (
        Path(history_path_raw).resolve()
        if Path(str(history_path_raw)).is_absolute()
        else (config.repo_root / str(history_path_raw)).resolve()
    )
    previous_history: list[dict[str, Any]] = []
    if history_path.exists():
        loaded = load_json(history_path, allow_relaxed=True)
        if isinstance(loaded, list):
            previous_history = loaded

    if changed and apply_changes:
        gitignore_path.write_text(updated_text, encoding="utf-8", newline="\n")

    # Versioned ignore rules history (deterministic JSON list).
    history_entry = {
        "timestamp": now_utc_iso(),
        "path": gitignore_path.as_posix(),
        "ruleCount": len(rules),
        "rules": list(rules),
        "changed": changed,
        "applied": bool(changed and apply_changes),
    }
    trimmed_history = [*previous_history[-49:], history_entry]
    write_json(history_path, trimmed_history, indent=2, sort_keys=True)

    return {
        "path": gitignore_path.as_posix(),
        "changed": changed,
        "applied": bool(changed and apply_changes),
        "ruleCount": len(rules),
        "historyPath": history_path.as_posix(),
        "historyLength": len(trimmed_history),
    }
