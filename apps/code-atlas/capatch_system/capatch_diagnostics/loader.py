from __future__ import annotations

"""Loader de plugins para el runtime diagnóstico.

Mantiene el layout plano `capatch_plugins/active/*` y registra callbacks por fase.
No depende del interior de otros dominios.
"""

import hashlib
import importlib.util
import json
import re
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

PLUGIN_DIR_NAME = "capatch_plugins"
PLUGIN_ACTIVE_DIR_NAME = "active"
PLUGIN_TEMPLATES_DIR_NAME = "templates"
PLUGIN_DISABLED_DIR_NAME = "disabled"
PLUGIN_QUARANTINE_DIR_NAME = "quarantine"
PLUGIN_ARCHIVE_DIR_NAME = "archive"
PLUGIN_REGISTRY_NAME = "_plugin_registry.json"
PLUGIN_DISABLED_NAME = "_plugin_disabled.json"
PLUGIN_LOGS_DIR_NAME = "_logs"
PLUGIN_RUNTIME_VERSION = "6.0.0"
PLUGIN_DEFAULT_TAIL_LINES = 80


PHASE_BUCKETS = {
    "guards": "guard",
    "before_apply": "guard",
    "after_apply": "guard",
    "support_resolvers": "guard",
    "target_detectors": "target-detector",
    "collectors": "collector",
    "context_enrichers": "context-enricher",
    "analyzers": "analyzer",
    "recommenders": "recommender",
    "fixers": "fixer",
    "verifiers": "verifier",
    "exporters": "exporter",
}


@dataclass(slots=True)
class PluginManifest:
    plugin_id: str
    version: str
    description: str
    min_runtime: str
    file_name: str
    path: str
    hash: str


class PluginAPI:
    def __init__(self, plugin_id: str, plugin_path: Path) -> None:
        self.plugin_id = plugin_id
        self.plugin_path = plugin_path
        self.guards: list[Callable[..., Any]] = []
        self.before_apply: list[Callable[..., Any]] = []
        self.after_apply: list[Callable[..., Any]] = []
        self.support_resolvers: list[Callable[..., Any]] = []
        self.target_detectors: list[Callable[..., Any]] = []
        self.collectors: list[Callable[..., Any]] = []
        self.context_enrichers: list[Callable[..., Any]] = []
        self.analyzers: list[Callable[..., Any]] = []
        self.recommenders: list[Callable[..., Any]] = []
        self.fixers: list[Callable[..., Any]] = []
        self.verifiers: list[Callable[..., Any]] = []
        self.exporters: list[Callable[..., Any]] = []

    def _append(self, attr_name: str, func: Callable[..., Any]) -> None:
        getattr(self, attr_name).append(func)

    def register_guard(self, func: Callable[..., Any]) -> None:
        self._append("guards", func)

    def register_before_apply(self, func: Callable[..., Any]) -> None:
        self._append("before_apply", func)

    def register_after_apply(self, func: Callable[..., Any]) -> None:
        self._append("after_apply", func)

    def register_support_resolver(self, func: Callable[..., Any]) -> None:
        self._append("support_resolvers", func)

    def register_target_detector(self, func: Callable[..., Any]) -> None:
        self._append("target_detectors", func)

    def register_collector(self, func: Callable[..., Any]) -> None:
        self._append("collectors", func)

    def register_context_enricher(self, func: Callable[..., Any]) -> None:
        self._append("context_enrichers", func)

    def register_analyzer(self, func: Callable[..., Any]) -> None:
        self._append("analyzers", func)

    def register_recommender(self, func: Callable[..., Any]) -> None:
        self._append("recommenders", func)

    def register_fixer(self, func: Callable[..., Any]) -> None:
        self._append("fixers", func)

    def register_verifier(self, func: Callable[..., Any]) -> None:
        self._append("verifiers", func)

    def register_exporter(self, func: Callable[..., Any]) -> None:
        self._append("exporters", func)


def empty_plugin_state() -> dict[str, Any]:
    state: dict[str, Any] = {
        "initialized": False,
        "base_dir": None,
        "plugins_dir": None,
        "active_dir": None,
        "templates_dir": None,
        "disabled_dir": None,
        "quarantine_dir": None,
        "archive_dir": None,
        "registry_path": None,
        "disabled_path": None,
        "logs_dir": None,
        "registry": {},
        "disabled_ids": set(),
        "manifests": {},
        "active_plugins": [],
        "runtime_version": PLUGIN_RUNTIME_VERSION,
        "load_summary": {
            "discovered": 0,
            "active": 0,
            "rejected": 0,
            "disabled": 0,
            "duplicate_ids": 0,
        },
    }
    for key in PHASE_BUCKETS:
        state[key] = []
    return state


def plugin_emit(level: str, message: str) -> None:
    print(f"[{level}] {message}")


def sanitize_plugin_token(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in {"-", "_", "."} else "_" for char in str(value))
    return safe.strip("._") or "plugin"


