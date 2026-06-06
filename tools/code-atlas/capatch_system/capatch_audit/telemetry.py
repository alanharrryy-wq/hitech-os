from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

from capatch_contracts.constants import DEFAULT_ENCODING
from capatch_contracts.versions import CAPATCH_PLUGIN_RUNTIME_VERSION, CAPATCH_SYSTEM_TARGET_VERSION, TELEMETRY_ARTIFACT_SCHEMA_VERSION


DEFAULT_ENV_KEYS = (
    "CAPATCH_WINDOWS_SMOKE_REQUIRED_PLUGINS",
    "CAPATCH_ENVIRONMENT_PROFILE",
    "VIRTUAL_ENV",
    "PYTHONPATH",
    "CI",
)


def utc_now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _run_git(root_dir: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root_dir), *args],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except Exception:
        return None
    value = (completed.stdout or "").strip()
    return value or None


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    return value


def build_environment_fingerprint(root_dir: Path | None = None, *, extra_env_keys: Iterable[str] | None = None) -> dict[str, Any]:
    env_keys = list(DEFAULT_ENV_KEYS)
    for key in list(extra_env_keys or []):
        if key and key not in env_keys:
            env_keys.append(str(key))
    env_snapshot = {key: os.environ.get(key) for key in env_keys if os.environ.get(key) is not None}
    return {
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "system": platform.system(),
        "cwd": str(Path.cwd()),
        "root_dir": str(Path(root_dir).resolve()) if root_dir else None,
        "virtual_env": os.environ.get("VIRTUAL_ENV"),
        "sys_path_head": [str(item) for item in sys.path[:8]],
        "env": env_snapshot,
    }


def payload_digest(payload: Any) -> str:
    raw = json.dumps(_jsonable(payload), sort_keys=True, ensure_ascii=False).encode(DEFAULT_ENCODING)
    return hashlib.sha256(raw).hexdigest()


def enrich_payload(
    base_payload: dict[str, Any],
    *,
    root_dir: Path,
    artifact_kind: str,
    artifact_scope: str,
    source_command: str | None = None,
    tool_version: str = CAPATCH_SYSTEM_TARGET_VERSION,
    runtime_version: str = CAPATCH_PLUGIN_RUNTIME_VERSION,
    schema_version: str = TELEMETRY_ARTIFACT_SCHEMA_VERSION,
    is_historical: bool = False,
    historical_reason: str | None = None,
    superseded_by: str | None = None,
    freshness_window: str | None = None,
    run_id: str | None = None,
    checkpoint_id: str | None = None,
    baseline_id: str | None = None,
    trace_id: str | None = None,
    actor: str | None = None,
) -> dict[str, Any]:
    payload = dict(base_payload or {})
    root_dir = Path(root_dir).resolve()
    payload.setdefault("schema_version", schema_version)
    payload.setdefault("generated_at_utc", utc_now_iso())
    payload.setdefault("tool_version", tool_version)
    payload.setdefault("runtime_version", runtime_version)
    payload.setdefault("artifact_kind", artifact_kind)
    payload.setdefault("artifact_scope", artifact_scope)
    payload.setdefault("source_command", source_command or " ".join(sys.argv) or "python")
    payload.setdefault("root_dir", str(root_dir))
    payload.setdefault("git_branch", _run_git(root_dir, "rev-parse", "--abbrev-ref", "HEAD"))
    payload.setdefault("git_head", _run_git(root_dir, "rev-parse", "HEAD"))
    payload.setdefault("is_historical", bool(is_historical))
    payload.setdefault("historical_reason", historical_reason)
    payload.setdefault("superseded_by", superseded_by)
    payload.setdefault("freshness_window", freshness_window)
    payload.setdefault("run_id", run_id)
    payload.setdefault("checkpoint_id", checkpoint_id)
    payload.setdefault("baseline_id", baseline_id)
    payload.setdefault("trace_id", trace_id or run_id or str(payload.get("name") or "artifact"))
    payload.setdefault("actor", actor)
    payload.setdefault("environment_fingerprint", build_environment_fingerprint(root_dir))
    payload.setdefault("payload_digest", payload_digest(base_payload or {}))
    validate_telemetry_payload(payload)
    return _jsonable(payload)


_REQUIRED_TELEMETRY_KEYS = (
    "name",
    "status",
    "schema_version",
    "generated_at_utc",
    "tool_version",
    "runtime_version",
    "artifact_kind",
    "artifact_scope",
    "source_command",
    "root_dir",
    "is_historical",
    "environment_fingerprint",
    "payload_digest",
)


def validate_telemetry_payload(payload: dict[str, Any]) -> None:
    missing = [key for key in _REQUIRED_TELEMETRY_KEYS if key not in payload]
    if missing:
        raise ValueError(f"Telemetry payload missing required keys: {missing}")
    if not isinstance(payload.get("environment_fingerprint"), dict):
        raise ValueError("Telemetry payload requires environment_fingerprint dict")
    if not isinstance(payload.get("is_historical"), bool):
        raise ValueError("Telemetry payload is_historical must be bool")


