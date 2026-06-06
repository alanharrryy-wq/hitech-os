from __future__ import annotations

"""Loader de plugins para el runtime diagnóstico.

Mantiene el layout plano `capatch_plugins/active/*` y registra callbacks por fase.
No depende del interior de otros dominios.
"""

import ast
import hashlib
import importlib.util
import json
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from ._contracts import (
    LEGACY_PLUGIN_KIND_ALIASES,
    PLUGIN_KIND_PHASE_HINTS,
    PLUGIN_KINDS,
)
from capatch_contracts.plugin_runtime import (
    CAPATCH_PLUGIN_RUNTIME_VERSION,
    ESSENTIAL_PLUGIN_IDS,
    infer_plugin_capabilities,
    summarize_essential_runtime_health,
)

try:  # pragma: no cover
    from capatch_contracts.constants import (  # type: ignore
        PLUGIN_ACTIVE_DIR_NAME,
        PLUGIN_ARCHIVE_DIR_NAME,
        PLUGIN_DISABLED_DIR_NAME,
        PLUGIN_DISABLED_NAME,
        PLUGIN_DIR_NAME,
        PLUGIN_LOGS_DIR_NAME,
        PLUGIN_REGISTRY_NAME,
        PLUGIN_TEMPLATES_DIR_NAME,
        PLUGIN_QUARANTINE_DIR_NAME,
        PLUGIN_DEFAULT_TAIL_LINES,
    )
except Exception:  # pragma: no cover
    PLUGIN_DIR_NAME = "capatch_plugins"
    PLUGIN_ACTIVE_DIR_NAME = "active"
    PLUGIN_TEMPLATES_DIR_NAME = "templates"
    PLUGIN_DISABLED_DIR_NAME = "disabled"
    PLUGIN_QUARANTINE_DIR_NAME = "quarantine"
    PLUGIN_ARCHIVE_DIR_NAME = "archive"
    PLUGIN_REGISTRY_NAME = "_plugin_registry.json"
    PLUGIN_DISABLED_NAME = "_plugin_disabled.json"
    PLUGIN_LOGS_DIR_NAME = "_logs"
    PLUGIN_DEFAULT_TAIL_LINES = 80

PLUGIN_RUNTIME_VERSION = CAPATCH_PLUGIN_RUNTIME_VERSION

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

FILENAME_KIND_ALIASES = {
    "guard": "guard",
    "collector": "collector",
    "analyzer": "analyzer",
    "recommender": "recommender",
    "fixer": "fixer",
    "verifier": "verifier",
    "exporter": "exporter",
    "executor": "fixer",
    "context": "context-enricher",
    "detector": "target-detector",
    "target": "target-detector",
}

PHASE_BUCKET_TO_PHASE = {
    "guards": "resolve-target",
    "before_apply": "fix",
    "after_apply": "verify",
    "support_resolvers": "export",
    "target_detectors": "resolve-target",
    "collectors": "collect",
    "context_enrichers": "enrich",
    "analyzers": "analyze",
    "recommenders": "recommend",
    "fixers": "fix",
    "verifiers": "verify",
    "exporters": "export",
}


@dataclass(slots=True)
class PluginManifest:
    plugin_id: str
    version: str
    description: str
    min_runtime: str
    plugin_kind: str
    plugin_phase: str
    plugin_outputs: list[str] = field(default_factory=list)
    file_name: str = ""
    path: str = ""
    hash: str = ""
    compat_notes: list[str] = field(default_factory=list)


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
        "capability_map": {},
        "runtime_status": {},
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
    parts = [part for part in "".join(char if char.isdigit() or char == "." else " " for char in str(value)).split()[:1]]
    raw = parts[0].split(".") if parts else []
    ints = [int(part) for part in raw[:3] if part.isdigit()]
    while len(ints) < 3:
        ints.append(0)
    return ints[0], ints[1], ints[2]


def plugin_runtime_satisfies(min_runtime: str | None) -> bool:
    if not min_runtime:
        return True
    return plugin_semver_tuple(PLUGIN_RUNTIME_VERSION) >= plugin_semver_tuple(min_runtime)


