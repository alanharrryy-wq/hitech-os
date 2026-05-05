#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, NoReturn

from capatch_engine.support_resolution import SupportResolution
from capatch_ops.base import CapatchError

try:
    from capatch_contracts.plugin_runtime import (
        CAPATCH_PLUGIN_RUNTIME_VERSION as _CONTRACT_PLUGIN_RUNTIME_VERSION,
        summarize_essential_runtime_health,
    )
except ImportError:
    from capatch_contracts.versions import CAPATCH_PLUGIN_RUNTIME_VERSION as _CONTRACT_PLUGIN_RUNTIME_VERSION

    def summarize_essential_runtime_health(
        runtime_version,
        registry,
        essential_plugin_ids=(),
        capability_map=None,
    ):
        registry = registry if isinstance(registry, dict) else {}
        missing = [
            str(plugin_id)
            for plugin_id in essential_plugin_ids
            if str(plugin_id) not in registry
        ]
        return {
            "status": "healthy" if not missing else "degraded",
            "runtime_version": runtime_version,
            "essential_plugin_ids": list(essential_plugin_ids),
            "active": [],
            "missing": missing,
            "rejected": [],
            "disabled": [],
            "duplicate": [],
            "healthy": not missing,
            "missing_capabilities": [],
        }


def fail(message: str) -> NoReturn:
    raise CapatchError(message)

# === CAPATCH PLUGIN RUNTIME START ===
CAPATCH_PLUGIN_DIR_NAME = "capatch_plugins"
CAPATCH_PLUGIN_ACTIVE_DIR_NAME = "active"
CAPATCH_PLUGIN_TEMPLATES_DIR_NAME = "templates"
CAPATCH_PLUGIN_DISABLED_DIR_NAME = "disabled"
CAPATCH_PLUGIN_QUARANTINE_DIR_NAME = "quarantine"
CAPATCH_PLUGIN_ARCHIVE_DIR_NAME = "archive"
CAPATCH_PLUGIN_REGISTRY_NAME = "_plugin_registry.json"
CAPATCH_PLUGIN_DISABLED_NAME = "_plugin_disabled.json"
CAPATCH_PLUGIN_LOGS_DIR_NAME = "_logs"

CAPATCH_PLUGIN_RUNTIME_VERSION = _CONTRACT_PLUGIN_RUNTIME_VERSION
CAPATCH_PLUGIN_DEFAULT_TAIL_LINES = 80

CAPATCH_PLUGIN_STATE: dict[str, Any] = {
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
    "guards": [],
    "before_apply": [],
    "after_apply": [],
    "support_resolvers": [],
    "active_plugins": [],
    "runtime_version": CAPATCH_PLUGIN_RUNTIME_VERSION,
    "load_summary": {
        "discovered": 0,
        "active": 0,
        "rejected": 0,
        "disabled": 0,
        "duplicate_ids": 0,
    },
}

def plugin_emit(level: str, message: str) -> None:
    print(f"[{level}] {message}")

def sanitize_plugin_token(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in {"-", "_", "."} else "_" for char in str(value))
    return safe.strip("._") or "plugin"

def plugin_log_path(plugin_id: str) -> Path | None:
    logs_dir = CAPATCH_PLUGIN_STATE.get("logs_dir")
    if not isinstance(logs_dir, Path):
        return None
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir / f"{sanitize_plugin_token(plugin_id)}.log"

def plugin_append_log(plugin_id: str, stage: str, message: str, exc: Exception | None = None) -> None:
    log_path = plugin_log_path(plugin_id)
    timestamp = datetime.now().isoformat(timespec="seconds")
    payload = [f"[{timestamp}] [{stage}] {message}"]
    if exc is not None:
        payload.append(f"{type(exc).__name__}: {exc}")
        payload.append(traceback.format_exc())

    if log_path is None:
        for line in payload:
            plugin_emit("WARN", line)
        return

    with log_path.open("a", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(payload))
        fh.write("\n\n")

def load_json_file_safe(path_value: Path, default: Any) -> Any:
    if not path_value.exists():
        return default
    try:
        return json.loads(path_value.read_text(encoding="utf-8"))
    except Exception as exc:
        plugin_append_log("plugin-system", "registry-read", f"No pude leer JSON {path_value}", exc)
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
    return plugin_semver_tuple(CAPATCH_PLUGIN_RUNTIME_VERSION) >= plugin_semver_tuple(min_runtime)