_METADATA_RENDER_ORDER = (
    "name",
    "status",
    "generated_at_utc",
    "tool_version",
    "runtime_version",
    "artifact_kind",
    "artifact_scope",
    "source_command",
    "run_id",
    "checkpoint_id",
    "baseline_id",
    "trace_id",
    "is_historical",
    "historical_reason",
    "superseded_by",
    "freshness_window",
    "git_branch",
    "git_head",
)


def render_telemetry_markdown(payload: dict[str, Any], body_lines: list[str] | None = None) -> str:
    lines = [f"# {payload.get('name', 'telemetry_artifact')}", ""]
    for key in _METADATA_RENDER_ORDER:
        if key in payload:
            lines.append(f"- {key}: `{payload.get(key)}`")
    lines.extend(["", "## environment_fingerprint", ""])
    fingerprint = dict(payload.get("environment_fingerprint") or {})
    for key, value in sorted(fingerprint.items()):
        lines.append(f"- {key}: `{value}`")
    if body_lines:
        lines.extend(["", *body_lines])
    return "\n".join(lines).rstrip() + "\n"


def write_telemetry_report(output_dir: Path, stem: str, payload: dict[str, Any], body_lines: list[str] | None = None) -> dict[str, str]:
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding=DEFAULT_ENCODING, newline="")
    md_path.write_text(render_telemetry_markdown(payload, body_lines), encoding=DEFAULT_ENCODING, newline="")
    return {"json": str(json_path), "md": str(md_path)}


def load_telemetry_payload(path_value: Path) -> dict[str, Any] | None:
    path_value = Path(path_value)
    if not path_value.exists():
        return None
    try:
        payload = json.loads(path_value.read_text(encoding=DEFAULT_ENCODING, errors="replace"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def mark_payload_historical(payload: dict[str, Any], *, reason: str, superseded_by: str | None = None) -> dict[str, Any]:
    next_payload = dict(payload)
    next_payload["is_historical"] = True
    next_payload["historical_reason"] = reason
    if superseded_by:
        next_payload["superseded_by"] = superseded_by
    return next_payload


def detect_runtime_mismatch(payload: dict[str, Any], *, expected_runtime_version: str = CAPATCH_PLUGIN_RUNTIME_VERSION) -> bool:
    return str(payload.get("runtime_version") or "") not in {"", str(expected_runtime_version)}


def refresh_existing_telemetry(root_dir: Path) -> list[dict[str, Any]]:
    root_dir = Path(root_dir).resolve()
    output_dir = root_dir / "reports" / "telemetry"
    actions: list[dict[str, Any]] = []
    for json_path in sorted(output_dir.glob("*.json")):
        payload = load_telemetry_payload(json_path)
        if not payload:
            continue
        changed = False
        if "schema_version" not in payload:
            payload["schema_version"] = TELEMETRY_ARTIFACT_SCHEMA_VERSION
            changed = True
        if "generated_at_utc" not in payload:
            payload["generated_at_utc"] = utc_now_iso()
            changed = True
        if "tool_version" not in payload:
            payload["tool_version"] = CAPATCH_SYSTEM_TARGET_VERSION
            changed = True
        if "runtime_version" not in payload:
            payload["runtime_version"] = CAPATCH_PLUGIN_RUNTIME_VERSION
            changed = True
        if "artifact_kind" not in payload:
            payload["artifact_kind"] = "telemetry-report"
            changed = True
        if "artifact_scope" not in payload:
            payload["artifact_scope"] = f"reports/telemetry/{json_path.name}"
            changed = True
        if "source_command" not in payload:
            payload["source_command"] = "historical-refresh"
            changed = True
        if "root_dir" not in payload:
            payload["root_dir"] = str(root_dir)
            changed = True
        if "environment_fingerprint" not in payload:
            payload["environment_fingerprint"] = build_environment_fingerprint(root_dir)
            changed = True
        if "payload_digest" not in payload:
            body = {k: v for k, v in payload.items() if k not in {"payload_digest"}}
            payload["payload_digest"] = payload_digest(body)
            changed = True
        if "is_historical" not in payload:
            payload["is_historical"] = False
            changed = True
        if detect_runtime_mismatch(payload) and not payload.get("is_historical"):
            payload = mark_payload_historical(payload, reason="runtime-version-mismatch-detected-during-refresh")
            changed = True
        if changed:
            validate_telemetry_payload(payload)
            json_path.write_text(json.dumps(_jsonable(payload), indent=2, ensure_ascii=False) + "\n", encoding=DEFAULT_ENCODING, newline="")
            md_path = json_path.with_suffix(".md")
            md_path.write_text(render_telemetry_markdown(payload), encoding=DEFAULT_ENCODING, newline="")
            actions.append({"path": str(json_path), "status": "updated", "is_historical": bool(payload.get("is_historical"))})
        else:
            actions.append({"path": str(json_path), "status": "unchanged", "is_historical": bool(payload.get("is_historical"))})
    return actions
