#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

r"""
Actualizador idempotente para subir capatch.py a un runtime de plugins v3,
con varias mejoras de soporte y operacion.

Mejoras principales:
- listado de plugins desde capatch (--plugin-list)
- health check y re-test de plugins (--plugin-health / --plugin-retest)
- habilitar/deshabilitar plugins sin borrar archivos (--plugin-enable / --plugin-disable)
- ver log de un plugin (--plugin-show-log)
- autodeteccion de PLUGIN_ID sin ejecutar plugins deshabilitados
- cuarentena y registro mas rico (descripcion, version, runtime minimo, errores)
- templates nuevos de plugins base
- compatibilidad con capatch limpio, v1 o v2
"""

import argparse
import py_compile
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_CAPATCH_PATH = Path(r"F:\OneDrive\Descargas\capatch.py")
DEFAULT_LOG_PATH = Path(r"F:\OneDrive\Descargas\capatch_plugin_upgrade_v3.log")

PLUGIN_RUNTIME_START = "# === CAPATCH PLUGIN RUNTIME START ==="
PLUGIN_RUNTIME_END = "# === CAPATCH PLUGIN RUNTIME END ==="

REQUIRED_IMPORTS = [
    "import hashlib",
    "import importlib.util",
    "import time",
    "import traceback",
]

PLUGIN_RUNTIME_BLOCK = r'''
# === CAPATCH PLUGIN RUNTIME START ===
CAPATCH_PLUGIN_DIR_NAME = "capatch_plugins"
CAPATCH_PLUGIN_REGISTRY_NAME = "_plugin_registry.json"
CAPATCH_PLUGIN_DISABLED_NAME = "_plugin_disabled.json"
CAPATCH_PLUGIN_LOGS_DIR_NAME = "_logs"
CAPATCH_PLUGIN_RUNTIME_VERSION = "3.0.0"
CAPATCH_PLUGIN_DEFAULT_TAIL_LINES = 80

CAPATCH_PLUGIN_STATE: dict[str, Any] = {
    "initialized": False,
    "base_dir": None,
    "plugins_dir": None,
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
    return tuple(ints[:3])


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

    files: list[Path] = []
    for path_value in sorted(plugins_dir.glob("*.py")):
        name = path_value.name.lower()
        if name.startswith("_"):
            continue
        if "template" in name:
            continue
        files.append(path_value.resolve())
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
    previous = registry.get(plugin_id) if isinstance(registry.get(plugin_id), dict) else {}
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
    summary = CAPATCH_PLUGIN_STATE.get("load_summary") if isinstance(CAPATCH_PLUGIN_STATE.get("load_summary"), dict) else {}
    plugin_emit(
        "INFO",
        "PluginHealth | "
        f"runtime={CAPATCH_PLUGIN_RUNTIME_VERSION} | "
        f"discovered={summary.get('discovered', 0)} | "
        f"active={summary.get('active', 0)} | "
        f"rejected={summary.get('rejected', 0)} | "
        f"disabled={summary.get('disabled', 0)} | "
        f"duplicate_ids={summary.get('duplicate_ids', 0)}",
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
    logs_dir = plugins_dir / CAPATCH_PLUGIN_LOGS_DIR_NAME
    registry_path = plugins_dir / CAPATCH_PLUGIN_REGISTRY_NAME
    disabled_path = plugins_dir / CAPATCH_PLUGIN_DISABLED_NAME

    plugins_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    CAPATCH_PLUGIN_STATE["initialized"] = True
    CAPATCH_PLUGIN_STATE["base_dir"] = base_dir.resolve()
    CAPATCH_PLUGIN_STATE["plugins_dir"] = plugins_dir
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
        f"dir={plugins_dir}",
    )


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
'''.strip("\n")