def _extract_literal_assignments(text: str) -> dict[str, Any]:
    values: dict[str, Any] = {}
    try:
        tree = ast.parse(text)
    except Exception:
        return values
    for node in tree.body:
        target_name = None
        value_node = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id
            value_node = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target_name = node.target.id
            value_node = node.value
        if not target_name or value_node is None:
            continue
        if target_name not in {
            "PLUGIN_ID",
            "PLUGIN_VERSION",
            "PLUGIN_DESCRIPTION",
            "PLUGIN_MIN_RUNTIME",
            "PLUGIN_KIND",
            "PLUGIN_PHASE",
            "PLUGIN_OUTPUTS",
        }:
            continue
        try:
            values[target_name] = ast.literal_eval(value_node)
        except Exception:
            continue
    return values


def _normalize_kind(value: Any) -> str:
    text = str(value or "").strip().lower().replace("_", "-")
    text = LEGACY_PLUGIN_KIND_ALIASES.get(text.replace("-", "_"), text)
    return text if text in PLUGIN_KINDS else ""


def _guess_kind_from_filename(plugin_path: Path) -> str:
    prefix = plugin_path.stem.split("_", 1)[0].strip().lower()
    alias = FILENAME_KIND_ALIASES.get(prefix, prefix)
    return _normalize_kind(alias)