def read_plugin_text_safe(plugin_path: Path) -> str:
    return plugin_path.read_text(encoding="utf-8", errors="replace")

def parse_plugin_literal_value(text: str, name: str, default: str) -> str:
    pattern = rf"(?m)^\s*{re.escape(name)}\s*=\s*([\"\'])(.*?)\1\s*$"
    match = re.search(pattern, text)
    if not match:
        return default
    return str(match.group(2)).strip() or default

def discover_plugin_manifest(plugin_path: Path) -> dict[str, Any]:
    text = read_plugin_text_safe(plugin_path)
    transient_id = plugin_path.stem
    manifest = {
        "plugin_id": parse_plugin_literal_value(text, "PLUGIN_ID", transient_id),
        "version": parse_plugin_literal_value(text, "PLUGIN_VERSION", "0.0.0"),
        "description": parse_plugin_literal_value(text, "PLUGIN_DESCRIPTION", ""),
        "min_runtime": parse_plugin_literal_value(text, "PLUGIN_MIN_RUNTIME", ""),
        "file_name": plugin_path.name,
        "path": str(plugin_path),
        "hash": hash_file_sha256(plugin_path),
    }
    return manifest

class PluginAPI:
    def __init__(self, plugin_id: str, plugin_path: Path) -> None:
        self.plugin_id = plugin_id
        self.plugin_path = plugin_path
        self.guards: list[Any] = []
        self.before_apply: list[Any] = []
        self.after_apply: list[Any] = []
        self.support_resolvers: list[Any] = []

    def register_guard(self, func: Any) -> None:
        self.guards.append(func)

    def register_before_apply(self, func: Any) -> None:
        self.before_apply.append(func)

    def register_after_apply(self, func: Any) -> None:
        self.after_apply.append(func)

    def register_support_resolver(self, func: Any) -> None:
        self.support_resolvers.append(func)

def discover_plugin_files(plugins_dir: Path) -> list[Path]:
    if not plugins_dir.exists():
        return []

    active_dir = plugins_dir / CAPATCH_PLUGIN_ACTIVE_DIR_NAME
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
            name = path_value.name.lower()
            if name.startswith("_"):
                continue
            if "template" in name:
                continue
            resolved = path_value.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            files.append(resolved)
    return files

def commit_plugin_hooks(plugin_id: str, api: PluginAPI) -> None:
    for func in api.guards:
        CAPATCH_PLUGIN_STATE["guards"].append({"plugin_id": plugin_id, "func": func})
    for func in api.before_apply:
        CAPATCH_PLUGIN_STATE["before_apply"].append({"plugin_id": plugin_id, "func": func})
    for func in api.after_apply:
        CAPATCH_PLUGIN_STATE["after_apply"].append({"plugin_id": plugin_id, "func": func})
    for func in api.support_resolvers:
        CAPATCH_PLUGIN_STATE["support_resolvers"].append({"plugin_id": plugin_id, "func": func})

def load_disabled_plugin_ids(disabled_path: Path) -> set[str]:
    data = load_json_file_safe(disabled_path, {"disabled_plugin_ids": []})
    if isinstance(data, list):
        values = data
    elif isinstance(data, dict):
        values = data.get("disabled_plugin_ids", [])
    else:
        values = []
    return {str(value).strip() for value in values if str(value).strip()}

def save_disabled_plugin_ids() -> None:
    disabled_path = CAPATCH_PLUGIN_STATE.get("disabled_path")
    disabled_ids = CAPATCH_PLUGIN_STATE.get("disabled_ids")
    if not isinstance(disabled_path, Path):
        return
    values = sorted(str(value) for value in disabled_ids if str(value).strip()) if isinstance(disabled_ids, set) else []
    save_json_file_safe(disabled_path, {"disabled_plugin_ids": values})