BUILD_ARG_PARSER_FUNCTION = '''def build_arg_parser() -> argparse.ArgumentParser:
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

    plugin_group = parser.add_argument_group("plugin runtime")
    plugin_group.add_argument(
        "--plugin-list",
        action="store_true",
        help="Lista el registro actual de plugins y sale.",
    )
    plugin_group.add_argument(
        "--plugin-health",
        action="store_true",
        help="Carga plugins, imprime estado/health y sale.",
    )
    plugin_group.add_argument(
        "--plugin-retest",
        action="store_true",
        help="Alias de --plugin-health para revalidar plugins en una corrida limpia.",
    )
    plugin_group.add_argument(
        "--plugin-disable",
        help="Deshabilita un plugin por PLUGIN_ID y sale.",
    )
    plugin_group.add_argument(
        "--plugin-enable",
        help="Habilita un plugin por PLUGIN_ID y sale.",
    )
    plugin_group.add_argument(
        "--plugin-show-log",
        help="Imprime el tail del log de un plugin y sale.",
    )
    plugin_group.add_argument(
        "--plugin-tail-lines",
        type=int,
        default=CAPATCH_PLUGIN_DEFAULT_TAIL_LINES,
        help="Numero de lineas para --plugin-show-log.",
    )
    return parser
'''.strip()

MAIN_FUNCTION = '''def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    initialize_plugin_runtime(Path(__file__).resolve().parent)

    if handle_plugin_cli_actions(args):
        return 0

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
'''.strip()

PLUGIN_TEMPLATE_GUARD = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

PLUGIN_ID = "guard.base.template"
PLUGIN_VERSION = "3.0.0"
PLUGIN_DESCRIPTION = "Template base para un plugin tolerante a fallos."
PLUGIN_MIN_RUNTIME = "3.0.0"


def register(api):
    api.register_guard(guard)
    api.register_before_apply(before_apply)
    api.register_after_apply(after_apply)
    api.register_support_resolver(support_resolver)


def plugin_self_test(api):
    return {"ok": True}


def guard(ctx, operations, preview_content_by_target):
    return {"allow": True}


def before_apply(ctx, operations, preview_content_by_target):
    return None


def after_apply(ctx, operations, results):
    return None


def support_resolver(ctx, target, content, operation, field_name, field_value):
    return None
'''.strip("\n")

PLUGIN_TEMPLATE_DEPENDENCY = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

PLUGIN_ID = "guard.dependency.blocker.template"
PLUGIN_VERSION = "3.0.0"
PLUGIN_DESCRIPTION = "Template para bloquear cambios riesgosos sobre archivos de dependencias."
PLUGIN_MIN_RUNTIME = "3.0.0"

CRITICAL_FILES = {
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "package.json",
    "package-lock.json",
}

BLOCKED_OPERATION_TYPES = {
    "ReplaceExactMany",
    "ReplaceRegexMany",
    "DeleteRegexMany",
}


def register(api):
    api.register_guard(block_on_risky_dependency_change)


def plugin_self_test(api):
    return {"ok": True}


def block_on_risky_dependency_change(ctx, operations, preview_content_by_target):
    risky = []
    for operation in operations:
        spec = getattr(operation, "spec", None)
        op_type = str(getattr(spec, "type", "") or "")
        file_value = str(getattr(spec, "file", "") or "").replace("\\", "/")
        file_name = file_value.split("/")[-1].lower()
        if file_name in CRITICAL_FILES and op_type in BLOCKED_OPERATION_TYPES:
            risky.append(f"{op_type}:{file_value}")

    if risky:
        return {
            "allow": False,
            "reason": (
                "Template bloqueo cambios potencialmente riesgosos sobre dependencias. "
                "Personalizalo para correr validaciones reales antes de permitir la inyeccion."
            ),
            "warning": "Coincidencias: " + ", ".join(risky[:8]),
        }

    return {"allow": True}
'''.strip("\n")

PLUGIN_TEMPLATE_DIFF_BUDGET = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

