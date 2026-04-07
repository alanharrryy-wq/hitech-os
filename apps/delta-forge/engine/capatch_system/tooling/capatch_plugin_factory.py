#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Fabrica local de plugins para capatch workspace."""

import argparse
import ast
import json
import py_compile
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CAPATCH_PATH = WORKSPACE_DIR / "capatch.py"
DEFAULT_PLUGINS_DIR = WORKSPACE_DIR / "capatch_plugins" / "active"
DEFAULT_TEMPLATES_DIR = WORKSPACE_DIR / "capatch_plugins" / "templates"
DEFAULT_LOG_PATH = WORKSPACE_DIR / "reports" / "capatch_plugin_factory.log"
MIN_RUNTIME = "4.0.0"

KIND_ALIASES = {
    "base": "base-guard",
    "guard": "base-guard",
    "base-guard": "base-guard",
    "dependency": "dependency-guard",
    "dependency-guard": "dependency-guard",
    "deps": "dependency-guard",
    "diff": "diff-budget",
    "diff-budget": "diff-budget",
    "support": "support-resolver",
    "support-resolver": "support-resolver",
}

DEPENDENCY_FILES = [
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
]
DEPENDENCY_OP_TYPES = ["ReplaceExactMany", "ReplaceRegexMany", "DeleteRegexMany"]


@dataclass(slots=True)
class FactoryConfig:
    capatch_path: Path
    plugins_dir: Path
    templates_dir: Path
    log_path: Path
    plugin_id: str
    description: str
    goal: str
    kind: str
    file_name: str
    overwrite: bool
    dry_run: bool
    run_health_check: bool


@dataclass(slots=True)
class ExistingPlugin:
    path: Path
    plugin_id: str


class FactoryError(Exception):
    pass


class PluginIdVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def visit_Assign(self, node: ast.Assign) -> None:
        if len(node.targets) != 1:
            return
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            return
        if target.id not in {"PLUGIN_ID", "PLUGIN_VERSION", "PLUGIN_DESCRIPTION", "PLUGIN_MIN_RUNTIME"}:
            return
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            self.values[target.id] = node.value.value


def now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_line(log_path: Path, message: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="") as fh:
        fh.write(f"[{now_stamp()}] {message}\n")


def emit(message: str) -> None:
    print(message)


def fail(message: str) -> None:
    raise FactoryError(message)


def sanitize_token(value: str, *, dots: bool = False) -> str:
    allowed = {"-", "_"}
    if dots:
        allowed.add(".")
    safe = "".join(ch if ch.isalnum() or ch in allowed else "_" for ch in str(value).strip().lower())
    safe = re.sub(r"_+", "_", safe)
    safe = re.sub(r"-+", "-", safe)
    safe = re.sub(r"\.+", ".", safe)
    return safe.strip("._-") or "plugin"


def slug_from_text(value: str) -> str:
    return sanitize_token(value, dots=False).replace("_", "-") or "plugin"


def normalize_kind(value: str) -> str:
    key = str(value or "").strip().lower()
    if key in KIND_ALIASES:
        return KIND_ALIASES[key]
    supported = ", ".join(sorted(set(KIND_ALIASES.values())))
    fail(f"kind invalido: {value}. Soportados: {supported}")


def infer_kind_from_goal(goal: str) -> str:
    text = str(goal or "").lower()
    if any(token in text for token in ["dependen", "requirements", "pyproject", "package.json", "lock"]):
        return "dependency-guard"
    if any(token in text for token in ["diff", "presupuesto", "budget", "preview", "muchos archivos", "demasiado grande"]):
        return "diff-budget"
    if any(token in text for token in ["resolver", "whitespace", "anchor", "ancla", "support", "auto-support"]):
        return "support-resolver"
    return "base-guard"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera plugins compatibles con capatch runtime v4.")
    parser.add_argument("--capatch-path", default=str(DEFAULT_CAPATCH_PATH))
    parser.add_argument("--plugins-dir", default=str(DEFAULT_PLUGINS_DIR))
    parser.add_argument("--templates-dir", default=str(DEFAULT_TEMPLATES_DIR))
    parser.add_argument("--log-path", default=str(DEFAULT_LOG_PATH))
    parser.add_argument("--plugin-id")
    parser.add_argument("--description")
    parser.add_argument("--goal")
    parser.add_argument("--kind", choices=sorted(set(KIND_ALIASES.keys()) | set(KIND_ALIASES.values())))
    parser.add_argument("--file-name")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--run-health-check", action="store_true")
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--list-kinds", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def list_kinds() -> int:
    emit("Templates disponibles:")
    emit("- base-guard")
    emit("- dependency-guard")
    emit("- diff-budget")
    emit("- support-resolver")
    return 0


