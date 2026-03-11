#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.stable_json import load_json


def _load_profile_overrides(profile_name: str) -> dict[str, Any]:
    profile = (profile_name or "safe").strip().lower()
    profile_path = (Path(__file__).resolve().parent / "profiles" / f"{profile}.json").resolve()
    if not profile_path.exists():
        raise FileNotFoundError(f"profile not found: {profile_path}")
    payload = load_json(profile_path)
    if not isinstance(payload, dict):
        raise ValueError(f"profile file must be an object: {profile_path}")
    return payload


def _normalize_profile_name(profile_name: str | None) -> str:
    raw = (profile_name or "").strip().lower()
    return raw or "safe"


@dataclass(frozen=True)
class SentinelConfig:
    repo_root: Path
    output_root: Path
    db_path: Path
    state_path: Path
    report_dir: Path
    telemetry_dir: Path
    dashboard_dir: Path
    visualization_dir: Path
    log_dir: Path
    quarantine_dir: Path
    profile_name: str = "safe"
    runtime_artifact_dirs: tuple[str, ...] = (
        "tools/codex/worktrees",
        "tools/codex/runs",
        "tools/_local",
        "artifacts",
        "logs",
    )
    exclude_dir_globs: tuple[str, ...] = (
        ".git",
        "node_modules",
        ".next",
        ".turbo",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        "coverage",
    )
    large_file_threshold_bytes: int = 10 * 1024 * 1024
    duplicate_hash_max_bytes: int = 64 * 1024 * 1024
    max_text_scan_bytes: int = 2 * 1024 * 1024
    max_security_scan_files: int = 15000
    binary_extensions: tuple[str, ...] = (
        ".zip",
        ".7z",
        ".rar",
        ".tar",
        ".gz",
        ".xz",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".bin",
        ".iso",
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".gif",
        ".webp",
        ".pdf",
    )
    expected_text_extensions: tuple[str, ...] = (
        ".py",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".mjs",
        ".cjs",
        ".json",
        ".yml",
        ".yaml",
        ".md",
        ".txt",
        ".toml",
        ".ini",
        ".conf",
        ".env",
        ".ps1",
        ".bat",
        ".cmd",
        ".sh",
        ".sql",
        ".csv",
        ".tsv",
        ".html",
        ".css",
        ".scss",
        ".svg",
        ".xml",
        ".lock",
    )
    allowed_binary_prefixes: tuple[str, ...] = (
        "assets/",
        "docs/",
        "artifacts/",
        "apps/keystone/public/",
    )
    temporary_extensions: tuple[str, ...] = (
        ".tmp",
        ".temp",
        ".bak",
        ".orig",
        ".old",
        ".rej",
        ".swp",
        ".swo",
    )
    cache_markers: tuple[str, ...] = (
        ".cache",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    )
    build_markers: tuple[str, ...] = (
        "/dist/",
        "/build/",
        "/out/",
        "/coverage/",
        "/.next/",
        "/.turbo/",
    )
    managed_ignore_start: str = "# >>> git-sentinel managed (auto-generated)"
    managed_ignore_end: str = "# <<< git-sentinel managed"
    ignore_history_path: str = "tools/_local/git_sentinel/state/ignore_rules_history.json"
    safe_cleanup_prefixes: tuple[str, ...] = (
        "tools/codex/worktrees/",
        "tools/codex/runs/",
        "tools/_local/",
        "artifacts/",
        "logs/",
        "_reports/",
        ".agents/_merge_",
    )
    safe_ignore_prefixes: tuple[str, ...] = (
        "tools/codex/worktrees/",
        "tools/codex/runs/",
        "tools/_local/",
        "artifacts/",
        "logs/",
        "_reports/",
        ".agents/",
    )
    ignore_whitelist_globs: tuple[str, ...] = (
        "apps/**",
        "packages/**",
        "services/**",
        "tools/hos/**",
        "tools/hydration_sentinel/**",
        "docs/**",
    )
    secret_scan_extensions: tuple[str, ...] = (
        ".py",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".mjs",
        ".cjs",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".conf",
        ".env",
        ".md",
        ".txt",
        ".ps1",
        ".bat",
        ".cmd",
        ".sh",
    )
    dangerous_script_tokens: tuple[str, ...] = (
        "rm -rf",
        "del /s /q",
        "git clean -fdx",
        "git reset --hard",
    )
    max_files_for_dependency_graph: int = 5000
    max_commits_for_history: int = 2500
    prediction_window: int = 20
    lock_path: str = "tools/_local/git_sentinel/state/guardian.lock.json"
    lock_stale_seconds: int = 7200
    retention_enabled: bool = True
    retention_max_age_days: int = 30
    retention_max_files_per_dir: int = 500
    alert_health_threshold: int = 65
    alert_webhook_env_var: str = "GIT_SENTINEL_ALERT_WEBHOOK"
    false_positive_feedback_path: str = "tools/_local/git_sentinel/state/false_positive_feedback.json"
    default_guardian_interval_seconds: int = 600
    autotune_enabled: bool = False
    autotune_min_interval_seconds: int = 300
    autotune_max_interval_seconds: int = 1800
    autotune_high_activity_threshold: int = 220
    autotune_low_activity_threshold: int = 80
    additional: dict[str, Any] = field(default_factory=dict)

    def rel(self, path: Path) -> str:
        return path.resolve().relative_to(self.repo_root.resolve()).as_posix()

    def ensure_layout(self) -> None:
        for directory in (
            self.output_root,
            self.report_dir,
            self.telemetry_dir,
            self.dashboard_dir,
            self.visualization_dir,
            self.log_dir,
            self.quarantine_dir,
            self.db_path.parent,
            self.state_path.parent,
        ):
            directory.mkdir(parents=True, exist_ok=True)


