from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

_GO_MODULE = re.compile(r"(?m)^\s*module\s+([^\s]+)\s*$")
_GO_PACKAGE = re.compile(r"(?m)^\s*package\s+([A-Za-z_][A-Za-z0-9_]*)\s*$")
_GO_IMPORT_BLOCK = re.compile(r"(?ms)^\s*import\s*\((.*?)\)")
_GO_IMPORT_SINGLE = re.compile(r"(?m)^\s*import\s+(?:[._A-Za-z][A-Za-z0-9_]*\s+)?[\"`]([^\"`]+)[\"`]")
_GO_QUOTED_IMPORT = re.compile(r"(?:^|\s)(?:[._A-Za-z][A-Za-z0-9_]*\s+)?[\"`]([^\"`]+)[\"`]", re.M)
_GO_FUNC = re.compile(r"(?m)^\s*func\s+(?:\([^\n)]*\)\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_GO_DECL = re.compile(r"(?m)^\s*(?:type|var|const)\s+([A-Za-z_][A-Za-z0-9_]*)\b")

_JAVA_PACKAGE = re.compile(r"(?m)^\s*package\s+([A-Za-z_$][A-Za-z0-9_.$]*)\s*;")
_JAVA_IMPORT = re.compile(r"(?m)^\s*import\s+(static\s+)?([A-Za-z_$][A-Za-z0-9_.$]*\*?)\s*;")
_JAVA_TYPE = re.compile(
    r"(?m)^\s*(?:(?:public|protected|private|abstract|final|static|sealed|non-sealed|strictfp)\s+)*(?:class|interface|enum|record)\s+([A-Za-z_$][A-Za-z0-9_$]*)\b"
)


def _safe_text(repo: Path, rel: str, max_bytes: int = 600_000) -> str:
    path = repo / rel
    try:
        if not path.is_file() or path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _nearest_ancestor(path: Path, roots: set[str]) -> str | None:
    current = path.parent
    while True:
        candidate = current.as_posix()
        if candidate == ".":
            candidate = ""
        if candidate in roots:
            return candidate
        if not current.parts:
            return None
        current = current.parent


def _go_imports(text: str) -> list[str]:
    imports = list(_GO_IMPORT_SINGLE.findall(text))
    for block in _GO_IMPORT_BLOCK.findall(text):
        imports.extend(_GO_QUOTED_IMPORT.findall(block))
    return sorted(set(imports))


def _go_module_facts(repo: Path, file_paths: set[str]) -> list[tuple[str, str]]:
    modules: list[tuple[str, str]] = []
    for rel in sorted(path for path in file_paths if Path(path).name == "go.mod"):
        text = _safe_text(repo, rel)
        match = _GO_MODULE.search(text)
        if not match:
            continue
        root = Path(rel).parent.as_posix()
        if root == ".":
            root = ""
        modules.append((match.group(1).rstrip("/"), root))
    return sorted(modules, key=lambda item: (-len(item[0]), item[0], item[1]))


def _join_repo(root: str, suffix: str) -> str:
    if not root:
        return Path(suffix).as_posix() if suffix else ""
    return (Path(root) / suffix).as_posix() if suffix else Path(root).as_posix()


def _go_edges(
    repo: Path,
    files: list[dict[str, Any]],
    file_paths: set[str],
) -> tuple[set[tuple[str, str, str, str]], list[dict[str, Any]]]:
    edges: set[tuple[str, str, str, str]] = set()
    unresolved: list[dict[str, Any]] = []
    modules = _go_module_facts(repo, file_paths)
    go_rows: dict[str, dict[str, Any]] = {}
    prod_by_dir_package: dict[tuple[str, str], list[str]] = defaultdict(list)
    all_prod_by_dir: dict[str, list[str]] = defaultdict(list)
    symbols_by_dir_package: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)

    for row in files:
        rel = str(row.get("path") or "")
        if not rel.endswith(".go") or not row.get("isText") or row.get("sensitiveName"):
            continue
        text = _safe_text(repo, rel)
        if not text:
            continue
        package_match = _GO_PACKAGE.search(text)
        if not package_match:
            unresolved.append({
                "from": rel,
                "specifier": None,
                "language": "go",
                "reason": "go-package-declaration-not-found",
            })
            continue
        package = package_match.group(1)
        directory = Path(rel).parent.as_posix()
        if directory == ".":
            directory = ""
        is_test = rel.endswith("_test.go")
        go_rows[rel] = {"text": text, "package": package, "directory": directory, "isTest": is_test}
        if not is_test:
            prod_by_dir_package[(directory, package)].append(rel)
            all_prod_by_dir[directory].append(rel)
            symbols = [*_GO_FUNC.findall(text), *_GO_DECL.findall(text)]
            for symbol in symbols:
                symbols_by_dir_package[(directory, package)].setdefault(symbol, rel)

    for key in prod_by_dir_package:
        prod_by_dir_package[key].sort()
    for directory in all_prod_by_dir:
        all_prod_by_dir[directory].sort()

    for rel, info in sorted(go_rows.items()):
        text = str(info["text"])
        directory = str(info["directory"])
        package = str(info["package"])

        if info["isTest"]:
            for target in prod_by_dir_package.get((directory, package), []):
                if target != rel:
                    edges.add((rel, target, "go-test-package", f"parsed-go-same-package-test:{package}"))

        for symbol, target in sorted(symbols_by_dir_package.get((directory, package), {}).items()):
            if target == rel or len(symbol) < 3:
                continue
            if re.search(rf"\b{re.escape(symbol)}\b", text):
                edges.add((rel, target, "go-symbol", f"parsed-go-same-package-symbol:{symbol}"))

        for spec in _go_imports(text):
            local_module: tuple[str, str] | None = None
            for module_path, module_root in modules:
                if spec == module_path or spec.startswith(module_path + "/"):
                    local_module = (module_path, module_root)
                    break
            if local_module is None:
                continue
            module_path, module_root = local_module
            suffix = spec[len(module_path) :].lstrip("/")
            target_dir = _join_repo(module_root, suffix)
            targets = all_prod_by_dir.get(target_dir, [])
            if not targets:
                unresolved.append({
                    "from": rel,
                    "specifier": spec,
                    "language": "go",
                    "reason": "local-go-module-import-not-resolved-to-repository-package",
                    "evidence": f"go-module:{module_path}",
                })
                continue
            for target in targets:
                if target != rel:
                    edges.add((rel, target, "go-import", f"parsed-go-local-import:{spec}|module:{module_path}"))

    return edges, unresolved