def update_plugin_registry_entry(
    plugin_id: str,
    plugin_path: Path,
    *,
    status: str,
    plugin_hash: str,
    version: str,
    description: str = "",
    min_runtime: str = "",
    last_error: str | None = None,
    hook_counts: dict[str, int] | None = None,
    self_test_status: str | None = None,
    load_ms: int | None = None,
) -> None:
    registry = CAPATCH_PLUGIN_STATE["registry"]
    assert isinstance(registry, dict)
    previous_raw = registry.get(plugin_id)
    previous: dict[str, Any] = previous_raw if isinstance(previous_raw, dict) else {}
    rejected_count = int(previous.get("rejected_count") or 0)
    if status == "rejected":
        rejected_count += 1

    registry[plugin_id] = {
        "path": str(plugin_path),
        "file_name": plugin_path.name,
        "status": status,
        "version": version,
        "description": description,
        "min_runtime": min_runtime,
        "hash": plugin_hash,
        "runtime_version": CAPATCH_PLUGIN_RUNTIME_VERSION,
        "last_loaded_at": datetime.now().isoformat(timespec="seconds"),
        "last_error": last_error,
        "hook_counts": hook_counts or {},
        "self_test_status": self_test_status,
        "rejected_count": rejected_count,
        "load_ms": load_ms,
    }

def normalize_plugin_self_test_result(result: Any) -> tuple[bool, str | None]:
    if result is None:
        return True, None
    if result is True:
        return True, None
    if result is False:
        return False, "plugin_self_test devolvio False"
    if isinstance(result, str):
        return True, result
    if isinstance(result, dict):
        if result.get("ok") is False:
            detail = str(result.get("reason") or result.get("message") or "plugin_self_test marco ok=False")
            return False, detail
        detail = result.get("warning") or result.get("message")
        return True, str(detail) if detail else None
    return True, None

def plugin_registry_snapshot() -> list[dict[str, Any]]:
    registry = CAPATCH_PLUGIN_STATE.get("registry")
    if not isinstance(registry, dict):
        return []
    rows: list[dict[str, Any]] = []
    for plugin_id in sorted(registry):
        value = registry.get(plugin_id)
        if isinstance(value, dict):
            row = dict(value)
            row["plugin_id"] = plugin_id
            rows.append(row)
    return rows

def plugin_print_registry_summary(verbose: bool = False) -> None:
    rows = plugin_registry_snapshot()
    if not rows:
        plugin_emit("INFO", "Plugin registry vacio.")
        return
    for row in rows:
        base = (
            "PluginRegistry | "
            f"id={row.get('plugin_id')} | status={row.get('status')} | "
            f"version={row.get('version')} | file={row.get('file_name')} | "
            f"self_test={row.get('self_test_status')}"
        )
        if verbose:
            base += (
                f" | min_runtime={row.get('min_runtime') or '-'} | "
                f"load_ms={row.get('load_ms')} | desc={row.get('description') or '-'}"
            )
        plugin_emit("INFO", base)

def plugin_emit_health_report() -> None:
    summary_raw = CAPATCH_PLUGIN_STATE.get("load_summary")
    summary: dict[str, Any] = summary_raw if isinstance(summary_raw, dict) else {}
    registry_raw = CAPATCH_PLUGIN_STATE.get("registry")
    registry = registry_raw if isinstance(registry_raw, dict) else {}
    essential = summarize_essential_runtime_health(CAPATCH_PLUGIN_RUNTIME_VERSION, registry)
    plugin_emit(
        "INFO",
        "PluginHealth | "
        f"runtime={CAPATCH_PLUGIN_RUNTIME_VERSION} | "
        f"status={essential.get('status')} | "
        f"discovered={summary.get('discovered', 0)} | "
        f"active={summary.get('active', 0)} | "
        f"rejected={summary.get('rejected', 0)} | "
        f"disabled={summary.get('disabled', 0)} | "
        f"duplicate_ids={summary.get('duplicate_ids', 0)} | "
        f"essential_missing={len(essential.get('missing', []))} | "
        f"essential_rejected={len(essential.get('rejected', []))}",
    )
    if essential.get("status") != "healthy":
        plugin_emit(
            "WARN",
            "PluginHealthEssential | "
            f"missing={','.join(essential.get('missing', [])) or '-'} | "
            f"rejected={','.join(essential.get('rejected', [])) or '-'} | "
            f"disabled={','.join(essential.get('disabled', [])) or '-'} | "
            f"duplicate={','.join(essential.get('duplicate', [])) or '-'}",
        )
    plugin_print_registry_summary(verbose=True)

