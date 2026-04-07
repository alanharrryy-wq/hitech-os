#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""
Instalador idempotente para meter un sistema de plugins tolerante a fallos
dentro de capatch.py, sin pegar cambios manuales.

Hace esto:
- Respalda capatch.py
- Inserta un runtime de plugins dentro del archivo
- Activa autodeteccion de plugins desde la carpeta "capatch_plugins"
- Crea un template de plugin de guardia
- Valida sintaxis y revierte si algo sale mal

Rutas por defecto:
- capatch.py objetivo: F:\\OneDrive\\Descargas\\capatch.py
- logs del instalador: F:\\OneDrive\\Descargas\\capatch_plugin_install.log
- plugins: al lado de capatch.py, carpeta "capatch_plugins"
"""

import argparse
import py_compile
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_CAPATCH_PATH = Path(r"F:\\OneDrive\\Descargas\\capatch.py")
DEFAULT_LOG_PATH = Path(r"F:\\OneDrive\\Descargas\\capatch_plugin_install.log")

PLUGIN_RUNTIME_START = "# === CAPATCH PLUGIN RUNTIME START ==="
PLUGIN_RUNTIME_END = "# === CAPATCH PLUGIN RUNTIME END ==="

REQUIRED_IMPORTS = [
    "import hashlib",
    "import importlib.util",
    "import traceback",
]

PLUGIN_RUNTIME_BLOCK = r'''
# === CAPATCH PLUGIN RUNTIME START ===
CAPATCH_PLUGIN_DIR_NAME = "capatch_plugins"
CAPATCH_PLUGIN_REGISTRY_NAME = "_plugin_registry.json"
CAPATCH_PLUGIN_LOGS_DIR_NAME = "_logs"

CAPATCH_PLUGIN_STATE: dict[str, Any] = {
    "initialized": False,
    "base_dir": None,
    "plugins_dir": None,
    "registry_path": None,
    "logs_dir": None,
    "registry": {},
    "guards": [],
    "before_apply": [],
    "after_apply": [],
    "support_resolvers": [],
    "active_plugins": [],
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
        plugin_append_log("plugin-system", "registry-read", f"No pude leer registro {path_value}", exc)
        return default


def save_json_file_safe(path_value: Path, data: Any) -> None:
    path_value.parent.mkdir(parents=True, exist_ok=True)
    path_value.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8", newline="")


def hash_file_sha256(path_value: Path) -> str:
    digest = hashlib.sha256()
    with path_value.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def update_plugin_registry_entry(
    plugin_id: str,
    plugin_path: Path,
    *,
    status: str,
    plugin_hash: str,
    version: str,
    last_error: str | None = None,
    hook_counts: dict[str, int] | None = None,
) -> None:
    registry = CAPATCH_PLUGIN_STATE["registry"]
    assert isinstance(registry, dict)
    registry[plugin_id] = {
        "path": str(plugin_path),
        "status": status,
        "version": version,
        "hash": plugin_hash,
        "last_loaded_at": datetime.now().isoformat(timespec="seconds"),
        "last_error": last_error,
        "hook_counts": hook_counts or {},
    }


def load_and_activate_plugin(plugin_path: Path) -> None:
    plugin_hash = hash_file_sha256(plugin_path)
    transient_id = plugin_path.stem
    module_name = f"_capatch_plugin_{sanitize_plugin_token(plugin_path.stem)}_{plugin_hash[:12]}"

    try:
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("spec/loader invalido")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        plugin_id = str(getattr(module, "PLUGIN_ID", transient_id)).strip() or transient_id
        plugin_version = str(getattr(module, "PLUGIN_VERSION", "0.0.0")).strip() or "0.0.0"
        api = PluginAPI(plugin_id, plugin_path)

        register_fn = getattr(module, "register", None)
        if callable(register_fn):
            register_fn(api)

        self_test_fn = getattr(module, "plugin_self_test", None)
        if callable(self_test_fn):
            self_test_fn(api)

        commit_plugin_hooks(plugin_id, api)
        CAPATCH_PLUGIN_STATE["active_plugins"].append(
            {
                "plugin_id": plugin_id,
                "version": plugin_version,
                "path": str(plugin_path),
            }
        )
        update_plugin_registry_entry(
            plugin_id,
            plugin_path,
            status="active",
            plugin_hash=plugin_hash,
            version=plugin_version,
            hook_counts={
                "guards": len(api.guards),
                "before_apply": len(api.before_apply),
                "after_apply": len(api.after_apply),
                "support_resolvers": len(api.support_resolvers),
            },
        )
        plugin_emit("INFO", f"Plugin activo: {plugin_id} v{plugin_version}")
    except Exception as exc:
        plugin_id = transient_id
        plugin_append_log(plugin_id, "load", f"Plugin rechazado: {plugin_path}", exc)
        update_plugin_registry_entry(
            plugin_id,
            plugin_path,
            status="rejected",
            plugin_hash=plugin_hash,
            version="0.0.0",
            last_error=f"{type(exc).__name__}: {exc}",
        )
        plugin_emit("WARN", f"Plugin rechazado: {plugin_path.name} ({exc})")


def initialize_plugin_runtime(base_dir: Path) -> None:
    plugins_dir = (base_dir / CAPATCH_PLUGIN_DIR_NAME).resolve()
    logs_dir = plugins_dir / CAPATCH_PLUGIN_LOGS_DIR_NAME
    registry_path = plugins_dir / CAPATCH_PLUGIN_REGISTRY_NAME

    plugins_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    CAPATCH_PLUGIN_STATE["initialized"] = True
    CAPATCH_PLUGIN_STATE["base_dir"] = base_dir.resolve()
    CAPATCH_PLUGIN_STATE["plugins_dir"] = plugins_dir
    CAPATCH_PLUGIN_STATE["registry_path"] = registry_path
    CAPATCH_PLUGIN_STATE["logs_dir"] = logs_dir
    CAPATCH_PLUGIN_STATE["guards"] = []
    CAPATCH_PLUGIN_STATE["before_apply"] = []
    CAPATCH_PLUGIN_STATE["after_apply"] = []
    CAPATCH_PLUGIN_STATE["support_resolvers"] = []
    CAPATCH_PLUGIN_STATE["active_plugins"] = []
    CAPATCH_PLUGIN_STATE["registry"] = load_json_file_safe(registry_path, {})

    for plugin_path in discover_plugin_files(plugins_dir):
        load_and_activate_plugin(plugin_path)

    save_json_file_safe(registry_path, CAPATCH_PLUGIN_STATE["registry"])
    plugin_emit(
        "INFO",
        f"Plugin runtime listo. Activos={len(CAPATCH_PLUGIN_STATE['active_plugins'])} dir={plugins_dir}",
    )


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

PLUGIN_TEMPLATE = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

PLUGIN_ID = "guard.dependency.template"
PLUGIN_VERSION = "1.0.0"


WATCH_TOKENS = [
    "requirements",
    "pyproject",
    "poetry.lock",
    "package.json",
]


def register(api):
    api.register_guard(dependency_guard)
    api.register_before_apply(before_apply)
    api.register_after_apply(after_apply)
    api.register_support_resolver(support_resolver)


def plugin_self_test(api):
    # Si quieres, aqui puedes validar imports propios del plugin.
    return {"ok": True}


def dependency_guard(ctx, operations, preview_content_by_target):
    """
    Plantilla base.

    Idea de uso:
    - revisas las operaciones entrantes
    - detectas si tocan archivos sensibles
    - decides si bloquear o solo advertir
    - si quieres bloquear, regresa:
      {"allow": False, "reason": "motivo"}
    - si solo quieres avisar:
      {"allow": True, "warning": "mensaje"}
    """

    touched = []
    for operation in operations:
        spec = getattr(operation, "spec", None)
        file_value = str(getattr(spec, "file", "") or "").replace("\\", "/").lower()
        if any(token in file_value for token in WATCH_TOKENS):
            touched.append(file_value)

    if touched:
        return {
            "allow": True,
            "warning": (
                "Template detecto archivos sensibles. "
                "Personaliza dependency_guard si quieres bloquear inyecciones "
                "cuando una dependencia pueda romperse."
            ),
        }

    return {"allow": True}


def before_apply(ctx, operations, preview_content_by_target):
    # Hook opcional: corre despues del preview y antes del apply real.
    return None


def after_apply(ctx, operations, results):
    # Hook opcional: corre al final si el apply termino bien.
    return None


def support_resolver(ctx, target, content, operation, field_name, field_value):
    # Hook opcional: puede devolver un string o dict con resolved_value.
    return None
'''.strip("\n")


@dataclass(slots=True)
class InstallResult:
    changed: bool
    backup_path: Path | None
    plugin_dir: Path
    template_path: Path
    target_path: Path


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

    text = text.replace(anchor, anchor + insert_chunk, 1)
    return text, True


def upsert_block(text: str, start_marker: str, end_marker: str, anchor: str, block: str) -> tuple[str, bool]:
    payload = block.rstrip() + "\n\n"
    if start_marker in text and end_marker in text:
        start = text.index(start_marker)
        end = text.index(end_marker) + len(end_marker)
        existing = text[start:end]
        if existing == block:
            return text, False
        text = text[:start] + block + text[end:]
        return text, True

    if anchor not in text:
        raise RuntimeError(f"No encontre el ancla para insertar bloque manejado: {anchor!r}")

    text = text.replace(anchor, payload + anchor, 1)
    return text, True


def ensure_snippet(text: str, old: str, new: str) -> tuple[str, bool]:
    if new in text:
        return text, False
    if old not in text:
        raise RuntimeError("No encontre un fragmento esperado para parchear capatch.py.")
    return text.replace(old, new, 1), True


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

    old_support = '''        resolution = find_support_resolution(content, field_name, field_value)
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
    new_support = '''        resolution = find_support_resolution(content, field_name, field_value)
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
    text, changed = ensure_snippet(text, old_support, new_support)
    changed_any = changed_any or changed

    old_dry_block = '''    if ctx.dry_run:
        info("Modo dry-run activo: no se escribiran cambios ni se crearan checkpoints.")
        for result in preview_results:
            ok(f"[dry-run] {result}")
            results.append(result)
        return results

    checkpoints = build_session_checkpoints(ctx, ops_list)
'''
    new_dry_block = '''    run_plugins_before_apply(ctx, ops_list, preview_content_by_target)

    if ctx.dry_run:
        info("Modo dry-run activo: no se escribiran cambios ni se crearan checkpoints.")
        for result in preview_results:
            ok(f"[dry-run] {result}")
            results.append(result)
        run_plugins_after_apply(ctx, ops_list, results)
        return results

    checkpoints = build_session_checkpoints(ctx, ops_list)
'''
    text, changed = ensure_snippet(text, old_dry_block, new_dry_block)
    changed_any = changed_any or changed

    old_apply_tail = '''    except Exception as exc:
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
    new_apply_tail = '''    except Exception as exc:
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
    text, changed = ensure_snippet(text, old_apply_tail, new_apply_tail)
    changed_any = changed_any or changed

    old_main_early = '''    if args.self_test:
        return print_self_test()
    if args.smoke_test:
        return run_smoke_tests()

    if not args.ops_file and not args.ops_stdin:
'''
    new_main_early = '''    initialize_plugin_runtime(Path(__file__).resolve().parent)

    if args.self_test:
        return print_self_test()
    if args.smoke_test:
        return run_smoke_tests()

    if not args.ops_file and not args.ops_stdin:
'''
    text, changed = ensure_snippet(text, old_main_early, new_main_early)
    changed_any = changed_any or changed

    old_main_late = '''    try:
        initialize_plugin_runtime(Path(__file__).resolve().parent)
        operations = (
'''
    new_main_late = '''    try:
        operations = (
'''
    text, changed = ensure_snippet(text, old_main_late, new_main_late)
    changed_any = changed_any or changed

    return text, changed_any


def write_template(plugin_dir: Path, log_path: Path) -> Path:
    plugin_dir.mkdir(parents=True, exist_ok=True)
    template_path = plugin_dir / "plugin_template_guard.py"
    if not template_path.exists():
        template_path.write_text(PLUGIN_TEMPLATE + "\n", encoding="utf-8", newline="")
        ok(log_path, f"Template de plugin creado: {template_path}")
    else:
        info(log_path, f"Template ya existe, lo deje intacto: {template_path}")
    return template_path


def install(target_path: Path, log_path: Path) -> InstallResult:
    if not target_path.exists():
        fail(log_path, f"No encontre el archivo objetivo: {target_path}")
    if not target_path.is_file():
        fail(log_path, f"La ruta objetivo no es archivo: {target_path}")

    original_text = target_path.read_text(encoding="utf-8")
    patched_text, changed = patch_capatch_text(original_text)

    backup_path: Path | None = None
    if changed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = target_path.with_name(f"{target_path.stem}.pre_plugins_{timestamp}{target_path.suffix}.bak")
        shutil.copy2(target_path, backup_path)
        info(log_path, f"Respaldo creado: {backup_path}")

        try:
            target_path.write_text(patched_text, encoding="utf-8", newline="")
            py_compile.compile(str(target_path), doraise=True)
            ok(log_path, f"capatch.py actualizado con runtime de plugins: {target_path}")
        except Exception as exc:
            if backup_path.exists():
                shutil.copy2(backup_path, target_path)
            fail(log_path, f"Fallo validacion/compilacion. Restaure respaldo. Detalle: {exc}")
    else:
        info(log_path, "capatch.py ya tenia el runtime instalado. No meti cambios al archivo.")

    plugin_dir = target_path.parent / "capatch_plugins"
    template_path = write_template(plugin_dir, log_path)

    return InstallResult(
        changed=changed,
        backup_path=backup_path,
        plugin_dir=plugin_dir,
        template_path=template_path,
        target_path=target_path,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Instala el sistema de plugins dentro de capatch.py",
    )
    parser.add_argument(
        "--target",
        default=str(DEFAULT_CAPATCH_PATH),
        help="Ruta absoluta a capatch.py",
    )
    parser.add_argument(
        "--log-file",
        default=str(DEFAULT_LOG_PATH),
        help="Ruta absoluta del log del instalador",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target_path = Path(args.target).expanduser().resolve()
    log_path = Path(args.log_file).expanduser().resolve()

    try:
        result = install(target_path, log_path)
        ok(log_path, f"Plugins listos en: {result.plugin_dir}")
        ok(log_path, f"Template base: {result.template_path}")
        ok(log_path, "Instalacion terminada.")
        return 0
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
