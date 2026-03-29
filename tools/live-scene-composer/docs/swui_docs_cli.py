#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List, Sequence

REQUIRED_BOOTSTRAP_SCRIPTS = [
    "bootstrap_docs_index.sh",
    "bootstrap_docs_toc.sh",
    "bootstrap_docs_part1.sh",
    "bootstrap_docs_part2.sh",
    "bootstrap_docs_part3.sh",
    "bootstrap_docs_part4.sh",
    "bootstrap_docs_arch_guard.sh",
]

SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
CRITICAL_DOCS = [
    "README.md",
    "00_TOC.md",
    "00_READING_PATHS.md",
    "01_PROJECT_OVERVIEW.md",
    "05_SYSTEM_ARCHITECTURE.md",
    "06_SYSTEM_BOUNDARIES.md",
    "07_DOMAIN_MODEL.md",
    "10_MUTATION_MODEL.md",
    "18_RUNTIME_MUTATION_BRIDGE.md",
    "19_DEPENDENCY_POLICY.md",
    "20_PROTECTED_NODES.md",
    "40_ARCHITECTURAL_DECISIONS.md",
    "41_ARCHITECTURE_GUARD_DOC_RULES.md",
]
ALL_EXPECTED_DOCS = [
    "README.md",
    "00_DOCS_INDEX.md",
    "00_TOC.md",
    "00_READING_PATHS.md",
] + [
    f"{i:02d}_{name}.md"
    for i, name in [
        (1, "PROJECT_OVERVIEW"),
        (2, "PRODUCT_VISION"),
        (3, "GOALS_AND_NON_GOALS"),
        (4, "CORE_CONCEPTS"),
        (5, "SYSTEM_ARCHITECTURE"),
        (6, "SYSTEM_BOUNDARIES"),
        (7, "DOMAIN_MODEL"),
        (8, "STATE_MODEL"),
        (9, "RUNTIME_MODEL"),
        (10, "MUTATION_MODEL"),
        (11, "MODULE_SYSTEM"),
        (12, "MODULE_SDK"),
        (13, "WIDGET_SYSTEM"),
        (14, "SLOT_SYSTEM"),
        (15, "LAYOUT_SYSTEM"),
        (16, "PREFAB_SYSTEM"),
        (17, "CUSTOM_WIDGET_SANDBOX"),
        (18, "RUNTIME_MUTATION_BRIDGE"),
        (19, "DEPENDENCY_POLICY"),
        (20, "PROTECTED_NODES"),
        (21, "DEVELOPER_GUIDE"),
        (22, "CONTRIBUTING"),
        (23, "CODE_STYLE"),
        (24, "TESTING_STRATEGY"),
        (25, "DEBUGGING_GUIDE"),
        (26, "ERROR_HANDLING"),
        (27, "PERFORMANCE_MODEL"),
        (28, "SECURITY_MODEL"),
        (29, "OPERATIONS_GUIDE"),
        (30, "DEPLOYMENT_MODEL"),
        (31, "USER_MANUAL"),
        (32, "WORKFLOW_GUIDE"),
        (33, "FEATURE_REFERENCE"),
        (34, "UI_INTERACTION_MODEL"),
        (35, "THEME_AND_STYLE_SYSTEM"),
        (36, "DATA_BINDING_MODEL"),
        (37, "VERSIONING_MODEL"),
        (38, "CHANGELOG"),
        (39, "ROADMAP"),
        (40, "ARCHITECTURAL_DECISIONS"),
        (41, "ARCHITECTURE_GUARD_DOC_RULES"),
    ]
]
CRITICAL_REFERENCES = [
    "01_PROJECT_OVERVIEW.md",
    "05_SYSTEM_ARCHITECTURE.md",
    "06_SYSTEM_BOUNDARIES.md",
    "07_DOMAIN_MODEL.md",
    "10_MUTATION_MODEL.md",
    "18_RUNTIME_MUTATION_BRIDGE.md",
    "19_DEPENDENCY_POLICY.md",
    "20_PROTECTED_NODES.md",
    "40_ARCHITECTURAL_DECISIONS.md",
]
GUARD_RULE_TOKENS = [
    "console-core",
    "runtime-debug-console",
    "live-scene-composer",
    "runtime-mutation-bridge",
]
IMPORT_RE = re.compile(
    r"(?:import|export)\\s+[^;]*?\\s+from\\s+['\"]([^'\"]+)['\"]|require\\(\\s*['\"]([^'\"]+)['\"]\\s*\\)",
    re.MULTILINE | re.DOTALL,
)
HEREDOC_RE = None