def plugin_disable_state_contains(plugin_id: str, plugin_path: Path | None = None) -> bool:
    disabled_ids = CAPATCH_PLUGIN_STATE.get("disabled_ids")
    if not isinstance(disabled_ids, set):
        return False
    tokens = {str(plugin_id).strip()}
    if plugin_path is not None:
        tokens.add(plugin_path.stem)
        tokens.add(plugin_path.name)
    return any(token in disabled_ids for token in tokens if token)

def plugin_set_enabled_state(plugin_id: str, enabled: bool) -> str:
    disabled_ids = CAPATCH_PLUGIN_STATE.get("disabled_ids")
    registry = CAPATCH_PLUGIN_STATE.get("registry")
    if not isinstance(disabled_ids, set) or not isinstance(registry, dict):
        return "Runtime de plugins no inicializado."

    plugin_id = str(plugin_id).strip()
    if not plugin_id:
        return "PLUGIN_ID vacio."

    if enabled:
        disabled_ids.discard(plugin_id)
    else:
        disabled_ids.add(plugin_id)

    row = registry.get(plugin_id)
    if isinstance(row, dict):
        row["status"] = "pending_reload" if enabled else "disabled"
        row["last_error"] = None if enabled else row.get("last_error")
    else:
        registry[plugin_id] = {
            "path": "",
            "file_name": "",
            "status": "pending_reload" if enabled else "disabled",
            "version": "0.0.0",
            "description": "",
            "min_runtime": "",
            "hash": "",
            "runtime_version": CAPATCH_PLUGIN_RUNTIME_VERSION,
            "last_loaded_at": datetime.now().isoformat(timespec="seconds"),
            "last_error": None,
            "hook_counts": {},
            "self_test_status": None,
            "rejected_count": 0,
            "load_ms": None,
        }

    save_disabled_plugin_ids()
    registry_path = CAPATCH_PLUGIN_STATE.get("registry_path")
    if isinstance(registry_path, Path):
        save_json_file_safe(registry_path, registry)
    return f"Plugin {'habilitado' if enabled else 'deshabilitado'}: {plugin_id}"

def plugin_print_log_tail(plugin_id: str, tail_lines: int) -> None:
    log_path = plugin_log_path(plugin_id)
    if log_path is None or not log_path.exists():
        plugin_emit("WARN", f"No existe log para plugin {plugin_id}")
        return
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    tail = lines[-max(1, int(tail_lines)):]
    plugin_emit("INFO", f"LogTail {plugin_id} | lines={len(tail)} | path={log_path}")
    for line in tail:
        print(line)

def commit_disabled_plugin(manifest: dict[str, Any], plugin_path: Path) -> None:
    plugin_id = str(manifest.get("plugin_id") or plugin_path.stem)
    CAPATCH_PLUGIN_STATE["load_summary"]["disabled"] += 1
    update_plugin_registry_entry(
        plugin_id,
        plugin_path,
        status="disabled",
        plugin_hash=str(manifest.get("hash") or hash_file_sha256(plugin_path)),
        version=str(manifest.get("version") or "0.0.0"),
        description=str(manifest.get("description") or ""),
        min_runtime=str(manifest.get("min_runtime") or ""),
        self_test_status="skipped:disabled",
    )