def _normalize_phase(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text if text in PHASE_BUCKET_TO_PHASE.values() else ""


def _phase_for_kind(kind: str) -> str:
    return PLUGIN_KIND_PHASE_HINTS.get(kind, "collect")


def _guess_phase_from_hooks(hook_counts: dict[str, int], kind: str) -> str:
    for bucket_name, count in hook_counts.items():
        if int(count or 0) > 0:
            return PHASE_BUCKET_TO_PHASE.get(bucket_name, _phase_for_kind(kind))
    return _phase_for_kind(kind)


def discover_plugin_manifest(plugin_path: Path) -> PluginManifest:
    text = plugin_path.read_text(encoding="utf-8", errors="replace")
    values = _extract_literal_assignments(text)
    compat_notes: list[str] = []
    plugin_id = str(values.get("PLUGIN_ID") or plugin_path.stem).strip() or plugin_path.stem
    plugin_kind = _normalize_kind(values.get("PLUGIN_KIND"))
    if not plugin_kind:
        plugin_kind = _guess_kind_from_filename(plugin_path) or "collector"
        compat_notes.append("plugin_kind inferido por compatibilidad")
    plugin_phase = _normalize_phase(values.get("PLUGIN_PHASE"))
    if not plugin_phase:
        plugin_phase = _phase_for_kind(plugin_kind)
        compat_notes.append("plugin_phase inferido por compatibilidad")
    outputs = values.get("PLUGIN_OUTPUTS") if isinstance(values.get("PLUGIN_OUTPUTS"), list) else []
    return PluginManifest(
        plugin_id=plugin_id,
        version=str(values.get("PLUGIN_VERSION") or "0.0.0").strip() or "0.0.0",
        description=str(values.get("PLUGIN_DESCRIPTION") or "").strip(),
        min_runtime=str(values.get("PLUGIN_MIN_RUNTIME") or "").strip(),
        plugin_kind=plugin_kind,
        plugin_phase=plugin_phase,
        plugin_outputs=[str(item) for item in outputs if str(item).strip()],
        file_name=plugin_path.name,
        path=str(plugin_path),
        hash=hash_file_sha256(plugin_path),
        compat_notes=compat_notes,
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


def _hook_counts(api: PluginAPI) -> dict[str, int]:
    return {key: len(getattr(api, key, [])) for key in PHASE_BUCKETS}


def _active_plugin_ids(state: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for item in state.get("active_plugins", []):
        if isinstance(item, dict) and item.get("plugin_id"):
            ids.append(str(item.get("plugin_id")))
    return ids


def update_plugin_registry_entry(
    state: dict[str, Any],
    manifest: PluginManifest,
    *,
    status: str,
    last_error: str | None = None,
    hook_counts: dict[str, int] | None = None,
    self_test_status: str | None = None,
    load_ms: int | None = None,
    final_kind: str | None = None,
    final_phase: str | None = None,
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
        "real_status": status,
        "version": manifest.version,
        "description": manifest.description,
        "min_runtime": manifest.min_runtime,
        "plugin_kind": final_kind or manifest.plugin_kind,
        "plugin_phase": final_phase or manifest.plugin_phase,
        "plugin_outputs": manifest.plugin_outputs,
        "hash": manifest.hash,
        "runtime_version": PLUGIN_RUNTIME_VERSION,
        "last_loaded_at": datetime.now().isoformat(timespec="seconds"),
        "last_error": last_error,
        "hook_counts": hook_counts or {},
        "self_test_status": self_test_status,
        "rejected_count": rejected_count,
        "load_ms": load_ms,
        "compat_notes": list(manifest.compat_notes),
    }


def _commit_plugin_hooks(state: dict[str, Any], plugin_id: str, api: PluginAPI) -> None:
    for key in PHASE_BUCKETS:
        for func in getattr(api, key, []):
            state[key].append({"plugin_id": plugin_id, "func": func})


def _infer_kind_from_hooks(hook_counts: dict[str, int], fallback_kind: str) -> str:
    best_kind = fallback_kind
    best_count = -1
    for bucket_name, kind in PHASE_BUCKETS.items():
        count = int(hook_counts.get(bucket_name, 0) or 0)
        if count > best_count and count > 0:
            best_kind = kind
            best_count = count
    return _normalize_kind(best_kind) or fallback_kind or "collector"


def load_and_activate_plugin(state: dict[str, Any], plugin_path: Path, manifest: PluginManifest | None = None) -> None:
    started = time.perf_counter()
    manifest = manifest or discover_plugin_manifest(plugin_path)
    state["load_summary"]["discovered"] += 1
    disabled_ids = state.get("disabled_ids", set())
    if manifest.plugin_id in disabled_ids:
        state["load_summary"]["disabled"] += 1
        update_plugin_registry_entry(state, manifest, status="disabled")
        return
    seen_ids = set(_active_plugin_ids(state))
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
        hook_counts = _hook_counts(api)
        final_kind = _infer_kind_from_hooks(hook_counts, manifest.plugin_kind)
        final_phase = _guess_phase_from_hooks(hook_counts, final_kind)
        _commit_plugin_hooks(state, manifest.plugin_id, api)
        state["active_plugins"].append(
            {
                "plugin_id": manifest.plugin_id,
                "version": manifest.version,
                "path": manifest.path,
                "plugin_kind": final_kind,
                "plugin_phase": final_phase,
            }
        )
        state["manifests"][manifest.plugin_id] = {
            **asdict(manifest),
            "plugin_kind": final_kind,
            "plugin_phase": final_phase,
        }
        state["load_summary"]["active"] += 1
        update_plugin_registry_entry(
            state,
            manifest,
            status="active",
            hook_counts=hook_counts,
            self_test_status=self_test_status,
            load_ms=int((time.perf_counter() - started) * 1000),
            final_kind=final_kind,
            final_phase=final_phase,
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


def _registry_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    registry = state.get("registry")
    if not isinstance(registry, dict):
        return []
    rows: list[dict[str, Any]] = []
    for plugin_id in sorted(registry):
        payload = registry.get(plugin_id)
        if isinstance(payload, dict):
            item = dict(payload)
            item["plugin_id"] = plugin_id
            rows.append(item)
    return rows


def build_capability_map(state: dict[str, Any]) -> dict[str, Any]:
    rows = _registry_rows(state)
    by_phase: dict[str, list[str]] = {phase: [] for phase in PHASE_BUCKET_TO_PHASE.values()}
    by_kind: dict[str, list[str]] = {kind: [] for kind in PLUGIN_KINDS}
    hook_totals: dict[str, int] = {key: 0 for key in PHASE_BUCKETS}
    rejected: list[str] = []
    disabled: list[str] = []
    duplicate: list[str] = []
    declared_capabilities_by_plugin: dict[str, list[str]] = {}
    all_capabilities: list[str] = []
    for row in rows:
        plugin_id = str(row.get("plugin_id") or "")
        plugin_kind = str(row.get("plugin_kind") or "")
        plugin_phase = str(row.get("plugin_phase") or "")
        status = str(row.get("real_status") or row.get("status") or "unknown")
        declared_capabilities = infer_plugin_capabilities(plugin_id, row)
        declared_capabilities_by_plugin[plugin_id] = list(declared_capabilities)
        all_capabilities.extend(declared_capabilities)
        if status == "active":
            if plugin_phase in by_phase and plugin_id not in by_phase[plugin_phase]:
                by_phase[plugin_phase].append(plugin_id)
            if plugin_kind in by_kind and plugin_id not in by_kind[plugin_kind]:
                by_kind[plugin_kind].append(plugin_id)
        elif status == "rejected":
            rejected.append(plugin_id)
        elif status == "disabled":
            disabled.append(plugin_id)
        elif status == "duplicate":
            duplicate.append(plugin_id)
        hook_counts = row.get("hook_counts") if isinstance(row.get("hook_counts"), dict) else {}
        for key in hook_totals:
            hook_totals[key] += int(hook_counts.get(key, 0) or 0)
    active_plugin_ids = _active_plugin_ids(state)
    return {
        "runtime_version": state.get("runtime_version", PLUGIN_RUNTIME_VERSION),
        "active_plugin_ids": active_plugin_ids,
        "phase_coverage": by_phase,
        "kind_coverage": by_kind,
        "hook_totals": hook_totals,
        "load_summary": dict(state.get("load_summary") or {}),
        "disabled_plugin_ids": sorted(disabled),
        "rejected_plugin_ids": sorted(rejected),
        "duplicate_plugin_ids": sorted(duplicate),
        "declared_capabilities_by_plugin": declared_capabilities_by_plugin,
        "all_declared_capabilities": sorted({item for item in all_capabilities if item}),
        "supports_fix_pipeline": bool(by_phase.get("fix")),
        "supports_verify_pipeline": bool(by_phase.get("verify")),
        "supports_export_pipeline": bool(by_phase.get("export")),
    }


def summarize_runtime_status(state: dict[str, Any]) -> dict[str, Any]:
    capability_map = build_capability_map(state)
    summary = capability_map.get("load_summary") if isinstance(capability_map.get("load_summary"), dict) else {}
    rejected = capability_map.get("rejected_plugin_ids") if isinstance(capability_map.get("rejected_plugin_ids"), list) else []
    duplicates = capability_map.get("duplicate_plugin_ids") if isinstance(capability_map.get("duplicate_plugin_ids"), list) else []
    essential = summarize_essential_runtime_health(
        runtime_version=str(capability_map.get("runtime_version") or PLUGIN_RUNTIME_VERSION),
        registry=state.get("registry") if isinstance(state.get("registry"), dict) else {},
        essential_plugin_ids=ESSENTIAL_PLUGIN_IDS,
        capability_map=capability_map,
    )
    status = "healthy"
    if essential.get("status") in {"failed", "blocked"}:
        status = "failed"
    elif essential.get("status") != "healthy" or rejected:
        status = "degraded"
    elif duplicates:
        status = "caution"
    return {
        "status": status,
        "runtime_version": capability_map.get("runtime_version"),
        "active_plugins": len(capability_map.get("active_plugin_ids", [])),
        "rejected_plugins": len(rejected),
        "disabled_plugins": len(capability_map.get("disabled_plugin_ids", [])),
        "duplicate_plugins": len(duplicates),
        "essential_plugins": essential,
        "all_declared_capabilities": list(capability_map.get("all_declared_capabilities") or []),
        "load_summary": summary,
    }


def normalize_plugin_state(state: dict[str, Any] | None, base_dir: Path | None = None) -> dict[str, Any]:
    if state is None:
        normalized = empty_plugin_state()
    else:
        normalized = state
        for key, value in empty_plugin_state().items():
            normalized.setdefault(key, value)
        for bucket_name in PHASE_BUCKETS:
            if not isinstance(normalized.get(bucket_name), list):
                normalized[bucket_name] = []
        if not isinstance(normalized.get("active_plugins"), list):
            normalized["active_plugins"] = []
        if not isinstance(normalized.get("manifests"), dict):
            normalized["manifests"] = {}
        if not isinstance(normalized.get("registry"), dict):
            normalized["registry"] = {}
        if not isinstance(normalized.get("load_summary"), dict):
            normalized["load_summary"] = dict(empty_plugin_state()["load_summary"])
        disabled_ids = normalized.get("disabled_ids")
        if isinstance(disabled_ids, list):
            normalized["disabled_ids"] = set(str(item) for item in disabled_ids if str(item).strip())
        elif not isinstance(disabled_ids, set):
            normalized["disabled_ids"] = set()
    if base_dir is not None and normalized.get("base_dir") is None:
        normalized["base_dir"] = Path(base_dir).resolve()
    normalized["runtime_version"] = normalized.get("runtime_version") or PLUGIN_RUNTIME_VERSION
    normalized["capability_map"] = build_capability_map(normalized)
    normalized["runtime_status"] = summarize_runtime_status(normalized)
    return normalized


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
    normalize_plugin_state(state, base_dir=base_dir)
    save_json_file_safe(registry_path, state["registry"])
    save_json_file_safe(disabled_path, {"disabled_plugin_ids": sorted(state["disabled_ids"])})
    return state
