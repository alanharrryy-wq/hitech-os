from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

REQUIRED_INTENT_FIELDS = (
    "visual_role",
    "visual_variant",
    "visual_emphasis",
    "visual_fx_level",
)

GOVERNED_BASES = ("VisualScreenTemplate", "GlassPanelTemplate")
RAW_QT_BASES = ("QMainWindow", "QDialog", "QWidget")
BYPASS_MARKERS = (
    "AppearanceCoordinator",
    "resolve_appearance_tokens(",
)

SKIP_PATH_PARTS = (
    "/docs/",
    "/artifacts/",
    "/__pycache__/",
    "/_ui_baseline_bundle/",
    "/_chatgpt_patch_backups/",
    "/examples_backup/",
    "/examples_backup_",
    "/.pytest_cache/",
    "/site-packages/",
)

EXAMPLE_PATH_PARTS = (
    "/examples/",
    "/examples/examples/",
)

SCREEN_TOOL_FILES = {
    "new_ui_screen.py",
    "validate_ui_baseline.py",
    "ui_baseline_builder.py",
}

FOUNDATION_STYLE_FILES = {
    "scene.py",
    "_template_shell_appearance.py",
    "charts.py",
    "theme.py",
}


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    severity: str
    path: str
    rule: str
    detail: str


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _norm(path: Path) -> str:
    return str(path).replace("\\", "/").lower()


def _should_skip(path: Path, *, exclude_examples: bool) -> bool:
    lowered = _norm(path)
    if any(token in lowered for token in SKIP_PATH_PARTS):
        return True
    if exclude_examples and any(token in lowered for token in EXAMPLE_PATH_PARTS):
        return True
    return False


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _screen_class_candidates(text: str) -> list[tuple[str, set[str], set[str]]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    matches: list[tuple[str, set[str], set[str]]] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if not node.name.endswith("Screen"):
            continue

        bases: set[str] = set()
        for base in node.bases:
            token = _call_name(base)
            if token:
                bases.add(token.split(".")[-1])

        attrs: set[str] = set()
        for child in node.body:
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        attrs.add(target.id)
            elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                attrs.add(child.target.id)

        matches.append((node.name, bases, attrs))
    return matches


def _is_governed_stylesheet_arg(node: ast.AST) -> bool:
    if isinstance(node, ast.Call):
        name = _call_name(node.func)
        short = name.split(".")[-1]
        if short in {"build_stylesheet", "build_chart_stylesheet"}:
            return True

    if isinstance(node, ast.Name):
        return node.id in {"stylesheet", "style_sheet", "qss"}

    return False


def _find_real_stylesheet_violations(path: Path, text: str) -> list[str]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        call_name = _call_name(node.func)
        if not call_name.endswith("setStyleSheet"):
            continue

        arg0 = node.args[0] if node.args else None
        if arg0 is not None and _is_governed_stylesheet_arg(arg0):
            continue

        if path.name in FOUNDATION_STYLE_FILES and arg0 is not None and _is_governed_stylesheet_arg(arg0):
            continue

        violations.append(call_name)

    return violations


def validate_file(path: Path, *, exclude_examples: bool) -> list[ValidationIssue]:
    if _should_skip(path, exclude_examples=exclude_examples):
        return []

    text = _read_text(path)
    issues: list[ValidationIssue] = []
    lowered_name = path.name.lower()

    stylesheet_violations = _find_real_stylesheet_violations(path, text)
    if stylesheet_violations:
        issues.append(
            ValidationIssue(
                severity="ERROR",
                path=str(path),
                rule="hardcoded_stylesheet",
                detail="Se detectó una llamada real a setStyleSheet(...) fuera de una zona foundation permitida.",
            )
        )

    if lowered_name in SCREEN_TOOL_FILES:
        return issues

    if not lowered_name.endswith("_screen.py"):
        return issues

    screen_classes = _screen_class_candidates(text)

    if not screen_classes:
        issues.append(
            ValidationIssue(
                severity="ERROR",
                path=str(path),
                rule="missing_screen_class",
                detail="El archivo _screen.py no declara una clase *Screen reconocible.",
            )
        )
        return issues

    has_governed_base = False

    for class_name, bases, attrs in screen_classes:
        if any(base in GOVERNED_BASES for base in bases):
            has_governed_base = True

        if any(base in RAW_QT_BASES for base in bases) and not any(base in GOVERNED_BASES for base in bases):
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    path=str(path),
                    rule="raw_final_widget_identity",
                    detail=f"La clase {class_name} usa una clase Qt cruda como identidad final.",
                )
            )

        for field_name in REQUIRED_INTENT_FIELDS:
            if field_name not in attrs:
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        path=str(path),
                        rule="missing_visual_intent",
                        detail=f"La clase {class_name} no declara `{field_name}`.",
                    )
                )

    if not has_governed_base:
        issues.append(
            ValidationIssue(
                severity="ERROR",
                path=str(path),
                rule="missing_governed_base",
                detail="La screen no hereda de VisualScreenTemplate ni GlassPanelTemplate.",
            )
        )

    for marker in BYPASS_MARKERS:
        if marker in text:
            issues.append(
                ValidationIssue(
                    severity="WARN",
                    path=str(path),
                    rule="screen_bypass_signal",
                    detail=f"La screen contiene una señal de bypass del core: {marker}",
                )
            )

    return issues


def validate_repository(root: Path, *, exclude_examples: bool) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path in root.rglob("*.py"):
        issues.extend(validate_file(path, exclude_examples=exclude_examples))
    return issues


def render_report(issues: list[ValidationIssue], root: Path) -> str:
    lines = [f"Reporte de validación: {root}", ""]
    if not issues:
        lines.append("Sin hallazgos. El baseline quedó delgado, gobernado y sin autoridad visual paralela.")
        return "\n".join(lines)

    buckets: dict[str, list[ValidationIssue]] = {"ERROR": [], "WARN": []}
    for issue in issues:
        buckets.setdefault(issue.severity, []).append(issue)

    for severity in ("ERROR", "WARN"):
        current = buckets.get(severity, [])
        if not current:
            continue
        lines.append(f"[{severity}]")
        for issue in current:
            lines.append(f"- {issue.rule}: {issue.path}")
            lines.append(f"  {issue.detail}")
        lines.append("")

    return "\n".join(lines).rstrip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Valida heurísticamente una base ui_baseline.")
    parser.add_argument("root", nargs="?", default=".", help="Ruta raíz a inspeccionar.")
    parser.add_argument(
        "--exclude-examples",
        action="store_true",
        help="Excluye examples/ del escaneo.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).expanduser().resolve()
    issues = validate_repository(root, exclude_examples=bool(args.exclude_examples))
    print(render_report(issues, root))
    return 1 if any(issue.severity == "ERROR" for issue in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