def _repo_root_from_arg(repo_root: str | None) -> Path:
    if repo_root:
        return Path(repo_root).resolve()
    return find_repo_root()


def _default_paths(repo_root: Path) -> dict[str, Path]:
    output_root = (repo_root / "tools/_local/git_sentinel").resolve()
    return {
        "output_root": output_root,
        "db_path": output_root / "state/sentinel.db",
        "state_path": output_root / "state/sentinel_state.json",
        "report_dir": output_root / "reports",
        "telemetry_dir": output_root / "telemetry",
        "dashboard_dir": output_root / "dashboard",
        "visualization_dir": output_root / "visualization",
        "log_dir": output_root / "logs",
        "quarantine_dir": output_root / "quarantine",
    }


def _merge_override(base: SentinelConfig, payload: dict[str, Any]) -> SentinelConfig:
    mutable = dict(base.__dict__)
    for key, value in payload.items():
        if key in mutable and key not in {"repo_root"}:
            mutable[key] = value
        else:
            mutable.setdefault("additional", {})
            mutable["additional"][key] = value

    path_keys = {
        "output_root",
        "db_path",
        "state_path",
        "report_dir",
        "telemetry_dir",
        "dashboard_dir",
        "visualization_dir",
        "log_dir",
        "quarantine_dir",
    }
    for key in path_keys:
        raw = mutable.get(key)
        if raw is None:
            continue
        mutable[key] = Path(raw).resolve() if Path(str(raw)).is_absolute() else (base.repo_root / str(raw)).resolve()

    tuple_keys = [
        "runtime_artifact_dirs",
        "exclude_dir_globs",
        "binary_extensions",
        "allowed_binary_prefixes",
        "temporary_extensions",
        "cache_markers",
        "build_markers",
        "safe_cleanup_prefixes",
        "safe_ignore_prefixes",
        "ignore_whitelist_globs",
        "secret_scan_extensions",
        "dangerous_script_tokens",
        "expected_text_extensions",
    ]
    for key in tuple_keys:
        raw = mutable.get(key)
        if isinstance(raw, list):
            mutable[key] = tuple(str(item) for item in raw)

    return SentinelConfig(**mutable)


def build_config(
    repo_root: str | None = None,
    config_path: str | None = None,
    profile: str | None = None,
) -> SentinelConfig:
    resolved_root = _repo_root_from_arg(repo_root=repo_root)
    defaults = _default_paths(resolved_root)
    config = SentinelConfig(repo_root=resolved_root, **defaults)
    override_payload: dict[str, Any] = {}
    if config_path:
        raw_payload = load_json(Path(config_path))
        if not isinstance(raw_payload, dict):
            raise ValueError(f"config file must be an object: {config_path}")
        override_payload = raw_payload

    selected_profile = _normalize_profile_name(
        profile
        if profile is not None
        else str(override_payload.get("profile_name", config.profile_name)),
    )
    config = _merge_override(config, _load_profile_overrides(selected_profile))
    config = _merge_override(config, {"profile_name": selected_profile})

    if override_payload:
        config = _merge_override(config, override_payload)
    return config
