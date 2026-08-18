from __future__ import annotations

import fnmatch
import json
import posixpath
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from .common import unique
from .language_dependencies import bounded_language_dependency_edges

IMPORT_PY = re.compile(r"^\s*(?:from\s+([A-Za-z0-9_\.]+)\s+import|import\s+([A-Za-z0-9_\.]+))", re.M)
IMPORT_JS = re.compile(
    r"(?:from\s+|require\(\s*|import\(\s*|(?:^|[;\n])\s*import\s*)[\"']([^\"']+)[\"']",
    re.M,
)
RUST_MOD = re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?mod\s+([A-Za-z_][A-Za-z0-9_]*)\s*;", re.M)
RUST_USE = re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?use\s+([^;]+);", re.M)
RUST_PATH_MOD = re.compile(
    r"#\s*\[\s*path\s*=\s*[\"']([^\"']+)[\"']\s*\]\s*(?:pub(?:\([^)]*\))?\s+)?mod\s+([A-Za-z_][A-Za-z0-9_]*)\s*;",
    re.M,
)
JS_RESOLVE_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts", ".json")

def _safe_text(repo: Path, rel: str, max_bytes: int = 600_000) -> str:
    path = repo / rel
    try:
        if not path.is_file() or path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""

def _python_module_map(files: list[dict[str, Any]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in files:
        rel = str(row.get("path") or "")
        if not rel.endswith(".py"):
            continue
        parts = Path(rel).with_suffix("").parts
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        if parts:
            out[".".join(parts)] = rel
            if "src" in parts:
                idx = parts.index("src") + 1
                if idx < len(parts):
                    out[".".join(parts[idx:])] = rel
    return out

def _normalize_relative_candidate(base: Path, spec: str) -> str | None:
    raw = (base / spec).as_posix()
    normalized = posixpath.normpath(raw)
    if normalized in {"", ".", ".."} or normalized.startswith("../") or normalized.startswith("/"):
        return None
    return normalized


def _resolve_js_relative(file_paths: set[str], base: Path, spec: str) -> str | None:
    raw = _normalize_relative_candidate(base, spec)
    if not raw:
        return None
    candidates = [raw]
    candidates.extend(raw + suffix for suffix in JS_RESOLVE_SUFFIXES)
    candidates.extend(raw + "/index" + suffix for suffix in JS_RESOLVE_SUFFIXES)
    return next((candidate for candidate in candidates if candidate in file_paths), None)


def _rust_module_location(rel: str) -> tuple[str, str] | None:
    path = Path(rel)
    if path.suffix.lower() != ".rs":
        return None
    parts = list(path.parts)
    src_positions = [idx for idx, part in enumerate(parts) if part == "src"]
    if not src_positions:
        return None
    idx = src_positions[-1]
    root = Path(*parts[: idx + 1]).as_posix()
    tail = list(parts[idx + 1 :])
    if not tail:
        return None
    if tail[-1] in {"lib.rs", "main.rs"}:
        module_parts = tail[:-1]
    elif tail[-1] == "mod.rs":
        module_parts = tail[:-1]
    else:
        module_parts = [*tail[:-1], Path(tail[-1]).stem]
    return root, "::".join(module_parts)


def _rust_module_map(file_paths: set[str]) -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for rel in sorted(file_paths):
        location = _rust_module_location(rel)
        if location:
            result[location] = rel
    return result


def _rust_resolve_use(
    module_map: dict[tuple[str, str], str],
    root: str,
    current_module: str,
    expression: str,
) -> tuple[str | None, str]:
    expr = expression.strip()
    expr = re.sub(r"\s+as\s+[A-Za-z_][A-Za-z0-9_]*\s*$", "", expr)
    if "{" in expr or "*" in expr:
        return None, "ambiguous-group-or-glob-use"
    parts = [part.strip() for part in expr.split("::") if part.strip()]
    if not parts:
        return None, "empty-use"
    current = [part for part in current_module.split("::") if part]
    if parts[0] == "crate":
        module_parts = parts[1:]
    elif parts[0] == "self":
        module_parts = current + parts[1:]
    elif parts[0] == "super":
        module_parts = current[:-1] + parts[1:]
    else:
        return None, "external-or-unqualified-use"
    for end in range(len(module_parts), 0, -1):
        key = (root, "::".join(module_parts[:end]))
        target = module_map.get(key)
        if target:
            return target, "resolved-local-module-prefix"
    return None, "unresolved-local-module"


def dependency_graph(repo_root: str | Path, inventory: dict[str, Any]) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    files = inventory.get("files") or []
    file_paths = {str(row.get("path")) for row in files if row.get("path")}
    module_map = _python_module_map(files)
    rust_modules = _rust_module_map(file_paths)
    edges: set[tuple[str, str, str, str]] = set()
    unresolved: list[dict[str, Any]] = []
    for row in files:
        rel = str(row.get("path") or "")
        if not row.get("isText") or row.get("sensitiveName"):
            continue
        text = _safe_text(repo, rel)
        if not text:
            continue
        if rel.endswith(".py"):
            for match in IMPORT_PY.finditer(text):
                module = match.group(1) or match.group(2) or ""
                target = module_map.get(module)
                if not target:
                    target = next((path for key, path in module_map.items() if module.startswith(key + ".")), None)
                if target and target != rel:
                    edges.add((rel, target, "imports", "parsed-python-import"))
        elif Path(rel).suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts"}:
            base = Path(rel).parent
            for spec in IMPORT_JS.findall(text):
                if not spec.startswith("."):
                    continue
                target = _resolve_js_relative(file_paths, base, spec)
                if target and target != rel:
                    edges.add((rel, target, "imports", f"parsed-js-relative:{spec}"))
                elif target is None:
                    unresolved.append({
                        "from": rel,
                        "specifier": spec,
                        "language": "javascript-typescript",
                        "reason": "relative-import-not-resolved-from-repository-facts",
                    })
        elif rel.endswith(".rs"):
            location = _rust_module_location(rel)
            if not location:
                unresolved.append({
                    "from": rel,
                    "specifier": None,
                    "language": "rust",
                    "reason": "rust-source-outside-src-module-convention",
                })
                continue
            root, current_module = location
            for path_spec, _name in RUST_PATH_MOD.findall(text):
                target = _normalize_relative_candidate(Path(rel).parent, path_spec)
                if target and target in file_paths and target != rel:
                    edges.add((rel, target, "rust-path-module", f"parsed-rust-path:{path_spec}"))
                else:
                    unresolved.append({
                        "from": rel,
                        "specifier": path_spec,
                        "language": "rust",
                        "reason": "rust-path-module-not-resolved",
                    })
            current_parts = [part for part in current_module.split("::") if part]
            for name in RUST_MOD.findall(text):
                target_module = "::".join([*current_parts, name])
                target = rust_modules.get((root, target_module))
                if target and target != rel:
                    edges.add((rel, target, "rust-mod", f"parsed-rust-mod:{name}"))
                else:
                    unresolved.append({
                        "from": rel,
                        "specifier": name,
                        "language": "rust",
                        "reason": "rust-mod-declaration-not-resolved",
                    })
            for expression in RUST_USE.findall(text):
                target, reason = _rust_resolve_use(rust_modules, root, current_module, expression)
                if target and target != rel:
                    edges.add((rel, target, "rust-use", f"parsed-rust-use:{expression.strip()}"))
                elif reason != "external-or-unqualified-use":
                    unresolved.append({
                        "from": rel,
                        "specifier": expression.strip(),
                        "language": "rust",
                        "reason": reason,
                    })

    bounded_edges, bounded_unresolved = bounded_language_dependency_edges(repo, inventory)
    edges.update(bounded_edges)
    unresolved.extend(bounded_unresolved)

    rows = [
        {"from": a, "to": b, "type": t, "evidence": e, "confidence": "supported"}
        for a, b, t, e in sorted(edges)
    ]
    unresolved = sorted(
        unresolved,
        key=lambda row: (
            str(row.get("language") or ""),
            str(row.get("from") or ""),
            str(row.get("specifier") or ""),
            str(row.get("reason") or ""),
        ),
    )
    return {
        "nodes": sorted(file_paths),
        "edges": rows,
        "edgeCount": len(rows),
        "unresolved": unresolved,
        "unresolvedCount": len(unresolved),
        "resolutionRule": "ONLY_RESOLVE_RELATIONSHIPS_PROVABLE_FROM_REPOSITORY_PATHS_AND_BOUNDED_LANGUAGE_SYNTAX",
        "doesNotProve": [
            "Runtime or macro-generated dependencies.",
            "External package resolution unless represented as a repository-local file relationship.",
            "Go build-tag/cgo/runtime-plugin relationships not visible in bounded repository syntax.",
            "Java reflection, generated bytecode/source, dependency injection runtime wiring, or external classpath semantics.",
        ],
    }

def _parse_codeowners(repo: Path, rel: str) -> list[tuple[str, list[str]]]:
    text = _safe_text(repo, rel)
    rules: list[tuple[str, list[str]]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        rules.append((parts[0], parts[1:]))
    return rules

def ownership_graph(repo_root: str | Path, inventory: dict[str, Any]) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    paths = [str(row.get("path")) for row in inventory.get("files") or [] if row.get("path")]
    owner_files = inventory.get("ownershipFiles") or []
    edges: list[dict[str, Any]] = []
    for rel in owner_files:
        if Path(rel).name != "CODEOWNERS":
            continue
        for pattern, owners in _parse_codeowners(repo, rel):
            normalized = pattern.lstrip("/")
            for path in paths:
                if fnmatch.fnmatch(path, normalized) or fnmatch.fnmatch("/" + path, pattern):
                    for owner in owners:
                        edges.append({
                            "from": rel, "to": path, "type": "declares-owner",
                            "owner": owner, "evidence": rel, "confidence": "supported",
                        })
    return {"edges": edges, "edgeCount": len(edges), "doesNotProve": ["Ownership outside repository evidence."]}

def evidence_graph(authorities: dict[str, Any]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for row in authorities.get("candidates") or []:
        path = row.get("path")
        nodes.append({"id": path, "kind": "file", "state": row.get("state"), "sha256": row.get("contentSha256")})
        for reason in row.get("whySelected") or []:
            rid = f"reason:{reason}"
            nodes.append({"id": rid, "kind": "selection-reason"})
            edges.append({"from": rid, "to": path, "type": "supports-selection", "confidence": "supported"})
        for decl in row.get("declarations") or []:
            source = decl.get("declarationFile")
            edges.append({"from": source, "to": path, "type": "declares-authority", "scope": decl.get("scope"), "confidence": "supported"})
    dedup = {json.dumps(node, sort_keys=True): node for node in nodes}
    return {"nodes": list(dedup.values()), "edges": edges, "edgeCount": len(edges)}

def authority_graph(authorities: dict[str, Any]) -> dict[str, Any]:
    nodes = [{
        "id": row.get("path"), "state": row.get("state"), "score": row.get("score"),
        "sha256": row.get("contentSha256"),
    } for row in authorities.get("candidates") or []]
    edges: list[dict[str, Any]] = []
    for row in authorities.get("candidates") or []:
        for decl in row.get("declarations") or []:
            edges.append({
                "from": decl.get("declarationFile"), "to": row.get("path"),
                "type": "authority-declaration", "scope": decl.get("scope"),
            })
    for scope, paths in (authorities.get("conflicts") or {}).items():
        for path in paths:
            edges.append({"from": f"conflict:{scope}", "to": path, "type": "authority-conflict"})
    return {"nodes": nodes, "edges": edges, "edgeCount": len(edges)}

def _architecture_candidates(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rel = str(row.get("path") or "")
    path = Path(rel)
    parts = [part.lower() for part in path.parts]
    partset = set(parts)
    basename = path.name.lower()
    suffix = path.suffix.lower()
    candidates: dict[str, dict[str, Any]] = {}

    def add(layer: str, signal: str, weight: int) -> None:
        current = candidates.setdefault(layer, {"score": 0, "evidence": []})
        current["score"] += weight
        current["evidence"].append(signal)

    if row.get("generated") or "generated" in partset:
        add("generated", "generated-path", 6)
    if partset & {"vendor", "third_party", "third-party", "vendored"}:
        add("vendor", "vendor-path", 6)
    if partset & {"test", "tests", "__tests__", "spec", "specs", "e2e"} or basename.startswith("test_") or basename.endswith(("_test.py", ".spec.ts", ".test.ts", ".spec.js", ".test.js")):
        add("test", "test-convention", 6)
    if partset & {"docs", "doc", "documentation"} or basename in {"readme.md", "architecture.md"}:
        add("documentation", "documentation-convention", 5)
    if partset & {"examples", "example", "samples", "sample", "demo", "demos"}:
        add("example", "example-convention", 5)
    if partset & {"bench", "benches", "benchmark", "benchmarks"}:
        add("benchmark", "benchmark-convention", 5)
    if partset & {"governance", "policy", "policies", "contracts"} or basename == "codeowners" or (len(parts) >= 2 and parts[0] == ".github" and parts[1] == "workflows"):
        add("governance", "governance-convention", 5)
    if partset & {"migrations", "migration", "database", "db", "repositories", "repository"} or suffix in {".sql", ".prisma"}:
        add("persistence", "persistence-convention", 5)
    if partset & {"adapters", "adapter", "connectors", "connector", "webhooks", "clients", "integrations", "integration", "api"}:
        add("integration", "integration-convention", 4)
    if partset & {"infra", "infrastructure", "deploy", "deployment", "terraform", "k8s", "helm", "docker"} or basename.startswith("dockerfile"):
        add("infrastructure", "infrastructure-convention", 5)
    if partset & {"components", "views", "pages", "templates", "styles"} or suffix in {".css", ".scss", ".jsx", ".tsx"}:
        add("ui", "ui-convention", 3)
    if partset & {"domain", "entities", "entity", "business"}:
        add("domain", "domain-convention", 4)
    if partset & {"handlers", "controllers", "commands", "queries", "usecase", "usecases", "application"}:
        add("application", "application-convention", 4)
    if partset & {"cli", "cmd", "bin"}:
        add("entrypoint", "cli-entrypoint-convention", 4)
    if basename in {"package.json", "pyproject.toml", "cargo.toml", "go.mod", "pom.xml", "build.gradle", "build.gradle.kts"}:
        add("package", "package-manifest", 5)
    if partset & {"config", "configs", ".config"} or basename.endswith((".config.js", ".config.ts", ".config.mjs")):
        add("configuration", "configuration-convention", 4)
    if "src" in partset or "lib" in partset:
        add("source", "generic-source-region", 1)
    return candidates


def architecture_layer_graph(inventory: dict[str, Any]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    for row in inventory.get("files") or []:
        rel = str(row.get("path") or "")
        candidates = _architecture_candidates(row)
        ordered = sorted(
            ((layer, data["score"], sorted(set(data["evidence"]))) for layer, data in candidates.items()),
            key=lambda item: (-item[1], item[0]),
        )
        if not ordered:
            layer, confidence, selected_evidence = "unclassified", "unknown", []
        elif len(ordered) > 1 and ordered[0][1] == ordered[1][1]:
            layer, confidence, selected_evidence = "unclassified", "unknown", []
        else:
            layer = ordered[0][0]
            confidence = "supported" if ordered[0][1] >= 5 else "inferred"
            selected_evidence = ordered[0][2]
        nodes.append({
            "path": rel,
            "layer": layer,
            "confidence": confidence,
            "evidence": selected_evidence,
            "candidateLayers": [
                {"layer": candidate, "score": score, "evidence": evidence}
                for candidate, score, evidence in ordered
            ],
            "classificationRule": "PORTABLE_STRUCTURAL_EVIDENCE_ONLY_NO_AUTHORIZATION",
            "doesNotProve": [
                "Runtime call order or architectural intent beyond repository evidence.",
                "Authorization to edit this path.",
            ],
        })
    layer_counts = {
        layer: sum(1 for row in nodes if row["layer"] == layer)
        for layer in sorted({row["layer"] for row in nodes})
    }
    unclassified = layer_counts.get("unclassified", 0)
    total = len(nodes)
    return {
        "schemaVersion": "code_atlas_architecture_layer_graph.v2",
        "name": "Architecture Layer Graph",
        "nodes": nodes,
        "layerCounts": layer_counts,
        "coverage": {
            "totalFiles": total,
            "classifiedFiles": total - unclassified,
            "unclassifiedFiles": unclassified,
            "classifiedPercent": round(100 * (total - unclassified) / max(1, total), 4),
            "supported": sum(1 for row in nodes if row["confidence"] == "supported"),
            "inferred": sum(1 for row in nodes if row["confidence"] == "inferred"),
            "unknown": sum(1 for row in nodes if row["confidence"] == "unknown"),
        },
        "authorizationRule": "ARCHITECTURE_CLASSIFICATION_NEVER_EXPANDS_ALLOWED_SCOPE",
    }

def test_intelligence(inventory: dict[str, Any], dependencies: dict[str, Any]) -> dict[str, Any]:
    tests = set(inventory.get("testFiles") or [])
    reverse: dict[str, set[str]] = defaultdict(set)
    for edge in dependencies.get("edges") or []:
        reverse[str(edge.get("to"))].add(str(edge.get("from")))
    rows = []
    for test in sorted(tests):
        direct = sorted(edge["to"] for edge in dependencies.get("edges") or [] if edge.get("from") == test)
        rows.append({
            "test": test,
            "directDependencies": direct,
            "coverageClass": "STRUCTURAL_REFERENCE_ONLY",
            "doesNotProve": ["Runtime behavior, assertion quality, or test completeness."],
        })
    return {"tests": rows, "testCount": len(rows), "productionCertified": False}


def _is_go_actionable_direct_edge(edge: dict[str, Any]) -> bool:
    edge_type = str(edge.get("type") or "")
    evidence = str(edge.get("evidence") or "")
    if edge_type == "go-symbol-exact":
        return True
    if edge_type == "go-import-symbol":
        return "|kind:type|" not in evidence and "|kind:method|" not in evidence
    return False


def _go_actionable_review(
    changed: set[str],
    impacted: set[str],
    dependencies: dict[str, Any],
) -> dict[str, Any]:
    direct_reverse: dict[str, set[str]] = defaultdict(set)
    companion_reverse: dict[str, set[str]] = defaultdict(set)
    for edge in dependencies.get("edges") or []:
        source = str(edge.get("from") or "")
        target = str(edge.get("to") or "")
        if not source or not target:
            continue
        if _is_go_actionable_direct_edge(edge):
            direct_reverse[target].add(source)
        elif edge.get("type") == "go-test-companion":
            companion_reverse[target].add(source)

    direct = {
        source
        for target in changed
        for source in direct_reverse.get(target, set())
        if source in impacted
    }
    actionable = set(changed) | direct
    test_companions: set[str] = set()
    frontier = list(actionable)
    while frontier:
        current = frontier.pop()
        for companion in companion_reverse.get(current, set()):
            if companion not in impacted or companion in actionable:
                continue
            actionable.add(companion)
            test_companions.add(companion)
            frontier.append(companion)

    structural_only = impacted - actionable
    return {
        "schemaVersion": "code_atlas_actionable_review.v1",
        "scope": "GO_BOUNDED_V1",
        "paths": sorted(actionable),
        "directDependencies": sorted(direct),
        "testCompanions": sorted(test_companions),
        "structuralOnlyImpacted": sorted(structural_only),
        "rule": "CHANGED_PLUS_DIRECT_EXACT_GO_REVERSE_DEPENDENCIES_PLUS_TEST_COMPANION_CLOSURE",
        "authorizationRule": "ACTIONABLE_REVIEW_NEVER_EXPANDS_ALLOWED_SCOPE",
        "doesNotProve": [
            "Authorization to edit any impacted or actionable path.",
            "Completeness outside bounded repository-proven Go relationships.",
            "That structural-only impacted paths are safe to ignore.",
        ],
    }


def change_impact(changed_paths: list[str], dependencies: dict[str, Any], ownership: dict[str, Any]) -> dict[str, Any]:
    changed = set(changed_paths)
    reverse: dict[str, set[str]] = defaultdict(set)
    for edge in dependencies.get("edges") or []:
        reverse[str(edge.get("to"))].add(str(edge.get("from")))
    impacted = set(changed)
    frontier = list(changed)
    while frontier:
        current = frontier.pop()
        for dep in reverse.get(current, set()):
            if dep not in impacted:
                impacted.add(dep)
                frontier.append(dep)
    owners = sorted({
        str(edge.get("owner"))
        for edge in ownership.get("edges") or []
        if edge.get("to") in impacted and edge.get("owner")
    })
    return {
        "changed": sorted(changed),
        "impacted": sorted(impacted),
        "owners": owners,
        "impactRule": "STATIC_GRAPH_TRANSITIVE_REVERSE_DEPENDENCY",
        "actionableReview": _go_actionable_review(changed, impacted, dependencies),
        "doesNotProve": ["Runtime dynamic dependencies not present in repository evidence."],
    }

def build_system_graphs(
    repo_root: str | Path,
    inventory: dict[str, Any],
    authorities: dict[str, Any],
    *,
    changed_paths: list[str] | None = None,
) -> dict[str, Any]:
    deps = dependency_graph(repo_root, inventory)
    owners = ownership_graph(repo_root, inventory)
    return {
        "schemaVersion": "code_atlas_system_graphs.v1",
        "authorityGraph": authority_graph(authorities),
        "evidenceGraph": evidence_graph(authorities),
        "dependencyGraph": deps,
        "ownershipGraph": owners,
        "architectureLayerGraph": architecture_layer_graph(inventory),
        "testIntelligence": test_intelligence(inventory, deps),
        "changeImpact": change_impact(changed_paths or [], deps, owners),
        "visualLayerMap": None,
        "visualLayerMapRule": "SEPARATE_OPTIONAL_ARTIFACT_NOT_ARCHITECTURE_GRAPH",
        "productionCertified": False,
    }