def _java_source_set(rel: str) -> str:
    normalized = rel.replace("\\", "/")
    if "/src/test/java/" in "/" + normalized:
        return "test"
    if "/src/main/java/" in "/" + normalized:
        return "main"
    return "repository"


def _java_edges(
    repo: Path,
    files: list[dict[str, Any]],
) -> tuple[set[tuple[str, str, str, str]], list[dict[str, Any]]]:
    edges: set[tuple[str, str, str, str]] = set()
    unresolved: list[dict[str, Any]] = []
    rows: dict[str, dict[str, Any]] = {}
    fqcn_to_path: dict[str, str] = {}
    package_types: dict[str, dict[str, str]] = defaultdict(dict)

    for row in files:
        rel = str(row.get("path") or "")
        if not rel.endswith(".java") or not row.get("isText") or row.get("sensitiveName"):
            continue
        text = _safe_text(repo, rel)
        if not text:
            continue
        package_match = _JAVA_PACKAGE.search(text)
        package = package_match.group(1) if package_match else ""
        type_names = _JAVA_TYPE.findall(text)
        if not type_names:
            type_names = [Path(rel).stem]
        rows[rel] = {
            "text": text,
            "package": package,
            "types": sorted(set(type_names)),
            "sourceSet": _java_source_set(rel),
        }
        for type_name in sorted(set(type_names)):
            fqcn = f"{package}.{type_name}" if package else type_name
            if fqcn in fqcn_to_path and fqcn_to_path[fqcn] != rel:
                unresolved.append({
                    "from": rel,
                    "specifier": fqcn,
                    "language": "java",
                    "reason": "duplicate-local-java-type",
                })
                fqcn_to_path.pop(fqcn, None)
                package_types[package].pop(type_name, None)
                continue
            fqcn_to_path[fqcn] = rel
            package_types[package][type_name] = rel

    local_packages = sorted(package_types, key=lambda item: (-len(item), item))
    for rel, info in sorted(rows.items()):
        text = str(info["text"])
        package = str(info["package"])
        source_set = str(info["sourceSet"])

        for _static, spec in _JAVA_IMPORT.findall(text):
            if spec.endswith(".*"):
                prefix = spec[:-2]
                if prefix in package_types:
                    unresolved.append({
                        "from": rel,
                        "specifier": spec,
                        "language": "java",
                        "reason": "local-java-wildcard-import-not-expanded",
                    })
                continue
            target = fqcn_to_path.get(spec)
            if target is None and _static:
                parts = spec.split(".")
                for end in range(len(parts) - 1, 0, -1):
                    target = fqcn_to_path.get(".".join(parts[:end]))
                    if target:
                        break
            if target and target != rel:
                edges.add((rel, target, "java-import", f"parsed-java-local-import:{spec}|source-set:{source_set}"))
                continue
            if any(spec.startswith(local + ".") for local in local_packages if local):
                unresolved.append({
                    "from": rel,
                    "specifier": spec,
                    "language": "java",
                    "reason": "local-looking-java-import-not-resolved",
                })

        for type_name, target in sorted(package_types.get(package, {}).items()):
            if target == rel:
                continue
            if re.search(rf"\b{re.escape(type_name)}\b", text):
                edges.add((rel, target, "java-package-type", f"parsed-java-same-package-type:{package}.{type_name}|source-set:{source_set}"))

    return edges, unresolved


def bounded_language_dependency_edges(
    repo_root: str | Path,
    inventory: dict[str, Any],
) -> tuple[set[tuple[str, str, str, str]], list[dict[str, Any]]]:
    """Return only repository-provable Go/Java relationships.

    External package managers, runtime reflection, generated code, build tags and
    other dynamic semantics are intentionally not guessed. Local-looking facts
    that cannot be resolved are emitted as unresolved evidence instead.
    """

    repo = Path(repo_root).resolve()
    files = inventory.get("files") or []
    file_paths = {str(row.get("path")) for row in files if row.get("path")}
    go_edges, go_unresolved = _go_edges(repo, files, file_paths)
    java_edges, java_unresolved = _java_edges(repo, files)
    return go_edges | java_edges, [*go_unresolved, *java_unresolved]


__all__ = ["bounded_language_dependency_edges"]