PLUGIN_ID = "guard.diff.budget.template"
PLUGIN_VERSION = "3.0.0"
PLUGIN_DESCRIPTION = "Template para bloquear previews demasiado grandes o dispersos."
PLUGIN_MIN_RUNTIME = "3.0.0"

MAX_FILES = 6
MAX_TOTAL_CHARS = 12000


def register(api):
    api.register_guard(enforce_diff_budget)


def plugin_self_test(api):
    return {"ok": True}


def enforce_diff_budget(ctx, operations, preview_content_by_target):
    touched_files = len(preview_content_by_target)
    total_chars = sum(len(value) for value in preview_content_by_target.values())

    if touched_files > MAX_FILES:
        return {
            "allow": False,
            "reason": f"El preview toca {touched_files} archivos y el limite del template es {MAX_FILES}.",
        }

    if total_chars > MAX_TOTAL_CHARS:
        return {
            "allow": False,
            "reason": (
                f"El preview suma {total_chars} caracteres y el limite del template es {MAX_TOTAL_CHARS}."
            ),
        }

    return {"allow": True}
'''.strip("\n")


@dataclass(slots=True)
class UpdateResult:
    changed: bool
    backup_path: Path | None
    target_path: Path
    plugin_dir: Path
    created_templates: list[Path]


def log_line(log_path: Path, message: str) -> None:
    timestamp = datetime.now().isoformat(timespec="seconds")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="") as fh:
        fh.write(f"[{timestamp}] {message}\n")


def info(log_path: Path, message: str) -> None:
    print(f"[INFO] {message}")
    log_line(log_path, f"[INFO] {message}")


def ok(log_path: Path, message: str) -> None:
    print(f"[OK] {message}")
    log_line(log_path, f"[OK] {message}")


def fail(log_path: Path, message: str) -> None:
    log_line(log_path, f"[ERROR] {message}")
    raise RuntimeError(message)


def ensure_imports(text: str) -> tuple[str, bool]:
    anchor = "import difflib\n"
    if anchor not in text:
        raise RuntimeError("No encontre el bloque de imports esperado para insertar imports del runtime.")

    insert_chunk = ""
    for line in REQUIRED_IMPORTS:
        if line not in text:
            insert_chunk += f"{line}\n"

    if not insert_chunk:
        return text, False

    return text.replace(anchor, anchor + insert_chunk, 1), True


def upsert_block(text: str, start_marker: str, end_marker: str, anchor: str, block: str) -> tuple[str, bool]:
    if start_marker in text and end_marker in text:
        start = text.index(start_marker)
        end = text.index(end_marker) + len(end_marker)
        existing = text[start:end]
        if existing == block:
            return text, False
        return text[:start] + block + text[end:], True

    payload = block.rstrip() + "\n\n"
    if anchor not in text:
        raise RuntimeError(f"No encontre el ancla para insertar bloque manejado: {anchor!r}")
    return text.replace(anchor, payload + anchor, 1), True


def ensure_one_of_snippets(text: str, alternatives: list[str], replacement: str, label: str) -> tuple[str, bool]:
    if replacement in text:
        return text, False
    for candidate in alternatives:
        if candidate in text:
            return text.replace(candidate, replacement, 1), True
    raise RuntimeError(f"No encontre fragmento esperado para parchear {label}.")


def replace_region(text: str, start_token: str, end_token: str, replacement: str, label: str) -> tuple[str, bool]:
    start = text.find(start_token)
    if start < 0:
        raise RuntimeError(f"No encontre el inicio de {label}: {start_token}")
    end = text.find(end_token, start)
    if end < 0:
        raise RuntimeError(f"No encontre el final de {label}: {end_token}")
    new_text = text[:start] + replacement.rstrip() + "\n\n" + text[end:]
    return (new_text, new_text != text)


def patch_capatch_text(original_text: str) -> tuple[str, bool]:
    text = original_text
    changed_any = False

    text, changed = ensure_imports(text)
    changed_any = changed_any or changed

    text, changed = upsert_block(
        text,
        PLUGIN_RUNTIME_START,
        PLUGIN_RUNTIME_END,
        'def normalize_match_candidate(text: str) -> str:\n',
        PLUGIN_RUNTIME_BLOCK,
    )
    changed_any = changed_any or changed

    old_support_base = '''        resolution = find_support_resolution(content, field_name, field_value)
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
'''
    old_support_plugin = '''        resolution = find_support_resolution(content, field_name, field_value)
        if resolution is None:
            resolution = resolve_support_resolution_with_plugins(
                ctx,
                target,
                content,
                operation,
                field_name,
                field_value,
            )
        if resolution is None:
            continue

        should_apply = field_value not in content
        if not should_apply and resolution.strategy in preferred_partial_strategies:
            should_apply = True
        if not should_apply and resolution.strategy == "trim_bordes" and has_partial_whitespace_overlap(content, field_value):
            should_apply = True
        if not should_apply and resolution.strategy.startswith("plugin:"):
            should_apply = True

        if not should_apply:
            continue

        payload[field_name] = resolution.resolved_value
        notes.append(
            f"{field_name}:{resolution.strategy} ({format_suggestion_preview(field_value)} -> "
            f"{format_suggestion_preview(resolution.resolved_value)})"
        )