def maybe_prompt(value: str | None, prompt: str, default: str = "") -> str:
    if value:
        return value
    suffix = f" [{default}]" if default else ""
    raw = input(f"{prompt}{suffix}: ").strip()
    return raw or default


def read_text_safe(path_value: Path) -> str:
    return path_value.read_text(encoding="utf-8", errors="replace")


def ensure_capatch_runtime_v4(capatch_path: Path) -> None:
    if not capatch_path.exists():
        fail(f"No encontre capatch.py en: {capatch_path}")
    text = read_text_safe(capatch_path)
    if 'CAPATCH_PLUGIN_RUNTIME_VERSION = "4.0.0"' not in text:
        fail("El capatch.py actual no parece tener runtime v4 de workspace.")


def iter_plugin_files(plugins_dir: Path, templates_dir: Path) -> Iterable[Path]:
    for base in [plugins_dir, templates_dir]:
        if not base.exists():
            continue
        for path_value in sorted(base.glob("*.py")):
            if path_value.name.startswith("_"):
                continue
            yield path_value


def read_existing_plugins(plugins_dir: Path, templates_dir: Path) -> list[ExistingPlugin]:
    found: list[ExistingPlugin] = []
    for path_value in iter_plugin_files(plugins_dir, templates_dir):
        try:
            tree = ast.parse(read_text_safe(path_value))
            visitor = PluginIdVisitor()
            visitor.visit(tree)
            plugin_id = visitor.values.get("PLUGIN_ID", path_value.stem)
        except Exception:
            plugin_id = path_value.stem
        found.append(ExistingPlugin(path=path_value.resolve(), plugin_id=plugin_id))
    return found


def ensure_unique_plugin_id(plugin_id: str, existing: Iterable[ExistingPlugin], target_path: Path, overwrite: bool) -> None:
    for item in existing:
        same_id = item.plugin_id == plugin_id
        same_path = item.path.resolve() == target_path.resolve()
        if same_id and not (same_path and overwrite):
            fail(f"Ya existe un plugin con PLUGIN_ID={plugin_id}: {item.path}")


def py_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def build_doc_header(goal: str) -> list[str]:
    goal = goal.strip() or "Plugin generado por capatch_plugin_factory."
    return [
        '"""',
        'Objetivo del plugin:',
        goal,
        '',
        'Notas:',
        '- Compatible con capatch runtime v4.',
        '- El plugin debe fallar con gracia.',
        '- Ajusta plugin_self_test() para validar tu regla real.',
        '"""',
    ]


def todo_comment(goal: str) -> str:
    return "TODO principal: " + ((goal.strip() or "Define aqui la regla especifica del plugin.").replace("\n", " "))


def header_lines(config: FactoryConfig) -> list[str]:
    return [
        "#!/usr/bin/env python3",
        "# -*- coding: utf-8 -*-",
        "from __future__ import annotations",
        "",
        *build_doc_header(config.goal),
        "",
        f"PLUGIN_ID = {py_string(config.plugin_id)}",
        f"PLUGIN_VERSION = {py_string(MIN_RUNTIME)}",
        f"PLUGIN_DESCRIPTION = {py_string(config.description)}",
        f"PLUGIN_MIN_RUNTIME = {py_string(MIN_RUNTIME)}",
        "",
    ]