class ProgressPrinter:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.total = 0
        self.current = 0

    def start(self, total: int, title: str) -> None:
        self.total = max(total, 1)
        self.current = 0
        if self.enabled:
            print(title)

    def step(self, label: str) -> None:
        self.current += 1
        if not self.enabled:
            return
        width = 24
        filled = int(width * self.current / self.total)
        bar = "#" * filled + "-" * (width - filled)
        print(f"[{bar}] {self.current:>2}/{self.total:<2} {label}")


@dataclass(frozen=True)
class TemplateEntry:
    source_script: Path
    source_var: str
    target_relative_path: str
    body: str

    @property
    def extension(self) -> str:
        return Path(self.target_relative_path).suffix.lower()


def parse_templates(script_path: Path) -> List[TemplateEntry]:
    text = script_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    entries: List[TemplateEntry] = []
    i = 0

    header_re = re.compile(r'^cat > "\$(?P<var>[A-Z_]+)/(?P<target>[^"]+)" <<\'EOF\'$')
    while i < len(lines):
        match = header_re.match(lines[i])
        if not match:
            i += 1
            continue

        body_lines: List[str] = []
        i += 1
        while i < len(lines) and lines[i] != "EOF":
            body_lines.append(lines[i])
            i += 1

        if i >= len(lines):
            raise ValueError(f"EOF sin cierre en {script_path}")

        entries.append(
            TemplateEntry(
                source_script=script_path,
                source_var=match.group("var"),
                target_relative_path=match.group("target"),
                body="\n".join(body_lines),
            )
        )
        i += 1

    return entries


def discover_source_dir(explicit: str | None, repo_root: Path) -> Path:
    candidates: List[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser().resolve())
    script_dir = Path(__file__).resolve().parent
    cwd = Path.cwd().resolve()
    candidates.extend([
        script_dir,
        cwd,
        repo_root,
        repo_root / "tools",
        repo_root / "scripts",
    ])

    seen = set()
    for candidate in candidates:
        if candidate in seen or not candidate.exists():
            continue
        seen.add(candidate)
        if all((candidate / name).exists() for name in REQUIRED_BOOTSTRAP_SCRIPTS):
            return candidate
    looked = "\n - ".join(str(item) for item in seen)
    raise FileNotFoundError(
        "No pude encontrar los scripts fuente de bootstrap. Busque en:\n - " + looked
    )


def collect_templates(source_dir: Path) -> List[TemplateEntry]:
    templates: List[TemplateEntry] = []
    for script_name in REQUIRED_BOOTSTRAP_SCRIPTS:
        script_path = source_dir / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Falta el archivo requerido: {script_path}")
        templates.extend(parse_templates(script_path))
    return templates


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + "\n", encoding="utf-8")


def bootstrap_docs(
    repo_root: Path,
    docs_root: Path,
    tools_root: Path,
    source_dir: Path,
    include_extracted_validator: bool,
    progress: ProgressPrinter,
) -> List[str]:
    templates = collect_templates(source_dir)
    filtered: List[TemplateEntry] = []
    for item in templates:
        ext = item.extension
        if item.source_var == "DOCS_DIR":
            filtered.append(item)
        elif item.source_var == "TOOLS_DIR" and include_extracted_validator and ext == ".py":
            filtered.append(item)

    progress.start(len(filtered), "\nGenerando artefactos en Python...")
    written: List[str] = []
    for item in filtered:
        if item.source_var == "DOCS_DIR":
            output_path = docs_root / item.target_relative_path
        else:
            output_path = tools_root / item.target_relative_path
        write_text(output_path, item.body.rstrip("\n"))
        written.append(str(output_path.relative_to(repo_root)).replace("\\", "/"))
        progress.step(written[-1])
    return written


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def normalize_import_path(value: str) -> str:
    return value.replace("\\", "/").strip()


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def iter_source_files(paths: Iterable[Path]) -> Iterator[Path]:
    for base in paths:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in SOURCE_EXTENSIONS:
                yield path