'''
    text, changed = ensure_one_of_snippets(text, [old_support_base, old_support_plugin], old_support_plugin, "materialize_support_payload")
    changed_any = changed_any or changed

    old_dry_base = '''    if ctx.dry_run:
        info("Modo dry-run activo: no se escribiran cambios ni se crearan checkpoints.")
        for result in preview_results:
            ok(f"[dry-run] {result}")
            results.append(result)
        return results

    checkpoints = build_session_checkpoints(ctx, ops_list)
'''
    old_dry_plugin = '''    run_plugins_before_apply(ctx, ops_list, preview_content_by_target)

    if ctx.dry_run:
        info("Modo dry-run activo: no se escribiran cambios ni se crearan checkpoints.")
        for result in preview_results:
            ok(f"[dry-run] {result}")
            results.append(result)
        run_plugins_after_apply(ctx, ops_list, results)
        return results

    checkpoints = build_session_checkpoints(ctx, ops_list)
'''
    text, changed = ensure_one_of_snippets(text, [old_dry_base, old_dry_plugin], old_dry_plugin, "apply_operations dry-run")
    changed_any = changed_any or changed

    old_apply_tail_base = '''    except Exception as exc:
        restored = restore_session_checkpoints(checkpoints)
        info(f"Rollback de sesion aplicado sobre {len(restored)} archivo(s).")
        if isinstance(exc, CapatchError):
            raise CapatchError(f"{exc} | Rollback aplicado desde {ctx.checkpoint_dir}") from exc
        raise CapatchError(
            f"Error inesperado durante apply_operations: {exc} | "
            f"Rollback aplicado desde {ctx.checkpoint_dir}"
        ) from exc

    return results
'''
    old_apply_tail_plugin = '''    except Exception as exc:
        restored = restore_session_checkpoints(checkpoints)
        info(f"Rollback de sesion aplicado sobre {len(restored)} archivo(s).")
        if isinstance(exc, CapatchError):
            raise CapatchError(f"{exc} | Rollback aplicado desde {ctx.checkpoint_dir}") from exc
        raise CapatchError(
            f"Error inesperado durante apply_operations: {exc} | "
            f"Rollback aplicado desde {ctx.checkpoint_dir}"
        ) from exc

    run_plugins_after_apply(ctx, ops_list, results)
    return results
