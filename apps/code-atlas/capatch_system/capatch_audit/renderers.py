from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from capatch_contracts.constants import DEFAULT_ENCODING
from capatch_contracts.directories import REPORT_DIRS
from capatch_contracts.report_catalog import REPORT_FILE_OWNERS

from .manifest import PatchRunRecord, patch_run_record_to_dict


def ensure_report_tree(root_dir: Path) -> dict[str, Path]:
    root_dir = Path(root_dir).resolve()
    paths: dict[str, Path] = {}
    for relative in REPORT_DIRS:
        path_value = root_dir / relative
        path_value.mkdir(parents=True, exist_ok=True)
        paths[relative] = path_value
    return paths


def write_text(path_value: Path, text: str) -> Path:
    path_value.parent.mkdir(parents=True, exist_ok=True)
    path_value.write_text(text, encoding=DEFAULT_ENCODING, newline="")
    return path_value


def write_json(path_value: Path, payload: Any) -> Path:
    return write_text(path_value, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def read_json(path_value: Path, default: Any) -> Any:
    if not path_value.exists():
        return default
    try:
        return json.loads(path_value.read_text(encoding=DEFAULT_ENCODING, errors="replace"))
    except Exception:
        return default


def sha256_file(path_value: Path) -> str | None:
    try:
        return sha256(path_value.read_bytes()).hexdigest()
    except Exception:
        return None


def _to_dict(value: Any) -> dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Unsupported render payload: {type(value)!r}")


def render_patch_run_md(record: PatchRunRecord) -> str:
    payload = patch_run_record_to_dict(record)
    lines = [f"# Patch run {payload['run_id']}", ""]
    summary_keys = [
        "patch_status",
        "system_status",
        "started_at",
        "finished_at",
        "execution_mode",
        "invocation_mode",
        "rollback_target",
        "baseline_ref",
    ]
    for key in summary_keys:
        lines.append(f"- {key}: `{payload.get(key)}`")
    lines.append("")
    lines.append("## Target files")
    lines.append("")
    if payload.get("target_files"):
        for target_file in payload["target_files"]:
            lines.append(f"- `{target_file}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Operation results")
    lines.append("")
    if payload.get("operation_results"):
        for item in payload["operation_results"]:
            lines.append(f"- `{item.get('operation_type')}` :: `{item.get('operation_label')}` :: `{item.get('patch_status')}`")
            lines.append(f"  - target_path: `{item.get('target_path')}`")
            lines.append(f"  - message: {item.get('message')}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Verifier results")
    lines.append("")
    if payload.get("verifier_results"):
        for item in payload["verifier_results"]:
            lines.append(f"- `{item.get('verifier_id')}` :: ok=`{item.get('ok')}` :: {item.get('title')}")
    else:
        lines.append("- none")
    lines.append("")
    if payload.get("error"):
        lines.append("## Error")
        lines.append("")
        lines.append(f"- {payload['error']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_rollback_preview_md(preview: Any) -> str:
    payload = _to_dict(preview)
    lines = [f"# Rollback preview {payload['rollback_id']}", ""]
    for key in ["source_run_id", "checkpoint_path", "restore_ok"]:
        lines.append(f"- {key}: `{payload.get(key)}`")
    lines.append("")
    lines.append("## Files to restore")
    lines.append("")
    for item in payload.get("files_to_restore") or ["none"]:
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## Conflicts")
    lines.append("")
    for item in payload.get("conflicts_with_current_tree") or []:
        lines.append(f"- `{item.get('relative_path')}` current=`{item.get('current_hash')}` expected=`{item.get('expected_hash')}`")
    if not payload.get("conflicts_with_current_tree"):
        lines.append("- none")
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    for item in payload.get("warnings") or ["none"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_baseline_md(record: Any) -> str:
    payload = _to_dict(record)
    lines = [f"# Baseline {payload['baseline_id']}", ""]
    for key in ["label", "created_at", "root_dir", "git_branch", "git_head"]:
        lines.append(f"- {key}: `{payload.get(key)}`")
    lines.append("")
    lines.append("## Target files")
    lines.append("")
    for item in payload.get("target_files") or ["none"]:
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## Hashes")
    lines.append("")
    for key, value in sorted((payload.get("hashes") or {}).items()):
        lines.append(f"- `{key}` -> `{value}`")
    lines.append("")
    if payload.get("notes"):
        lines.append("## Notes")
        lines.append("")
        lines.append(payload["notes"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_owner_manifest() -> dict[str, str]:
    return dict(REPORT_FILE_OWNERS)