def render_base_guard(config: FactoryConfig) -> str:
    lines = header_lines(config)
    lines += [
        "def register(api):",
        "    api.register_guard(guard)",
        "    api.register_before_apply(before_apply)",
        "    api.register_after_apply(after_apply)",
        "    api.register_support_resolver(support_resolver)",
        "",
        "def plugin_self_test(api):",
        f"    return {{\"ok\": True, \"message\": {py_string(todo_comment(config.goal))}}}",
        "",
        "def guard(ctx, operations, preview_content_by_target):",
        "    return {\"allow\": True}",
        "",
        "def before_apply(ctx, operations, preview_content_by_target):",
        "    return None",
        "",
        "def after_apply(ctx, operations, results):",
        "    return None",
        "",
        "def support_resolver(ctx, target, content, operation, field_name, field_value):",
        "    return None",
        "",
    ]
    return "\n".join(lines)


def render_dependency_guard(config: FactoryConfig) -> str:
    lines = header_lines(config)
    lines += [
        f"CRITICAL_FILES = {json.dumps(DEPENDENCY_FILES, ensure_ascii=False, indent=4)}",
        f"BLOCKED_OPERATION_TYPES = {json.dumps(DEPENDENCY_OP_TYPES, ensure_ascii=False, indent=4)}",
        "",
        "def register(api):",
        "    api.register_guard(block_on_risky_dependency_change)",
        "",
        "def plugin_self_test(api):",
        "    return {\"ok\": True}",
        "",
        "def block_on_risky_dependency_change(ctx, operations, preview_content_by_target):",
        "    risky = []",
        "    critical = {str(item).lower() for item in CRITICAL_FILES}",
        "    for operation in operations:",
        "        spec = getattr(operation, \"spec\", None)",
        "        op_type = str(getattr(spec, \"type\", \"\") or \"\")",
        "        file_value = str(getattr(spec, \"file\", \"\") or \"\").replace('\\\\', '/')",
        "        file_name = file_value.split('/')[-1].lower()",
        "        if file_name in critical and op_type in BLOCKED_OPERATION_TYPES:",
        "            risky.append(f\"{op_type}:{file_value}\")",
        "    if risky:",
        "        return {",
        "            \"allow\": False,",
        f"            \"reason\": {py_string(config.goal or 'Template bloqueo cambios potencialmente riesgosos sobre dependencias.')},",
        "            \"warning\": \"Coincidencias: \" + \", \".join(risky[:8]),",
        "        }",
        "    return {\"allow\": True}",
        "",
    ]
    return "\n".join(lines)


def render_diff_budget(config: FactoryConfig) -> str:
    lines = header_lines(config)
    lines += [
        "MAX_FILES = 6",
        "MAX_TOTAL_CHARS = 12000",
        "",
        "def register(api):",
        "    api.register_guard(enforce_diff_budget)",
        "",
        "def plugin_self_test(api):",
        "    return {\"ok\": True}",
        "",
        "def enforce_diff_budget(ctx, operations, preview_content_by_target):",
        "    touched_files = len(preview_content_by_target)",
        "    total_chars = sum(len(value) for value in preview_content_by_target.values())",
        "    if touched_files > MAX_FILES:",
        "        return {\"allow\": False, \"reason\": f\"El preview toca {touched_files} archivos y el limite es {MAX_FILES}.\"}",
        "    if total_chars > MAX_TOTAL_CHARS:",
        "        return {\"allow\": False, \"reason\": f\"El preview suma {total_chars} chars y el limite es {MAX_TOTAL_CHARS}.\"}",
        "    return {\"allow\": True}",
        "",
    ]
    return "\n".join(lines)


def render_support_resolver(config: FactoryConfig) -> str:
    lines = header_lines(config)
    lines += [
        "def register(api):",
        "    api.register_support_resolver(resolve_field)",
        "",
        "def plugin_self_test(api):",
        "    return {\"ok\": True}",
        "",
        "def resolve_field(ctx, target, content, operation, field_name, field_value):",
        "    return None",
        "",
    ]
    return "\n".join(lines)


RENDERERS = {
    "base-guard": render_base_guard,
    "dependency-guard": render_dependency_guard,
    "diff-budget": render_diff_budget,
    "support-resolver": render_support_resolver,
}


def derive_default_plugin_id(goal: str, kind: str) -> str:
    slug = slug_from_text(goal) if goal else kind.replace("-", ".")
    prefix = {
        "base-guard": "guard",
        "dependency-guard": "guard.dependency",
        "diff-budget": "guard.diff",
        "support-resolver": "resolver.support",
    }[kind]
    return sanitize_token(f"{prefix}.{slug}", dots=True)