def load_and_activate_plugin(plugin_path: Path, manifest: dict[str, Any] | None = None) -> None:
    manifest = manifest or discover_plugin_manifest(plugin_path)
    plugin_hash = str(manifest.get("hash") or hash_file_sha256(plugin_path))
    transient_id = plugin_path.stem
    module_name = f"_capatch_plugin_{sanitize_plugin_token(plugin_path.stem)}_{plugin_hash[:12]}"
    CAPATCH_PLUGIN_STATE["load_summary"]["discovered"] += 1
    started = time.perf_counter()

    try:
        plugin_id = str(manifest.get("plugin_id") or transient_id).strip() or transient_id
        plugin_version = str(manifest.get("version") or "0.0.0").strip() or "0.0.0"
        plugin_description = str(manifest.get("description") or "")
        min_runtime = str(manifest.get("min_runtime") or "")

        if plugin_disable_state_contains(plugin_id, plugin_path):
            commit_disabled_plugin(manifest, plugin_path)
            plugin_emit("INFO", f"Plugin deshabilitado omitido: {plugin_id}")
            return

        if min_runtime and not plugin_runtime_satisfies(min_runtime):
            raise RuntimeError(
                f"PLUGIN_MIN_RUNTIME={min_runtime} requiere runtime mas nuevo que {CAPATCH_PLUGIN_RUNTIME_VERSION}"
            )

        for item in CAPATCH_PLUGIN_STATE["active_plugins"]:
            if str(item.get("plugin_id")) == plugin_id:
                CAPATCH_PLUGIN_STATE["load_summary"]["duplicate_ids"] += 1
                raise RuntimeError(f"PLUGIN_ID duplicado detectado: {plugin_id}")

        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("spec/loader invalido")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        api = PluginAPI(plugin_id, plugin_path)

        register_fn = getattr(module, "register", None)
        if callable(register_fn):
            register_fn(api)

        self_test_fn = getattr(module, "plugin_self_test", None)
        self_test_status = "not_declared"
        if callable(self_test_fn):
            test_ok, test_message = normalize_plugin_self_test_result(self_test_fn(api))
            if not test_ok:
                raise RuntimeError(test_message or "plugin_self_test fallo")
            self_test_status = f"ok:{test_message}" if test_message else "ok"

        commit_plugin_hooks(plugin_id, api)
        CAPATCH_PLUGIN_STATE["active_plugins"].append(
            {
                "plugin_id": plugin_id,
                "version": plugin_version,
                "path": str(plugin_path),
            }
        )
        CAPATCH_PLUGIN_STATE["load_summary"]["active"] += 1
        load_ms = int((time.perf_counter() - started) * 1000)
        update_plugin_registry_entry(
            plugin_id,
            plugin_path,
            status="active",
            plugin_hash=plugin_hash,
            version=plugin_version,
            description=plugin_description,
            min_runtime=min_runtime,
            hook_counts={
                "guards": len(api.guards),
                "before_apply": len(api.before_apply),
                "after_apply": len(api.after_apply),
                "support_resolvers": len(api.support_resolvers),
            },
            self_test_status=self_test_status,
            load_ms=load_ms,
        )
        plugin_emit("INFO", f"Plugin activo: {plugin_id} v{plugin_version}")
    except Exception as exc:
        plugin_id = str(manifest.get("plugin_id") or transient_id)
        CAPATCH_PLUGIN_STATE["load_summary"]["rejected"] += 1
        plugin_append_log(plugin_id, "load", f"Plugin rechazado: {plugin_path}", exc)
        update_plugin_registry_entry(
            plugin_id,
            plugin_path,
            status="rejected",
            plugin_hash=plugin_hash,
            version=str(manifest.get("version") or "0.0.0"),
            description=str(manifest.get("description") or ""),
            min_runtime=str(manifest.get("min_runtime") or ""),
            last_error=f"{type(exc).__name__}: {exc}",
            self_test_status="failed",
            load_ms=int((time.perf_counter() - started) * 1000),
        )
        plugin_emit("WARN", f"Plugin rechazado: {plugin_path.name} ({exc})")

