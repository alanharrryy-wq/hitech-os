from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

_GO_MODULE = re.compile(r"(?m)^\s*module\s+([^\s]+)\s*$")
_GO_PACKAGE = re.compile(r"(?m)^\s*package\s+([A-Za-z_][A-Za-z0-9_]*)\s*$")
_GO_IMPORT_BLOCK = re.compile(r"(?ms)^\s*import\s*\((.*?)\)")
_GO_IMPORT_SINGLE_ENTRY = re.compile(
    r"(?m)^\s*import\s+(?:(?P<alias>[._A-Za-z][A-Za-z0-9_]*)\s+)?[\"`](?P<spec>[^\"`]+)[\"`]"
)
_GO_IMPORT_BLOCK_ENTRY = re.compile(
    r"(?m)^\s*(?:(?P<alias>[._A-Za-z][A-Za-z0-9_]*)\s+)?[\"`](?P<spec>[^\"`]+)[\"`]"
)
_GO_FREE_FUNC = re.compile(r"(?m)^func\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_GO_METHOD = re.compile(r"(?m)^func\s+\([^\n)]*\)\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_GO_TYPE = re.compile(r"(?m)^type\s+([A-Za-z_][A-Za-z0-9_]*)\b")
_GO_VALUE = re.compile(r"(?m)^(var|const)\s+([A-Za-z_][A-Za-z0-9_]*)\b")
_GO_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_GO_LINE_COMMENT = re.compile(r"//[^\n]*")
_GO_RAW_STRING = re.compile(r"`[^`]*`", re.S)
_GO_QUOTED_STRING = re.compile(r'"(?:\\.|[^"\\\n])*"')
_GO_RUNE = re.compile(r"'(?:\\.|[^'\\\n])+'")

_GO_PREDECLARED = {
    "any",
    "append",
    "bool",
    "byte",
    "cap",
    "clear",
    "close",
    "comparable",
    "complex",
    "complex128",
    "complex64",
    "copy",
    "delete",
    "error",
    "false",
    "float32",
    "float64",
    "imag",
    "int",
    "int16",
    "int32",
    "int64",
    "int8",
    "iota",
    "len",
    "make",
    "max",
    "min",
    "new",
    "nil",
    "panic",
    "print",
    "println",
    "real",
    "recover",
    "rune",
    "string",
    "true",
    "uint",
    "uint16",
    "uint32",
    "uint64",
    "uint8",
    "uintptr",
}

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


def _blank_non_newlines(match: re.Match[str]) -> str:
    return "".join("\n" if char == "\n" else " " for char in match.group(0))


def _go_code_only(text: str) -> str:
    """Blank comments and literals before lexical reference matching.

    This is intentionally a bounded lexer, not a Go parser. Its job is to prevent
    comments, examples and string contents from manufacturing file dependencies.
    """

    cleaned = _GO_BLOCK_COMMENT.sub(_blank_non_newlines, text)
    cleaned = _GO_LINE_COMMENT.sub(_blank_non_newlines, cleaned)
    cleaned = _GO_RAW_STRING.sub(_blank_non_newlines, cleaned)
    cleaned = _GO_QUOTED_STRING.sub(_blank_non_newlines, cleaned)
    cleaned = _GO_RUNE.sub(_blank_non_newlines, cleaned)
    return cleaned


def _go_import_entries(text: str) -> list[tuple[str | None, str]]:
    entries: list[tuple[str | None, str]] = []
    block_spans = [match.span() for match in _GO_IMPORT_BLOCK.finditer(text)]
    for block in _GO_IMPORT_BLOCK.findall(text):
        for match in _GO_IMPORT_BLOCK_ENTRY.finditer(block):
            entries.append((match.group("alias"), match.group("spec")))
    for match in _GO_IMPORT_SINGLE_ENTRY.finditer(text):
        start = match.start()
        if any(left <= start < right for left, right in block_spans):
            continue
        entries.append((match.group("alias"), match.group("spec")))
    return sorted(set(entries), key=lambda item: (item[1], item[0] or ""))


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