'''
    text, changed = ensure_one_of_snippets(text, [old_apply_tail_base, old_apply_tail_plugin], old_apply_tail_plugin, "apply_operations tail")
    changed_any = changed_any or changed

    text, changed = replace_region(
        text,
        "def build_arg_parser() -> argparse.ArgumentParser:\n",
        "\n\ndef print_self_test() -> int:\n",
        BUILD_ARG_PARSER_FUNCTION,
        "build_arg_parser",
    )
    changed_any = changed_any or changed

    text, changed = replace_region(
        text,
        "def main(argv: list[str] | None = None) -> int:\n",
        "\n\nif __name__ == \"__main__\":\n",
        MAIN_FUNCTION,
        "main",
    )
    changed_any = changed_any or changed

    return text, changed_any


def write_template(path_value: Path, content: str, log_path: Path, *, replace: bool) -> Path:
    path_value.parent.mkdir(parents=True, exist_ok=True)
    if path_value.exists() and not replace:
        info(log_path, f"Template existente intacto: {path_value}")
        return path_value
    path_value.write_text(content + "\n", encoding="utf-8", newline="")
    ok(log_path, f"Template actualizado: {path_value}")
    return path_value


def upgrade_capatch(target_path: Path, log_path: Path, refresh_templates: bool) -> UpdateResult:
    if not target_path.exists():
        fail(log_path, f"No encontre el archivo objetivo: {target_path}")
    if not target_path.is_file():
        fail(log_path, f"La ruta objetivo no es archivo: {target_path}")

    original_text = target_path.read_text(encoding="utf-8")
    patched_text, changed = patch_capatch_text(original_text)

    backup_path: Path | None = None
    if changed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = target_path.with_name(f"{target_path.stem}.pre_plugin_upgrade_v3_{timestamp}{target_path.suffix}.bak")
        shutil.copy2(target_path, backup_path)
        info(log_path, f"Respaldo creado: {backup_path}")

        try:
            target_path.write_text(patched_text, encoding="utf-8", newline="")
            py_compile.compile(str(target_path), doraise=True)
            ok(log_path, f"capatch.py actualizado al runtime v3: {target_path}")
        except Exception as exc:
            if backup_path.exists():
                shutil.copy2(backup_path, target_path)
            fail(log_path, f"Fallo validacion/compilacion. Restaure respaldo. Detalle: {exc}")
    else:
        info(log_path, "capatch.py ya estaba al dia para este upgrade. No meti cambios al archivo.")

    plugin_dir = target_path.parent / "capatch_plugins"
    created_templates = [
        write_template(plugin_dir / "plugin_template_guard.py", PLUGIN_TEMPLATE_GUARD, log_path, replace=refresh_templates),
        write_template(plugin_dir / "plugin_template_dependency_guard.py", PLUGIN_TEMPLATE_DEPENDENCY, log_path, replace=refresh_templates),
        write_template(plugin_dir / "plugin_template_diff_budget.py", PLUGIN_TEMPLATE_DIFF_BUDGET, log_path, replace=refresh_templates),
    ]

    return UpdateResult(
        changed=changed,
        backup_path=backup_path,
        target_path=target_path,
        plugin_dir=plugin_dir,
        created_templates=created_templates,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sube capatch.py al runtime v3 de plugins tolerante a fallos.",
    )
    parser.add_argument(
        "--capatch-path",
        default=str(DEFAULT_CAPATCH_PATH),
        help="Ruta al capatch.py objetivo.",
    )
    parser.add_argument(
        "--log-path",
        default=str(DEFAULT_LOG_PATH),
        help="Ruta del log del updater.",
    )
    parser.add_argument(
        "--refresh-templates",
        action="store_true",
        help="Sobrescribe tambien los templates base de plugins.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target_path = Path(args.capatch_path).expanduser().resolve()
    log_path = Path(args.log_path).expanduser().resolve()

    try:
        result = upgrade_capatch(
            target_path=target_path,
            log_path=log_path,
            refresh_templates=bool(args.refresh_templates),
        )
        ok(log_path, f"Target listo: {result.target_path}")
        ok(log_path, f"Plugin dir: {result.plugin_dir}")
        for template_path in result.created_templates:
            ok(log_path, f"Template: {template_path}")
        return 0
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