def initialize_plugin_runtime(base_dir: Path) -> None:
    plugins_dir = (base_dir / CAPATCH_PLUGIN_DIR_NAME).resolve()
    active_dir = plugins_dir / CAPATCH_PLUGIN_ACTIVE_DIR_NAME
    templates_dir = plugins_dir / CAPATCH_PLUGIN_TEMPLATES_DIR_NAME
    disabled_dir = plugins_dir / CAPATCH_PLUGIN_DISABLED_DIR_NAME
    quarantine_dir = plugins_dir / CAPATCH_PLUGIN_QUARANTINE_DIR_NAME
    archive_dir = plugins_dir / CAPATCH_PLUGIN_ARCHIVE_DIR_NAME
    logs_dir = plugins_dir / CAPATCH_PLUGIN_LOGS_DIR_NAME
    registry_path = plugins_dir / CAPATCH_PLUGIN_REGISTRY_NAME
    disabled_path = plugins_dir / CAPATCH_PLUGIN_DISABLED_NAME

    for path_value in [plugins_dir, active_dir, templates_dir, disabled_dir, quarantine_dir, archive_dir, logs_dir]:
        path_value.mkdir(parents=True, exist_ok=True)

    CAPATCH_PLUGIN_STATE["initialized"] = True
    CAPATCH_PLUGIN_STATE["base_dir"] = base_dir.resolve()
    CAPATCH_PLUGIN_STATE["plugins_dir"] = plugins_dir
    CAPATCH_PLUGIN_STATE["active_dir"] = active_dir
    CAPATCH_PLUGIN_STATE["templates_dir"] = templates_dir
    CAPATCH_PLUGIN_STATE["disabled_dir"] = disabled_dir
    CAPATCH_PLUGIN_STATE["quarantine_dir"] = quarantine_dir
    CAPATCH_PLUGIN_STATE["archive_dir"] = archive_dir
    CAPATCH_PLUGIN_STATE["registry_path"] = registry_path
    CAPATCH_PLUGIN_STATE["disabled_path"] = disabled_path
    CAPATCH_PLUGIN_STATE["logs_dir"] = logs_dir
    CAPATCH_PLUGIN_STATE["guards"] = []
    CAPATCH_PLUGIN_STATE["before_apply"] = []
    CAPATCH_PLUGIN_STATE["after_apply"] = []
    CAPATCH_PLUGIN_STATE["support_resolvers"] = []
    CAPATCH_PLUGIN_STATE["active_plugins"] = []
    CAPATCH_PLUGIN_STATE["manifests"] = {}
    CAPATCH_PLUGIN_STATE["load_summary"] = {
        "discovered": 0,
        "active": 0,
        "rejected": 0,
        "disabled": 0,
        "duplicate_ids": 0,
    }
    CAPATCH_PLUGIN_STATE["registry"] = load_json_file_safe(registry_path, {})
    CAPATCH_PLUGIN_STATE["disabled_ids"] = load_disabled_plugin_ids(disabled_path)

    discovered_from = active_dir if any(active_dir.glob("*.py")) else plugins_dir
    for plugin_path in discover_plugin_files(plugins_dir):
        manifest = discover_plugin_manifest(plugin_path)
        CAPATCH_PLUGIN_STATE["manifests"][manifest["plugin_id"]] = manifest
        load_and_activate_plugin(plugin_path, manifest)

    save_json_file_safe(registry_path, CAPATCH_PLUGIN_STATE["registry"])
    save_disabled_plugin_ids()
    plugin_emit(
        "INFO",
        "Plugin runtime listo. "
        f"v={CAPATCH_PLUGIN_RUNTIME_VERSION} | "
        f"activos={CAPATCH_PLUGIN_STATE['load_summary']['active']} | "
        f"rechazados={CAPATCH_PLUGIN_STATE['load_summary']['rejected']} | "
        f"deshabilitados={CAPATCH_PLUGIN_STATE['load_summary']['disabled']} | "
        f"dir={discovered_from}",
    )

# === CAPATCH DIAGNOSTIC RUNTIME EXTENSION START ===
_ORIGINAL_PLUGINAPI_INIT = PluginAPI.__init__

def _diagnostic_pluginapi_init(self, plugin_id: str, plugin_path: Path) -> None:
    _ORIGINAL_PLUGINAPI_INIT(self, plugin_id, plugin_path)
    self.target_detectors = []
    self.collectors = []
    self.context_enrichers = []
    self.analyzers = []
    self.recommenders = []
    self.fixers = []
    self.verifiers = []
    self.exporters = []

PluginAPI.__init__ = _diagnostic_pluginapi_init

def _pluginapi_append(api_self: PluginAPI, attr_name: str, func: Any) -> None:
    bucket = getattr(api_self, attr_name, None)
    if bucket is None:
        bucket = []
        setattr(api_self, attr_name, bucket)
    bucket.append(func)

def _pluginapi_register_target_detector(self, func: Any) -> None:
    _pluginapi_append(self, "target_detectors", func)

def _pluginapi_register_collector(self, func: Any) -> None:
    _pluginapi_append(self, "collectors", func)

def _pluginapi_register_context_enricher(self, func: Any) -> None:
    _pluginapi_append(self, "context_enrichers", func)