def _go_top_level_declarations(text: str) -> list[tuple[str, str]]:
    code = _go_code_only(text)
    rows: list[tuple[str, str]] = []
    rows.extend((name, "free-func") for name in _GO_FREE_FUNC.findall(code))
    rows.extend((name, "method") for name in _GO_METHOD.findall(code))
    rows.extend((name, "type") for name in _GO_TYPE.findall(code))
    rows.extend((name, kind) for kind, name in _GO_VALUE.findall(code))
    return sorted({(name, kind) for name, kind in rows if len(name) >= 3 and name not in _GO_PREDECLARED})


def _unique_symbol_definitions(
    definitions: dict[str, list[tuple[str, str]]],
) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    for symbol, rows in definitions.items():
        unique_rows = sorted(set(rows))
        if len(unique_rows) == 1:
            result[symbol] = unique_rows[0]
    return result


def _symbol_references(code: str, definitions: dict[str, tuple[str, str]], *, exclude_path: str) -> dict[str, list[tuple[str, str]]]:
    by_target: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for symbol, (target, kind) in sorted(definitions.items()):
        if target == exclude_path:
            continue
        if re.search(rf"\b{re.escape(symbol)}\b", code):
            by_target[target].append((symbol, kind))
    return {target: rows for target, rows in by_target.items()}


