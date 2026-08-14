from __future__ import annotations

import fnmatch
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from .common import unique

IMPORT_PY = re.compile(r"^\s*(?:from\s+([A-Za-z0-9_\.]+)\s+import|import\s+([A-Za-z0-9_\.]+))", re.M)
IMPORT_JS = re.compile(r"(?:from\s+|require\(\s*|import\(\s*)[\"']([^\"']+)[\"']")
LAYER_RULES = [
    ("governance", ("governance", "policy", "contract", "docs/architecture", "codeowners", ".github/workflows")),
    ("ui", ("components", "views", "pages", "templates", "styles", ".css", ".scss", ".tsx", ".jsx")),
    ("application", ("application", "usecase", "use-case", "handlers", "controllers", "commands", "queries")),
    ("domain", ("domain", "entities", "models", "business", "core")),
    ("persistence", ("database", "db", "repository", "repositories", "migrations", ".sql", ".prisma")),
    ("integration", ("integration", "clients", "adapters", "connectors", "webhooks", "api")),
    ("infrastructure", ("infra", "deploy", "docker", "terraform", "k8s", "helm", "workflow")),
]

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

def dependency_graph(repo_root: str | Path, inventory: dict[str, Any]) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    files = inventory.get("files") or []
    file_paths = {str(row.get("path")) for row in files if row.get("path")}
    module_map = _python_module_map(files)
    edges: set[tuple[str, str, str, str]] = set()
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
                    edges.add((rel, target, "imports", "parsed"))
        elif Path(rel).suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
            base = Path(rel).parent
            for spec in IMPORT_JS.findall(text):
                if not spec.startswith("."):
                    continue
                raw = (base / spec).as_posix()
                candidates = [
                    raw, raw + ".ts", raw + ".tsx", raw + ".js", raw + ".jsx",
                    raw + "/index.ts", raw + "/index.tsx", raw + "/index.js", raw + "/index.jsx",
                ]
                target = next((c for c in candidates if c in file_paths), None)
                if target and target != rel:
                    edges.add((rel, target, "imports", "parsed"))
    rows = [
        {"from": a, "to": b, "type": t, "evidence": e, "confidence": "supported"}
        for a, b, t, e in sorted(edges)
    ]
    return {"nodes": sorted(file_paths), "edges": rows, "edgeCount": len(rows)}

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

def architecture_layer_graph(inventory: dict[str, Any]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    for row in inventory.get("files") or []:
        rel = str(row.get("path") or "")
        low = rel.lower()
        scores: dict[str, int] = {}
        evidence: dict[str, list[str]] = defaultdict(list)
        for layer, signals in LAYER_RULES:
            for signal in signals:
                if signal in low:
                    scores[layer] = scores.get(layer, 0) + 1
                    evidence[layer].append(signal)
        if not scores:
            layer, confidence = "unclassified", "unknown"
            selected_evidence: list[str] = []
        else:
            ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
            layer = ordered[0][0]
            confidence = "supported" if ordered[0][1] >= 2 else "inferred"
            selected_evidence = sorted(set(evidence[layer]))
        nodes.append({
            "path": rel, "layer": layer, "confidence": confidence,
            "evidence": selected_evidence,
            "doesNotProve": ["Runtime call order or architectural intent beyond repository evidence."],
        })
    return {
        "schemaVersion": "code_atlas_architecture_layer_graph.v1",
        "name": "Architecture Layer Graph",
        "nodes": nodes,
        "layerCounts": {
            layer: sum(1 for row in nodes if row["layer"] == layer)
            for layer in sorted({row["layer"] for row in nodes})
        },
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