def _pluginapi_register_analyzer(self, func: Any) -> None:
    _pluginapi_append(self, "analyzers", func)

def _pluginapi_register_recommender(self, func: Any) -> None:
    _pluginapi_append(self, "recommenders", func)

def _pluginapi_register_fixer(self, func: Any) -> None:
    _pluginapi_append(self, "fixers", func)

def _pluginapi_register_verifier(self, func: Any) -> None:
    _pluginapi_append(self, "verifiers", func)

def _pluginapi_register_exporter(self, func: Any) -> None:
    _pluginapi_append(self, "exporters", func)

PluginAPI.register_target_detector = _pluginapi_register_target_detector
PluginAPI.register_collector = _pluginapi_register_collector
PluginAPI.register_context_enricher = _pluginapi_register_context_enricher
PluginAPI.register_analyzer = _pluginapi_register_analyzer
PluginAPI.register_recommender = _pluginapi_register_recommender
PluginAPI.register_fixer = _pluginapi_register_fixer
PluginAPI.register_verifier = _pluginapi_register_verifier
PluginAPI.register_exporter = _pluginapi_register_exporter

_ORIGINAL_COMMIT_PLUGIN_HOOKS = commit_plugin_hooks

def commit_plugin_hooks(plugin_id: str, api: PluginAPI) -> None:
    _ORIGINAL_COMMIT_PLUGIN_HOOKS(plugin_id, api)
    for attr_name, state_key in [
        ("target_detectors", "target_detectors"),
        ("collectors", "collectors"),
        ("context_enrichers", "context_enrichers"),
        ("analyzers", "analyzers"),
        ("recommenders", "recommenders"),
        ("fixers", "fixers"),
        ("verifiers", "verifiers"),
        ("exporters", "exporters"),
    ]:
        bucket = CAPATCH_PLUGIN_STATE.setdefault(state_key, [])
        for func in getattr(api, attr_name, []):
            bucket.append({"plugin_id": plugin_id, "func": func})

_ORIGINAL_INITIALIZE_PLUGIN_RUNTIME = initialize_plugin_runtime

def initialize_plugin_runtime(base_dir: Path) -> None:
    _ORIGINAL_INITIALIZE_PLUGIN_RUNTIME(base_dir)
    for key in [
        "target_detectors",
        "collectors",
        "context_enrichers",
        "analyzers",
        "recommenders",
        "fixers",
        "verifiers",
        "exporters",
    ]:
        CAPATCH_PLUGIN_STATE.setdefault(key, [])
# === CAPATCH DIAGNOSTIC RUNTIME EXTENSION END ===

def handle_plugin_cli_actions(args: Any) -> bool:
    if getattr(args, "plugin_disable", None):
        plugin_emit("INFO", plugin_set_enabled_state(str(args.plugin_disable), enabled=False))
        return True

    if getattr(args, "plugin_enable", None):
        plugin_emit("INFO", plugin_set_enabled_state(str(args.plugin_enable), enabled=True))
        return True

    if getattr(args, "plugin_show_log", None):
        tail_lines = int(getattr(args, "plugin_tail_lines", CAPATCH_PLUGIN_DEFAULT_TAIL_LINES) or CAPATCH_PLUGIN_DEFAULT_TAIL_LINES)
        plugin_print_log_tail(str(args.plugin_show_log), tail_lines)
        return True

    if getattr(args, "plugin_list", False):
        plugin_print_registry_summary(verbose=True)
        return True

    if getattr(args, "plugin_health", False) or getattr(args, "plugin_retest", False):
        plugin_emit_health_report()
        return True

    return False

def interpret_plugin_guard_result(plugin_id: str, result: Any) -> None:
    if result is None or result is True:
        return

    if result is False:
        fail(f"Plugin {plugin_id} bloqueo la ejecucion sin detalle adicional.")

    if isinstance(result, str):
        plugin_emit("WARN", f"Plugin {plugin_id}: {result}")
        return

    if isinstance(result, dict):
        warning = result.get("warning")
        if warning:
            plugin_emit("WARN", f"Plugin {plugin_id}: {warning}")

        if result.get("allow") is False:
            reason = str(result.get("reason") or result.get("message") or "sin detalle")
            fail(f"Plugin {plugin_id} bloqueo la ejecucion: {reason}")
        return

    plugin_emit("WARN", f"Plugin {plugin_id}: resultado no reconocido {type(result).__name__}")