def _unique_top_partner(counts: dict[str, int], *, minimum: int = 2) -> str | None:
    if not counts:
        return None
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    if ordered[0][1] < minimum:
        return None
    if len(ordered) > 1 and ordered[0][1] == ordered[1][1]:
        return None
    return ordered[0][0]


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
    prod_by_dir: dict[str, list[str]] = defaultdict(list)
    definitions_by_dir_package: dict[tuple[str, str], dict[str, list[tuple[str, str]]]] = defaultdict(lambda: defaultdict(list))

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
        code = _go_code_only(text)
        go_rows[rel] = {
            "text": text,
            "code": code,
            "package": package,
            "directory": directory,
            "isTest": is_test,
        }
        if not is_test:
            prod_by_dir_package[(directory, package)].append(rel)
            prod_by_dir[directory].append(rel)
            for symbol, kind in _go_top_level_declarations(text):
                definitions_by_dir_package[(directory, package)][symbol].append((rel, kind))

    for key in prod_by_dir_package:
        prod_by_dir_package[key].sort()
    for directory in prod_by_dir:
        prod_by_dir[directory].sort()

    unique_by_package = {
        key: _unique_symbol_definitions(definitions)
        for key, definitions in definitions_by_dir_package.items()
    }
    unique_by_dir: dict[str, dict[str, tuple[str, str]]] = {}
    for directory in sorted(prod_by_dir):
        merged: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for (candidate_dir, _package), definitions in definitions_by_dir_package.items():
            if candidate_dir != directory:
                continue
            for symbol, rows in definitions.items():
                merged[symbol].extend(rows)
        unique_by_dir[directory] = _unique_symbol_definitions(merged)

    same_package_refs: dict[str, dict[str, list[tuple[str, str]]]] = {}
    prod_reference_counts: dict[str, dict[str, int]] = defaultdict(dict)
    for rel, info in sorted(go_rows.items()):
        key = (str(info["directory"]), str(info["package"]))
        refs = _symbol_references(str(info["code"]), unique_by_package.get(key, {}), exclude_path=rel)
        same_package_refs[rel] = refs
        if not info["isTest"]:
            prod_reference_counts[rel] = {
                target: len({symbol for symbol, _kind in rows})
                for target, rows in refs.items()
                if target != rel
            }

    top_partner = {
        rel: _unique_top_partner(counts)
        for rel, counts in prod_reference_counts.items()
    }

    for rel, info in sorted(go_rows.items()):
        directory = str(info["directory"])
        package = str(info["package"])
        code = str(info["code"])
        refs = same_package_refs.get(rel, {})

        if info["isTest"]:
            stem_target = rel[: -len("_test.go")] + ".go"
            if stem_target in file_paths:
                edges.add((
                    rel,
                    stem_target,
                    "go-test-companion",
                    f"parsed-go-same-basename-test:{Path(stem_target).name}",
                ))
        else:
            for target, symbols in sorted(refs.items()):
                for symbol, kind in sorted(set(symbols)):
                    if kind in {"free-func", "var", "const"}:
                        edges.add((
                            rel,
                            target,
                            "go-symbol-exact",
                            f"parsed-go-unique-top-level-symbol:{symbol}|kind:{kind}",
                        ))

            partner = top_partner.get(rel)
            if partner and top_partner.get(partner) == rel:
                forward_symbols = sorted({symbol for symbol, _kind in refs.get(partner, [])})
                reverse_symbols = sorted({
                    symbol
                    for symbol, _kind in same_package_refs.get(partner, {}).get(rel, [])
                })
                if len(forward_symbols) >= 2 and len(reverse_symbols) >= 2:
                    edges.add((
                        rel,
                        partner,
                        "go-mutual-file-cohesion",
                        "parsed-go-mutual-top-partner:"
                        f"forward={len(forward_symbols)}|reverse={len(reverse_symbols)}|"
                        f"symbols={','.join(forward_symbols[:6])}",
                    ))

            for target, symbols in sorted(refs.items()):
                suppressed = sorted({
                    symbol
                    for symbol, kind in symbols
                    if kind in {"method", "type"}
                })
                if suppressed and not any(
                    edge[0] == rel and edge[1] == target and edge[2] == "go-mutual-file-cohesion"
                    for edge in edges
                ):
                    unresolved.append({
                        "from": rel,
                        "specifier": target,
                        "language": "go",
                        "reason": "same-package-method-or-type-reference-not-specific-enough-for-file-impact",
                        "evidence": suppressed[:8],
                    })

        for explicit_alias, spec in _go_import_entries(str(info["text"])):
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
            targets = prod_by_dir.get(target_dir, [])
            if not targets:
                unresolved.append({
                    "from": rel,
                    "specifier": spec,
                    "language": "go",
                    "reason": "local-go-module-import-not-resolved-to-repository-package",
                    "evidence": f"go-module:{module_path}",
                })
                continue

            alias = explicit_alias or Path(spec).name
            if alias in {"_", "."}:
                unresolved.append({
                    "from": rel,
                    "specifier": spec,
                    "language": "go",
                    "reason": "local-go-blank-or-dot-import-not-file-resolved",
                    "evidence": f"go-module:{module_path}|alias:{alias}",
                })
                continue

            observed = sorted(set(re.findall(rf"\b{re.escape(alias)}\.([A-Za-z_][A-Za-z0-9_]*)\b", code)))
            resolved_symbols = 0
            dir_definitions = unique_by_dir.get(target_dir, {})
            for symbol in observed:
                target_row = dir_definitions.get(symbol)
                if target_row is None:
                    unresolved.append({
                        "from": rel,
                        "specifier": f"{spec}:{symbol}",
                        "language": "go",
                        "reason": "local-go-qualified-symbol-not-resolved",
                        "evidence": f"go-module:{module_path}|alias:{alias}",
                    })
                    continue
                target, kind = target_row
                if target == rel:
                    continue
                edges.add((
                    rel,
                    target,
                    "go-import-symbol",
                    f"parsed-go-local-qualified-symbol:{alias}.{symbol}|kind:{kind}|module:{module_path}",
                ))
                resolved_symbols += 1

            if not observed:
                if len(targets) == 1 and targets[0] != rel:
                    edges.add((
                        rel,
                        targets[0],
                        "go-import-single-file-package",
                        f"parsed-go-local-single-file-package:{spec}|module:{module_path}",
                    ))
                else:
                    unresolved.append({
                        "from": rel,
                        "specifier": spec,
                        "language": "go",
                        "reason": "local-go-package-import-not-file-specific-enough",
                        "evidence": f"go-module:{module_path}|candidateFiles:{len(targets)}",
                    })
            elif resolved_symbols == 0:
                unresolved.append({
                    "from": rel,
                    "specifier": spec,
                    "language": "go",
                    "reason": "local-go-package-import-has-no-resolved-qualified-symbols",
                    "evidence": f"go-module:{module_path}|observedSymbols:{len(observed)}",
                })

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