def load_json_file_safe(path_value: Path, default: Any) -> Any:
    if not path_value.exists():
        return default
    try:
        return json.loads(path_value.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json_file_safe(path_value: Path, data: Any) -> None:
    path_value.parent.mkdir(parents=True, exist_ok=True)
    safe_data = list(data) if isinstance(data, set) else data
    path_value.write_text(json.dumps(safe_data, indent=2, ensure_ascii=False), encoding="utf-8", newline="")


def hash_file_sha256(path_value: Path) -> str:
    digest = hashlib.sha256()
    with path_value.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def plugin_semver_tuple(value: str) -> tuple[int, int, int]:
    parts = [part for part in re.findall(r"\d+", str(value))[:3]]
    ints = [int(part) for part in parts]
    while len(ints) < 3:
        ints.append(0)
    return ints[0], ints[1], ints[2]


def plugin_runtime_satisfies(min_runtime: str | None) -> bool:
    if not min_runtime:
        return True
    return plugin_semver_tuple(PLUGIN_RUNTIME_VERSION) >= plugin_semver_tuple(min_runtime)


def parse_plugin_literal_value(text: str, name: str, default: str) -> str:
    pattern = rf"(?m)^\s*{re.escape(name)}\s*=\s*([\"\'])(.*?)\1\s*$"
    match = re.search(pattern, text)
    if not match:
        return default
    return str(match.group(2)).strip() or default


def discover_plugin_manifest(plugin_path: Path) -> PluginManifest:
    text = plugin_path.read_text(encoding="utf-8", errors="replace")
    transient_id = plugin_path.stem
    return PluginManifest(
        plugin_id=parse_plugin_literal_value(text, "PLUGIN_ID", transient_id),
        version=parse_plugin_literal_value(text, "PLUGIN_VERSION", "0.0.0"),
        description=parse_plugin_literal_value(text, "PLUGIN_DESCRIPTION", ""),
        min_runtime=parse_plugin_literal_value(text, "PLUGIN_MIN_RUNTIME", ""),
        file_name=plugin_path.name,
        path=str(plugin_path),
        hash=hash_file_sha256(plugin_path),
    )


def discover_plugin_files(plugins_dir: Path) -> list[Path]:
    if not plugins_dir.exists():
        return []
    active_dir = plugins_dir / PLUGIN_ACTIVE_DIR_NAME
    candidate_dirs: list[Path] = []
    if active_dir.exists():
        candidate_dirs.append(active_dir)
    if not active_dir.exists() or not any(active_dir.glob("*.py")):
        candidate_dirs.append(plugins_dir)
    files: list[Path] = []
    seen: set[Path] = set()
    for base in candidate_dirs:
        if not base.exists() or not base.is_dir():
            continue
        for path_value in sorted(base.glob("*.py")):
            lowered = path_value.name.lower()
            if lowered.startswith("_"):
                continue
            if "template" in lowered:
                continue
            resolved = path_value.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            files.append(resolved)
    return files


def load_disabled_plugin_ids(disabled_path: Path) -> set[str]:
    data = load_json_file_safe(disabled_path, {"disabled_plugin_ids": []})
    if isinstance(data, list):
        values = data
    elif isinstance(data, dict):
        values = data.get("disabled_plugin_ids", [])
    else:
        values = []
    return {str(value).strip() for value in values if str(value).strip()}


def normalize_plugin_self_test_result(result: Any) -> tuple[bool, str | None]:
    if result is None:
        return True, None
    if result is True:
        return True, None
    if result is False:
        return False, "plugin_self_test devolvió False"
    if isinstance(result, str):
        return True, result
    if isinstance(result, dict):
        if result.get("ok") is False:
            detail = str(result.get("reason") or result.get("message") or "plugin_self_test marcó ok=False")
            return False, detail
        detail = result.get("warning") or result.get("message")
        return True, str(detail) if detail else None
    return True, None


def update_plugin_registry_entry(
    state: dict[str, Any],
    manifest: PluginManifest,
    *,
    status: str,
    last_error: str | None = None,
    hook_counts: dict[str, int] | None = None,
    self_test_status: str | None = None,
    load_ms: int | None = None,
) -> None:
    registry = state["registry"]
    assert isinstance(registry, dict)
    previous = registry.get(manifest.plugin_id) if isinstance(registry.get(manifest.plugin_id), dict) else {}
    rejected_count = int((previous or {}).get("rejected_count") or 0)
    if status == "rejected":
        rejected_count += 1
    registry[manifest.plugin_id] = {
        "path": manifest.path,
        "file_name": manifest.file_name,
        "status": status,
        "version": manifest.version,
        "description": manifest.description,
        "min_runtime": manifest.min_runtime,
        "hash": manifest.hash,
        "runtime_version": PLUGIN_RUNTIME_VERSION,
        "last_loaded_at": datetime.now().isoformat(timespec="seconds"),
        "last_error": last_error,
        "hook_counts": hook_counts or {},
        "self_test_status": self_test_status,
        "rejected_count": rejected_count,
        "load_ms": load_ms,
    }


def _commit_plugin_hooks(state: dict[str, Any], plugin_id: str, api: PluginAPI) -> None:
    for key in PHASE_BUCKETS:
        for func in getattr(api, key, []):
            state[key].append({"plugin_id": plugin_id, "func": func})


def load_and_activate_plugin(state: dict[str, Any], plugin_path: Path, manifest: PluginManifest | None = None) -> None:
    started = time.perf_counter()
    manifest = manifest or discover_plugin_manifest(plugin_path)
    state["load_summary"]["discovered"] += 1
    disabled_ids = state.get("disabled_ids", set())
    if manifest.plugin_id in disabled_ids:
        state["load_summary"]["disabled"] += 1
        update_plugin_registry_entry(state, manifest, status="disabled")
        return
    seen_ids = {str(item.get("plugin_id")) for item in state.get("active_plugins", []) if isinstance(item, dict)}
    if manifest.plugin_id in seen_ids:
        state["load_summary"]["duplicate_ids"] += 1
        update_plugin_registry_entry(state, manifest, status="duplicate", last_error="duplicate plugin_id")
        return
    if not plugin_runtime_satisfies(manifest.min_runtime):
        state["load_summary"]["rejected"] += 1
        update_plugin_registry_entry(
            state,
            manifest,
            status="rejected",
            last_error=f"runtime {PLUGIN_RUNTIME_VERSION} no satisface min_runtime {manifest.min_runtime}",
            self_test_status="failed",
        )
        return
    try:
        module_name = f"capatch_plugin_{sanitize_plugin_token(manifest.plugin_id)}"
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("spec/loader inválido")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        api = PluginAPI(manifest.plugin_id, plugin_path)
        register_fn = getattr(module, "register", None)
        if callable(register_fn):
            register_fn(api)
        self_test_fn = getattr(module, "plugin_self_test", None)
        self_test_status = "not_declared"
        if callable(self_test_fn):
            ok, detail = normalize_plugin_self_test_result(self_test_fn(api))
            if not ok:
                raise RuntimeError(detail or "plugin_self_test falló")
            self_test_status = f"ok:{detail}" if detail else "ok"
        _commit_plugin_hooks(state, manifest.plugin_id, api)
        state["active_plugins"].append({"plugin_id": manifest.plugin_id, "version": manifest.version, "path": manifest.path})
        state["manifests"][manifest.plugin_id] = manifest.__dict__
        state["load_summary"]["active"] += 1
        update_plugin_registry_entry(
            state,
            manifest,
            status="active",
            hook_counts={key: len(getattr(api, key)) for key in PHASE_BUCKETS},
            self_test_status=self_test_status,
            load_ms=int((time.perf_counter() - started) * 1000),
        )
    except Exception as exc:
        state["load_summary"]["rejected"] += 1
        update_plugin_registry_entry(
            state,
            manifest,
            status="rejected",
            last_error=f"{type(exc).__name__}: {exc}",
            self_test_status="failed",
            load_ms=int((time.perf_counter() - started) * 1000),
        )
        logs_dir = state.get("logs_dir")
        if isinstance(logs_dir, Path):
            logs_dir.mkdir(parents=True, exist_ok=True)
            (logs_dir / f"{sanitize_plugin_token(manifest.plugin_id)}.log").write_text(
                traceback.format_exc(), encoding="utf-8"
            )


def initialize_plugin_runtime(base_dir: Path) -> dict[str, Any]:
    state = empty_plugin_state()
    plugins_dir = (base_dir / PLUGIN_DIR_NAME).resolve()
    active_dir = plugins_dir / PLUGIN_ACTIVE_DIR_NAME
    templates_dir = plugins_dir / PLUGIN_TEMPLATES_DIR_NAME
    disabled_dir = plugins_dir / PLUGIN_DISABLED_DIR_NAME
    quarantine_dir = plugins_dir / PLUGIN_QUARANTINE_DIR_NAME
    archive_dir = plugins_dir / PLUGIN_ARCHIVE_DIR_NAME
    logs_dir = plugins_dir / PLUGIN_LOGS_DIR_NAME
    registry_path = plugins_dir / PLUGIN_REGISTRY_NAME
    disabled_path = plugins_dir / PLUGIN_DISABLED_NAME
    for path_value in [plugins_dir, active_dir, templates_dir, disabled_dir, quarantine_dir, archive_dir, logs_dir]:
        path_value.mkdir(parents=True, exist_ok=True)
    state.update(
        {
            "initialized": True,
            "base_dir": base_dir.resolve(),
            "plugins_dir": plugins_dir,
            "active_dir": active_dir,
            "templates_dir": templates_dir,
            "disabled_dir": disabled_dir,
            "quarantine_dir": quarantine_dir,
            "archive_dir": archive_dir,
            "registry_path": registry_path,
            "disabled_path": disabled_path,
            "logs_dir": logs_dir,
            "registry": load_json_file_safe(registry_path, {}),
            "disabled_ids": load_disabled_plugin_ids(disabled_path),
        }
    )
    for plugin_path in discover_plugin_files(plugins_dir):
        manifest = discover_plugin_manifest(plugin_path)
        load_and_activate_plugin(state, plugin_path, manifest)
    save_json_file_safe(registry_path, state["registry"])
    save_json_file_safe(disabled_path, {"disabled_plugin_ids": sorted(state["disabled_ids"])})
    return state