def run_plugins_before_apply(
    ctx: PatchContext,
    operations: Iterable[Operation],
    preview_content_by_target: dict[Path, str],
) -> None:
    if not CAPATCH_PLUGIN_STATE.get("initialized"):
        return

    operations_list = list(operations)

    for item in CAPATCH_PLUGIN_STATE["guards"]:
        plugin_id = str(item["plugin_id"])
        func = item["func"]
        try:
            result = func(ctx, operations_list, preview_content_by_target)
            interpret_plugin_guard_result(plugin_id, result)
        except CapatchError:
            raise
        except Exception as exc:
            plugin_append_log(plugin_id, "guard", "Error en guard; se continua sin el plugin", exc)
            plugin_emit("WARN", f"Plugin {plugin_id} fallo en guard; se continua sin el plugin")

    for item in CAPATCH_PLUGIN_STATE["before_apply"]:
        plugin_id = str(item["plugin_id"])
        func = item["func"]
        try:
            func(ctx, operations_list, preview_content_by_target)
        except Exception as exc:
            plugin_append_log(plugin_id, "before_apply", "Error en before_apply; se continua", exc)
            plugin_emit("WARN", f"Plugin {plugin_id} fallo en before_apply; se continua")

def run_plugins_after_apply(
    ctx: PatchContext,
    operations: Iterable[Operation],
    results: list[str],
) -> None:
    if not CAPATCH_PLUGIN_STATE.get("initialized"):
        return

    operations_list = list(operations)

    for item in CAPATCH_PLUGIN_STATE["after_apply"]:
        plugin_id = str(item["plugin_id"])
        func = item["func"]
        try:
            func(ctx, operations_list, results)
        except Exception as exc:
            plugin_append_log(plugin_id, "after_apply", "Error en after_apply; se continua", exc)
            plugin_emit("WARN", f"Plugin {plugin_id} fallo en after_apply; se continua")

def resolve_support_resolution_with_plugins(
    ctx: PatchContext,
    target: Path,
    content: str,
    operation: BaseOperation,
    field_name: str,
    field_value: str,
) -> SupportResolution | None:
    if not CAPATCH_PLUGIN_STATE.get("initialized"):
        return None

    for item in CAPATCH_PLUGIN_STATE["support_resolvers"]:
        plugin_id = str(item["plugin_id"])
        func = item["func"]
        try:
            result = func(ctx, target, content, operation, field_name, field_value)
            if result is None:
                continue

            if isinstance(result, SupportResolution):
                return result

            if isinstance(result, str):
                return SupportResolution(
                    field_name=field_name,
                    original_value=field_value,
                    resolved_value=result,
                    strategy=f"plugin:{plugin_id}",
                )

            if isinstance(result, dict):
                resolved_value = result.get("resolved_value")
                if resolved_value is None:
                    continue
                strategy = str(result.get("strategy") or f"plugin:{plugin_id}")
                return SupportResolution(
                    field_name=field_name,
                    original_value=field_value,
                    resolved_value=str(resolved_value),
                    strategy=strategy,
                )
        except Exception as exc:
            plugin_append_log(plugin_id, "support_resolver", "Error en support_resolver; se continua", exc)
            plugin_emit("WARN", f"Plugin {plugin_id} fallo en support_resolver; se continua")

    return None
# === CAPATCH PLUGIN RUNTIME END ===


def get_plugin_state() -> dict[str, Any]:
    return CAPATCH_PLUGIN_STATE


__all__ = [
    'CAPATCH_PLUGIN_DEFAULT_TAIL_LINES',
    'CAPATCH_PLUGIN_RUNTIME_VERSION',
    'CAPATCH_PLUGIN_STATE',
    'PluginAPI',
    'get_plugin_state',
    'handle_plugin_cli_actions',
    'initialize_plugin_runtime',
    'plugin_runtime_satisfies',
    'resolve_support_resolution_with_plugins',
    'run_plugins_after_apply',
    'run_plugins_before_apply',
]

