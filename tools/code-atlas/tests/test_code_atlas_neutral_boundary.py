from __future__ import annotations

import ast
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CODE_ATLAS_ROOT = REPO_ROOT / "tools" / "code-atlas"
PACKAGE_ROOT = CODE_ATLAS_ROOT / "src" / "code_atlas"
NEUTRAL_NAMESPACES = {
    "core",
    "operational",
    "surface_target_atlas",
    "legal_readiness",
    "coverage",
    "db_glass",
    "manifest",
    "cli",
}
NEUTRAL_ROOTS = tuple(PACKAGE_ROOT / name for name in sorted(NEUTRAL_NAMESPACES))


def _neutral_files() -> list[Path]:
    files: list[Path] = []
    for root in NEUTRAL_ROOTS:
        if root.exists():
            files.extend(root.rglob("*.py"))
    return sorted(set(files))


def _internal_namespace_from_import(node: ast.AST, current_namespace: str) -> str | None:
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name.startswith("code_atlas."):
                parts = alias.name.split(".")
                return parts[1] if len(parts) > 1 else None
        return None
    if not isinstance(node, ast.ImportFrom):
        return None
    module = node.module or ""
    if node.level == 0 and module.startswith("code_atlas."):
        parts = module.split(".")
        return parts[1] if len(parts) > 1 else None
    if node.level == 1:
        return current_namespace
    if node.level >= 2:
        return module.split(".", 1)[0] if module else None
    return None


class CodeAtlasNeutralImportBoundaryTests(unittest.TestCase):
    def test_neutral_core_never_imports_project_adapter_namespaces(self) -> None:
        violations: list[str] = []
        for path in _neutral_files():
            relative = path.relative_to(PACKAGE_ROOT)
            current_namespace = relative.parts[0]
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(relative))
            for node in ast.walk(tree):
                namespace = _internal_namespace_from_import(node, current_namespace)
                if namespace and namespace not in NEUTRAL_NAMESPACES:
                    violations.append(f"{relative.as_posix()}:{getattr(node, 'lineno', 0)} -> code_atlas.{namespace}")
        self.assertEqual(violations, [], "Neutral core imports optional/project adapter namespaces: " + " | ".join(violations))

    def test_base_cli_exports_only_neutral_commands(self) -> None:
        from code_atlas.cli.main import COMMANDS

        self.assertEqual(
            set(COMMANDS),
            {"coverage", "gate", "db", "todo-plus", "operational", "surface-target"},
        )


if __name__ == "__main__":
    unittest.main()