def derive_default_file_name(plugin_id: str) -> str:
    return sanitize_token(plugin_id, dots=False).replace(".", "_") + ".py"


def build_config(args: argparse.Namespace) -> FactoryConfig:
    capatch_path = Path(args.capatch_path).expanduser().resolve()
    plugins_dir = Path(args.plugins_dir).expanduser().resolve()
    templates_dir = Path(args.templates_dir).expanduser().resolve()
    log_path = Path(args.log_path).expanduser().resolve()
    ensure_capatch_runtime_v4(capatch_path)
    plugins_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    kind = normalize_kind(args.kind or infer_kind_from_goal(args.goal or ""))
    plugin_id_default = derive_default_plugin_id(args.goal or "", kind)
    plugin_id = sanitize_token(
        maybe_prompt(args.plugin_id, "PLUGIN_ID", plugin_id_default) if args.interactive else (args.plugin_id or plugin_id_default),
        dots=True,
    )
    description_default = args.description or f"Plugin {kind} generado para capatch workspace."
    description = maybe_prompt(args.description, "Descripcion corta", description_default) if args.interactive else description_default
    goal = maybe_prompt(args.goal, "Objetivo del plugin", "bloquear cambios riesgosos") if args.interactive else (args.goal or "bloquear cambios riesgosos")
    file_name_default = derive_default_file_name(plugin_id)
    file_name = maybe_prompt(args.file_name, "Nombre del archivo .py", file_name_default) if args.interactive else (args.file_name or file_name_default)
    file_name = sanitize_token(file_name.removesuffix(".py"), dots=False) + ".py"
    return FactoryConfig(capatch_path, plugins_dir, templates_dir, log_path, plugin_id, description, goal, kind, file_name, bool(args.overwrite), bool(args.dry_run), bool(args.run_health_check))


def write_plugin(config: FactoryConfig) -> Path:
    target_path = config.plugins_dir / config.file_name
    existing = read_existing_plugins(config.plugins_dir, config.templates_dir)
    ensure_unique_plugin_id(config.plugin_id, existing, target_path, config.overwrite)
    if target_path.exists() and not config.overwrite:
        fail(f"El archivo ya existe: {target_path}. Usa --overwrite si quieres reemplazarlo.")
    text = RENDERERS[config.kind](config).rstrip() + "\n"
    if config.dry_run:
        emit(f"[dry-run] Plugin se generaria en: {target_path}")
        return target_path
    target_path.write_text(text, encoding="utf-8", newline="")
    py_compile.compile(str(target_path), doraise=True)
    log_line(config.log_path, f"Plugin generado: {target_path} | plugin_id={config.plugin_id} | kind={config.kind}")
    return target_path


def run_health_check(config: FactoryConfig) -> int:
    result = subprocess.run([sys.executable, str(config.capatch_path), "--plugin-health"], capture_output=True, text=True)
    emit("\n[INFO] Resultado de capatch --plugin-health:\n")
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    return result.returncode


def run_self_test() -> int:
    emit("[OK] capatch_plugin_factory workspace listo.")
    emit(f"[OK] Capatch default: {DEFAULT_CAPATCH_PATH}")
    emit(f"[OK] Plugins activos default: {DEFAULT_PLUGINS_DIR}")
    emit(f"[OK] Templates default: {DEFAULT_TEMPLATES_DIR}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.list_kinds:
        return list_kinds()
    if args.self_test:
        return run_self_test()
    try:
        config = build_config(args)
        target = write_plugin(config)
        emit(f"[OK] Plugin generado: {target}")
        emit(f"[OK] PLUGIN_ID: {config.plugin_id}")
        emit(f"[OK] kind: {config.kind}")
        if config.run_health_check and not config.dry_run:
            code = run_health_check(config)
            if code != 0:
                fail(f"capatch --plugin-health regreso codigo {code}")
        return 0
    except FactoryError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    except py_compile.PyCompileError as exc:
        print(f"[ERROR] No compilo el plugin generado: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"[ERROR] Error inesperado en factory: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