def extract_imports(file_path: Path) -> List[str]:
    text = read_text(file_path)
    values: List[str] = []
    for match in IMPORT_RE.findall(text):
        raw = match[0] or match[1]
        if raw:
            values.append(normalize_import_path(raw))
    return values


def make_check(rule_id: str, status: str, message: str, files: Sequence[str] | None = None) -> dict:
    return {
        "rule_id": rule_id,
        "status": status,
        "message": message,
        "files": list(files or []),
    }


def validate_architecture(repo_root: Path, docs_root: Path, report_file: Path | None, json_report_file: Path | None, progress: ProgressPrinter) -> int:
    components_root = repo_root / "apps" / "keystone" / "components"
    dev_console_root = components_root / "dev-console"
    legacy_core_root = dev_console_root / "core"

    checks: List[dict] = []
    warnings: List[dict] = []

    steps = 7
    progress.start(steps, "\nValidando guardrails de arquitectura...")

    # AGR-001
    if docs_root.exists():
        checks.append(make_check("AGR-001", "PASS", f"Docs root exists: {relative(docs_root, repo_root)}"))
    else:
        checks.append(make_check("AGR-001", "FAIL", f"Docs root missing: {relative(docs_root, repo_root)}"))

    missing_all = [name for name in ALL_EXPECTED_DOCS if not (docs_root / name).exists()]
    checks.append(
        make_check(
            "AGR-001A",
            "FAIL" if missing_all else "PASS",
            "Expected documentation files are missing" if missing_all else "All expected docs are present",
            missing_all,
        )
    )
    missing_critical = [name for name in CRITICAL_DOCS if not (docs_root / name).exists()]
    checks.append(
        make_check(
            "AGR-001B",
            "FAIL" if missing_critical else "PASS",
            "Critical architecture docs are missing" if missing_critical else "All critical architecture docs are present",
            missing_critical,
        )
    )
    progress.step("AGR-001 docs e inventario")

    # AGR-002
    checks.append(
        make_check(
            "AGR-002",
            "FAIL" if legacy_core_root.exists() else "PASS",
            "Legacy shared-core path exists and must not be reintroduced" if legacy_core_root.exists() else "Legacy shared-core path is absent",
            [relative(legacy_core_root, repo_root)] if legacy_core_root.exists() else [],
        )
    )
    progress.step("AGR-002 path legacy")

    # scan imports
    source_files = list(iter_source_files([components_root, repo_root / "apps" / "keystone" / "tests"]))
    legacy_import_hits: List[str] = []
    debug_to_composer_hits: List[str] = []
    composer_to_debug_hits: List[str] = []
    composer_to_pitch_debug_warns: List[str] = []

    for file_path in source_files:
        rel = relative(file_path, repo_root)
        rel_norm = rel.replace("\\", "/")
        imports = extract_imports(file_path)
        for item in imports:
            item_norm = normalize_import_path(item)
            if "dev-console/core" in item_norm:
                legacy_import_hits.append(f"{rel} -> {item_norm}")
            elif "apps/keystone/components/dev-console" in rel_norm:
                if item_norm.startswith("./core/") or item_norm == "./core" or "/core/" in item_norm or item_norm.endswith("/core"):
                    legacy_import_hits.append(f"{rel} -> {item_norm}")

            if "apps/keystone/components/dev-console" in rel_norm and "live-scene-composer" in item_norm:
                debug_to_composer_hits.append(f"{rel} -> {item_norm}")

            if "apps/keystone/components/live-scene-composer" in rel_norm:
                if ("runtime-debug-console" in item_norm or "dev-console" in item_norm) and "console-core" not in item_norm:
                    composer_to_debug_hits.append(f"{rel} -> {item_norm}")
                if "pitch/debug" in item_norm:
                    composer_to_pitch_debug_warns.append(f"{rel} -> {item_norm}")

    checks.append(make_check("AGR-003", "FAIL" if legacy_import_hits else "PASS", "Legacy dev-console core import references detected" if legacy_import_hits else "No legacy dev-console core imports detected", legacy_import_hits))
    progress.step("AGR-003 imports legacy")

    checks.append(make_check("AGR-004", "FAIL" if debug_to_composer_hits else "PASS", "Runtime Debug Console boundary imports Composer product logic" if debug_to_composer_hits else "Runtime Debug Console boundary does not import Composer product logic", debug_to_composer_hits))
    progress.step("AGR-004 debug -> composer")

    checks.append(make_check("AGR-005", "FAIL" if composer_to_debug_hits else "PASS", "Composer imports Runtime Debug Console or non-console-core dev-console product logic" if composer_to_debug_hits else "Composer does not import Runtime Debug Console product logic", composer_to_debug_hits))
    if composer_to_pitch_debug_warns:
        warnings.append(make_check("AGR-W001", "WARN", "Composer imports pitch/debug paths directly; review whether this should become an explicit adapter seam", composer_to_pitch_debug_warns))
    progress.step("AGR-005 composer -> debug")

    # AGR-006
    for file_name in ["README.md", "00_TOC.md", "00_READING_PATHS.md"]:
        path = docs_root / file_name
        if not path.exists():
            checks.append(make_check("AGR-006", "FAIL", f"{file_name} is missing", [file_name]))
            continue
        text = read_text(path)
        missing_refs = [ref for ref in CRITICAL_REFERENCES if ref not in text]
        checks.append(make_check("AGR-006", "FAIL" if missing_refs else "PASS", f"{file_name} is missing references to one or more critical docs" if missing_refs else f"{file_name} references the critical docs", missing_refs))
    progress.step("AGR-006 índices")

    # AGR-007
    guard_doc = docs_root / "41_ARCHITECTURE_GUARD_DOC_RULES.md"
    if guard_doc.exists():
        missing_tokens = [token for token in GUARD_RULE_TOKENS if token not in read_text(guard_doc)]
        checks.append(make_check("AGR-007", "FAIL" if missing_tokens else "PASS", "Guard rules doc is missing canonical boundary tokens" if missing_tokens else "Guard rules doc names all canonical boundaries", missing_tokens))
    else:
        checks.append(make_check("AGR-007", "FAIL", "Guard rules doc is missing", ["41_ARCHITECTURE_GUARD_DOC_RULES.md"]))
    progress.step("AGR-007 boundaries canónicas")

    failures = [item for item in checks if item["status"] == "FAIL"]
    passes = [item for item in checks if item["status"] == "PASS"]
    summary = {
        "repo_root": str(repo_root),
        "docs_root": str(docs_root),
        "result": "FAIL" if failures else "PASS",
        "pass_count": len(passes),
        "fail_count": len(failures),
        "warn_count": len(warnings),
        "checks": checks,
        "warnings": warnings,
    }

    lines = [
        "=" * 72,
        "LIVE SCENE COMPOSER DOCS ARCHITECTURE GUARD",
        "=" * 72,
        f"Repo root : {repo_root}",
        f"Docs root : {docs_root}",
        f"Result    : {summary['result']}",
        f"Passes    : {summary['pass_count']}",
        f"Fails     : {summary['fail_count']}",
        f"Warnings  : {summary['warn_count']}",
        "",
    ]
    for item in checks + warnings:
        lines.append(f"[{item['status']}] {item['rule_id']} :: {item['message']}")
        for file_entry in item.get("files", []):
            lines.append(f"  - {file_entry}")
        lines.append("")

    report_text = "\n".join(lines).rstrip() + "\n"
    print("\n" + report_text)

    if report_file is not None:
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(report_text, encoding="utf-8")
        print(f"Reporte de texto escrito en: {report_file}")
    if json_report_file is not None:
        json_report_file.parent.mkdir(parents=True, exist_ok=True)
        json_report_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"Reporte JSON escrito en: {json_report_file}")

    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI en Python para bootstrap y validacion de docs de Live Scene Composer sin ejecutar Bash.",
    )
    parser.add_argument("--repo-root", default=".", help="Raiz del repo")
    parser.add_argument("--source-dir", default=None, help="Carpeta donde viven los bootstrap_docs_*.sh")
    parser.add_argument("--quiet", action="store_true", help="Oculta la barra de progreso")

    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap = subparsers.add_parser("bootstrap", help="Genera docs y, si se pide, el validator Python extraido")
    bootstrap.add_argument("--docs-root", default="docs/live-scene-composer", help="Carpeta destino de docs")
    bootstrap.add_argument("--tools-root", default="tools/live-scene-composer", help="Carpeta destino de herramientas Python")
    bootstrap.add_argument("--include-extracted-validator", action="store_true", help="Extrae tambien validate_docs_architecture_guard.py desde el bootstrap legacy")

    validate = subparsers.add_parser("validate", help="Corre el guard de arquitectura")
    validate.add_argument("--docs-root", default="docs/live-scene-composer", help="Carpeta de docs a validar")
    validate.add_argument("--report-file", default="tools/_local/evidence/live_scene_composer_docs_arch_guard_report.txt", help="Reporte de texto")
    validate.add_argument("--json-report-file", default="tools/_local/evidence/live_scene_composer_docs_arch_guard_report.json", help="Reporte JSON")
    validate.add_argument("--no-report", action="store_true", help="No escribe reportes a disco")

    all_cmd = subparsers.add_parser("all", help="Genera docs y luego valida")
    all_cmd.add_argument("--docs-root", default="docs/live-scene-composer", help="Carpeta destino de docs")
    all_cmd.add_argument("--tools-root", default="tools/live-scene-composer", help="Carpeta destino de herramientas Python")
    all_cmd.add_argument("--include-extracted-validator", action="store_true", help="Extrae tambien validate_docs_architecture_guard.py desde el bootstrap legacy")
    all_cmd.add_argument("--report-file", default="tools/_local/evidence/live_scene_composer_docs_arch_guard_report.txt", help="Reporte de texto")
    all_cmd.add_argument("--json-report-file", default="tools/_local/evidence/live_scene_composer_docs_arch_guard_report.json", help="Reporte JSON")

    inventory = subparsers.add_parser("inventory", help="Lista los artefactos que puede generar desde los .sh legacy")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve()
    source_dir = discover_source_dir(args.source_dir, repo_root)
    progress = ProgressPrinter(enabled=not args.quiet)

    if args.command == "inventory":
        templates = collect_templates(source_dir)
        docs = [item.target_relative_path for item in templates if item.source_var == "DOCS_DIR"]
        tools = [item.target_relative_path for item in templates if item.source_var == "TOOLS_DIR"]
        print("Artefactos DOCS_DIR:")
        for item in docs:
            print(f" - {item}")
        print("\nArtefactos TOOLS_DIR:")
        for item in tools:
            print(f" - {item}")
        return 0

    if args.command == "bootstrap":
        docs_root = repo_root / args.docs_root
        tools_root = repo_root / args.tools_root
        written = bootstrap_docs(repo_root, docs_root, tools_root, source_dir, args.include_extracted_validator, progress)
        print(f"\nListo. Se generaron {len(written)} archivos.")
        return 0

    if args.command == "validate":
        docs_root = repo_root / args.docs_root
        report_file = None if args.no_report else repo_root / args.report_file
        json_report_file = None if args.no_report else repo_root / args.json_report_file
        return validate_architecture(repo_root, docs_root, report_file, json_report_file, progress)

    if args.command == "all":
        docs_root = repo_root / args.docs_root
        tools_root = repo_root / args.tools_root
        written = bootstrap_docs(repo_root, docs_root, tools_root, source_dir, args.include_extracted_validator, progress)
        print(f"\nBootstrap completo. Archivos generados: {len(written)}")
        return validate_architecture(
            repo_root=repo_root,
            docs_root=docs_root,
            report_file=repo_root / args.report_file,
            json_report_file=repo_root / args.json_report_file,
            progress=progress,
        )

    parser.error("Comando no soportado")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
        sys.exit(130)
