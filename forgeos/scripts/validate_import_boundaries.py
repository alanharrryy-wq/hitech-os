from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModuleNode:
    file_path: Path
    module_name: str
    layer: str
    product_id: str | None


@dataclass(frozen=True)
class Violation:
    rule_id: str
    message: str
    importer_module: str
    importer_file: str
    imported_module: str
    line: int


FORGEOS_ROOT = Path(__file__).resolve().parents[1]


def build_module_index(root: Path) -> dict[str, ModuleNode]:
    index: dict[str, ModuleNode] = {}
    roots = [
        (root / "platform" / "forge_kernel" / "src", "kernel", None),
        (root / "platform" / "forge_commons" / "src", "commons", None),
    ]
    products_root = root / "products"
    if products_root.exists():
        for product_dir in sorted(products_root.iterdir()):
            if not product_dir.is_dir():
                continue
            if product_dir.name == "_skeleton":
                continue
            src_root = product_dir / "src"
            if src_root.exists():
                roots.append((src_root, "product", product_dir.name))

    for src_root, layer, product_id in roots:
        if not src_root.exists():
            continue
        for py_file in src_root.rglob("*.py"):
            module_name = module_name_for_file(src_root=src_root, file_path=py_file)
            index[module_name] = ModuleNode(
                file_path=py_file,
                module_name=module_name,
                layer=layer,
                product_id=product_id,
            )
    return index


def module_name_for_file(src_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(src_root)
    if rel.name == "__init__.py":
        rel = rel.parent
    else:
        rel = rel.with_suffix("")
    return ".".join(rel.parts)


def resolve_relative_module(importer_module: str, level: int, module: str | None) -> str:
    importer_parts = importer_module.split(".")
    base_parts = importer_parts[:-1]
    if level > 0:
        if level > len(base_parts):
            return module or ""
        base_parts = base_parts[: len(base_parts) - level + 1]
    if module:
        if base_parts:
            return ".".join(base_parts + module.split("."))
        return module
    return ".".join(base_parts)


def normalize_imported_module(
    importer_module: str,
    raw_module: str | None,
    level: int,
) -> str:
    if level > 0:
        return resolve_relative_module(importer_module=importer_module, level=level, module=raw_module)
    return raw_module or ""


def top_package(module_name: str) -> str:
    return module_name.split(".")[0] if module_name else ""


def known_layer_for_top_package(top: str, index: dict[str, ModuleNode]) -> tuple[str, str | None] | None:
    for node in index.values():
        if node.module_name.split(".")[0] == top:
            return (node.layer, node.product_id)
    return None


def collect_violations(root: Path, index: dict[str, ModuleNode]) -> list[Violation]:
    violations: list[Violation] = []
    for module_name, node in sorted(index.items()):
        tree = ast.parse(node.file_path.read_text(encoding="utf-8"), filename=str(node.file_path))
        for stmt in ast.walk(tree):
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    imported = alias.name
                    violations.extend(
                        evaluate_import(
                            importer=node,
                            imported_module=imported,
                            line=stmt.lineno,
                            index=index,
                        )
                    )
            elif isinstance(stmt, ast.ImportFrom):
                imported = normalize_imported_module(
                    importer_module=module_name,
                    raw_module=stmt.module,
                    level=stmt.level,
                )
                if imported:
                    violations.extend(
                        evaluate_import(
                            importer=node,
                            imported_module=imported,
                            line=stmt.lineno,
                            index=index,
                        )
                    )
    return violations


def evaluate_import(
    importer: ModuleNode,
    imported_module: str,
    line: int,
    index: dict[str, ModuleNode],
) -> list[Violation]:
    violations: list[Violation] = []
    top = top_package(imported_module)
    if not top:
        return violations

    known = known_layer_for_top_package(top, index=index)
    if known is None:
        return violations
    imported_layer, imported_product = known

    if importer.layer == "kernel":
        if imported_layer == "product":
            violations.append(
                Violation(
                    rule_id="BOUND-01-KERNEL-NO-PRODUCT",
                    message="kernel cannot import product modules",
                    importer_module=importer.module_name,
                    importer_file=str(importer.file_path),
                    imported_module=imported_module,
                    line=line,
                )
            )

    if importer.layer == "commons":
        if imported_layer == "product":
            violations.append(
                Violation(
                    rule_id="BOUND-01-COMMONS-NO-PRODUCT",
                    message="commons cannot import product modules",
                    importer_module=importer.module_name,
                    importer_file=str(importer.file_path),
                    imported_module=imported_module,
                    line=line,
                )
            )

    if importer.layer == "product":
        if imported_layer == "product" and imported_product != importer.product_id:
            violations.append(
                Violation(
                    rule_id="BOUND-01-PRODUCT-NO-CROSS-PRODUCT",
                    message="product cannot import other product modules",
                    importer_module=importer.module_name,
                    importer_file=str(importer.file_path),
                    imported_module=imported_module,
                    line=line,
                )
            )

    return violations


def write_report(report_path: Path, violations: list[Violation], scanned_modules: int) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "PASS" if not violations else "FAIL",
        "scanned_modules": scanned_modules,
        "violation_count": len(violations),
        "violations": [
            {
                "rule_id": v.rule_id,
                "message": v.message,
                "importer_module": v.importer_module,
                "importer_file": v.importer_file,
                "imported_module": v.imported_module,
                "line": v.line,
            }
            for v in violations
        ],
    }
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ForgeOS import boundaries.")
    parser.add_argument(
        "--root",
        default=str(FORGEOS_ROOT),
        help="ForgeOS workspace root.",
    )
    parser.add_argument(
        "--report",
        default=str(FORGEOS_ROOT.parent / "tools" / "_local" / "evidence" / "forgeos_import_boundaries_report.json"),
        help="Path to write JSON report.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report_path = Path(args.report).resolve()
    module_index = build_module_index(root)
    violations = collect_violations(root=root, index=module_index)
    write_report(report_path=report_path, violations=violations, scanned_modules=len(module_index))

    if violations:
        print(f"[ForgeOS] Import boundary validation FAILED with {len(violations)} violation(s).")
        for violation in violations:
            print(
                f"- {violation.rule_id}: {violation.importer_module} -> {violation.imported_module} "
                f"({violation.importer_file}:{violation.line})"
            )
        return 1

    print(f"[ForgeOS] Import boundary validation PASSED. Scanned modules: {len(module_index)}")
    print(f"[ForgeOS] Report: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
