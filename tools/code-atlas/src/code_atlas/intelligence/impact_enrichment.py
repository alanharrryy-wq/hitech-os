from __future__ import annotations

import hashlib
import json
import posixpath
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

from .common import run_git, safe_repo_relative

_C_FAMILY_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
_BASE_STATIC_SUFFIXES = {
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts",
    ".go", ".java", ".rs", *_C_FAMILY_SUFFIXES,
}
_STRUCTURED_SUFFIXES = {".json", ".jsonc", ".yaml", ".yml", ".toml", ".md", ".graphql", ".gql", ".prisma"}
_RECOGNIZED_BUT_UNSUPPORTED_SUFFIXES = {".cs", ".rb", ".php", ".swift", ".scala"}
_INCLUDE_RE = re.compile(r"(?m)^\s*#\s*include\s*([<\"])([^>\"\n]+)[>\"]")
_QUOTED_OR_TICK_RE = re.compile(r"(?:[\"'`])([^\"'`\r\n]{1,300})(?:[\"'`])")
_TEST_HINT_RE = re.compile(r"(?:^|/)(?:test|tests|spec|specs|e2e)(?:/|$)|(?:^|/)(?:test[_-]|.*(?:[._-](?:test|spec)))", re.I)


def _canonical_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _safe_text(repo: Path, rel: str, *, max_bytes: int = 600_000) -> str:
    path = repo / rel
    try:
        if not path.is_file() or path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _existing_file_paths(inventory: dict[str, Any]) -> set[str]:
    return {
        str(row.get("path"))
        for row in inventory.get("files") or []
        if row.get("path") and row.get("exists", True)
    }


def _resolve_repo_candidate(base: Path, spec: str, file_paths: set[str]) -> str | None:
    normalized = posixpath.normpath((base / spec).as_posix())
    if normalized not in {"", ".", ".."} and not normalized.startswith("../") and not normalized.startswith("/"):
        if normalized in file_paths:
            return normalized
    spec_norm = posixpath.normpath(spec.replace("\\", "/")).lstrip("./")
    if not spec_norm or spec_norm.startswith("../"):
        return None
    matches = sorted(path for path in file_paths if path == spec_norm or path.endswith("/" + spec_norm))
    return matches[0] if len(matches) == 1 else None


def _c_family_include_relations(repo: Path, inventory: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    file_paths = _existing_file_paths(inventory)
    relations: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    for rel in sorted(path for path in file_paths if Path(path).suffix.lower() in _C_FAMILY_SUFFIXES):
        text = _safe_text(repo, rel)
        if not text:
            continue
        base = Path(rel).parent
        for opener, raw_spec in _INCLUDE_RE.findall(text):
            spec = raw_spec.strip()
            target = _resolve_repo_candidate(base, spec, file_paths)
            if target and target != rel:
                relations.append({
                    "from": rel,
                    "to": target,
                    "type": "c-family-include",
                    "supportLevel": "SUPPORTED",
                    "disposition": "STATIC_DEPENDENCY",
                    "evidence": {
                        "kind": "parsed-local-include",
                        "specifier": spec,
                        "delimiter": "quote" if opener == '"' else "angle",
                        "resolution": "repository-existing-unique-path",
                    },
                })
            elif opener == '"' or "/" in spec or spec.startswith("."):
                unknown.append({
                    "from": rel,
                    "to": None,
                    "type": "c-family-include",
                    "supportLevel": "UNKNOWN",
                    "disposition": "UNRESOLVED",
                    "reason": "LOCAL_LOOKING_INCLUDE_NOT_RESOLVED_TO_UNIQUE_REPOSITORY_PATH",
                    "specifier": spec,
                })
    return relations, unknown


def _normalized_test_stem(path: str) -> str:
    stem = Path(path).stem
    lowered = stem.lower()
    if lowered.startswith("test_"):
        stem = stem[5:]
    for suffix in (".test", ".spec", "_test", "_spec", "-test", "-spec"):
        if stem.lower().endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return stem.lower()


def _typed_companion_relations(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    file_paths = _existing_file_paths(inventory)
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for rel in sorted(file_paths):
        suffix = Path(rel).suffix.lower()
        if suffix not in _BASE_STATIC_SUFFIXES:
            continue
        directory = Path(rel).parent.as_posix()
        if directory == ".":
            directory = ""
        groups[(directory, _normalized_test_stem(rel))].append(rel)

    relations: list[dict[str, Any]] = []
    for (_directory, stem), rows in sorted(groups.items()):
        rows = sorted(set(rows))
        if len(rows) < 2 or len(rows) > 8:
            continue
        has_test_signal = any(_TEST_HINT_RE.search(path) for path in rows)
        suffixes = {Path(path).suffix.lower() for path in rows}
        cross_language = len(suffixes) > 1
        if not has_test_signal or not cross_language:
            continue
        for left in rows:
            for right in rows:
                if left >= right:
                    continue
                relations.append({
                    "from": left,
                    "to": right,
                    "type": "typed-test-companion",
                    "supportLevel": "SUPPORTED",
                    "disposition": "COMPANION",
                    "evidence": {
                        "kind": "same-directory-normalized-test-stem",
                        "normalizedStem": stem,
                        "extensions": sorted({Path(left).suffix.lower(), Path(right).suffix.lower()}),
                    },
                })
    return relations


def _is_structured_relation_source(rel: str) -> bool:
    path = Path(rel)
    suffix = path.suffix.lower()
    if suffix in {".graphql", ".gql", ".prisma"}:
        return True
    parts = {part.lower() for part in path.parts}
    if parts & {"config", "configs", "contract", "contracts", "api", "apis", "schema", "schemas", "openapi"}:
        return True
    name = path.name.lower()
    return any(token in name for token in ("contract", "config", "schema", "openapi", "api"))


def _structured_reference_relations(repo: Path, inventory: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    file_paths = _existing_file_paths(inventory)
    relations: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    for rel in sorted(
        path for path in file_paths
        if Path(path).suffix.lower() in _STRUCTURED_SUFFIXES and _is_structured_relation_source(path)
    ):
        text = _safe_text(repo, rel, max_bytes=350_000)
        if not text:
            continue
        base = Path(rel).parent
        seen: set[tuple[str, str]] = set()
        for raw in _QUOTED_OR_TICK_RE.findall(text):
            token = raw.strip().replace("\\", "/")
            if not token or len(token) > 260 or token.startswith(("http://", "https://")):
                continue
            if "/" not in token and Path(token).suffix.lower() not in _BASE_STATIC_SUFFIXES | _STRUCTURED_SUFFIXES:
                continue
            target = _resolve_repo_candidate(base, token, file_paths)
            if target and target != rel and (rel, target) not in seen:
                seen.add((rel, target))
                relations.append({
                    "from": rel,
                    "to": target,
                    "type": "structured-path-reference",
                    "supportLevel": "SUPPORTED",
                    "disposition": "STATIC_REFERENCE",
                    "evidence": {
                        "kind": "exact-structured-repository-path",
                        "literal": token,
                        "sourceSuffix": Path(rel).suffix.lower(),
                    },
                })
            elif token.startswith(("../", "./")) and not target:
                unknown.append({
                    "from": rel,
                    "to": None,
                    "type": "structured-path-reference",
                    "supportLevel": "UNKNOWN",
                    "disposition": "UNRESOLVED",
                    "reason": "RELATIVE_STRUCTURED_PATH_NOT_RESOLVED",
                    "specifier": token,
                })
    return relations, unknown


_QUERY_STOPWORDS = {
    "about", "after", "again", "allow", "before", "change", "changing", "could", "from", "have",
    "into", "only", "repository", "should", "that", "their", "there", "these", "this", "those", "under",
    "using", "when", "where", "which", "while", "with", "without", "would",
}


def _query_terms(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", value.lower())
        if token not in _QUERY_STOPWORDS
    }


def _relation_candidate_score(repo: Path, path: str, query_terms: set[str]) -> tuple[int, str]:
    if not query_terms:
        return 0, path
    lowered_path = path.lower()
    path_hits = sum(1 for term in query_terms if term in lowered_path)
    text = _safe_text(repo, path, max_bytes=120_000).lower()
    content_hits = sum(min(3, text.count(term)) for term in query_terms) if text else 0
    test_bonus = 2 if _TEST_HINT_RE.search(path) else 0
    header_bonus = 1 if Path(path).suffix.lower() in {".h", ".hh", ".hpp", ".hxx"} else 0
    return path_hits * 6 + content_hits + test_bonus + header_bonus, path


def _bounded_reverse_relations(
    repo: Path,
    reverse: dict[str, list[dict[str, Any]]],
    current: str,
    query_terms: set[str],
    *,
    max_fanout: int = 12,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = list(reverse.get(current, []))
    if len(rows) <= max_fanout:
        return rows, []
    ranked = sorted(
        ((_relation_candidate_score(repo, str(row.get("from") or ""), query_terms), row) for row in rows),
        key=lambda item: (-item[0][0], item[0][1], str(item[1].get("type"))),
    )
    selected = [row for (score, _path), row in ranked[:max_fanout] if score > 0]
    if not selected:
        selected = [row for (_score, _path), row in ranked[: min(4, max_fanout)]]
    selected_ids = {id(row) for row in selected}
    deferred = [row for (_rank, row) in ranked if id(row) not in selected_ids]
    return selected, deferred


def _base_dependency_relations(graphs: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for edge in (graphs.get("dependencyGraph") or {}).get("edges") or []:
        source = str(edge.get("from") or "")
        target = str(edge.get("to") or "")
        if not source or not target:
            continue
        confidence = str(edge.get("confidence") or "supported").lower()
        support = "SUPPORTED" if confidence == "supported" else "INFERRED" if confidence == "inferred" else "UNKNOWN"
        rows.append({
            "from": source,
            "to": target,
            "type": str(edge.get("type") or "dependency"),
            "supportLevel": support,
            "disposition": "STATIC_DEPENDENCY",
            "evidence": edge.get("provenance") or edge.get("evidence") or {
                "kind": "dependency-graph-edge",
                "sourceGraph": "dependencyGraph",
            },
        })
    return rows


def _historical_cochange_relations(
    repo: Path,
    changed: set[str],
    file_paths: set[str],
    *,
    max_commits: int = 160,
    max_files_per_commit: int = 80,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not changed:
        return [], []
    code, out, err = run_git(repo, "log", f"-n{max_commits}", "--format=@@%H", "--name-only", "--no-renames")
    if code != 0:
        return [], [{
            "type": "historical-cochange",
            "supportLevel": "UNKNOWN",
            "disposition": "UNRESOLVED",
            "reason": "GIT_HISTORY_UNAVAILABLE",
            "detail": err.strip()[:500],
        }]

    commits: list[tuple[str, list[str]]] = []
    current_sha: str | None = None
    current_paths: list[str] = []
    for raw in out.splitlines():
        line = raw.strip()
        if line.startswith("@@"):
            if current_sha is not None:
                commits.append((current_sha, sorted(set(current_paths))))
            current_sha = line[2:]
            current_paths = []
        elif line and current_sha is not None:
            normalized = line.replace("\\", "/")
            if normalized in file_paths:
                current_paths.append(normalized)
    if current_sha is not None:
        commits.append((current_sha, sorted(set(current_paths))))

    target_hits: dict[str, int] = defaultdict(int)
    pair_hits: dict[tuple[str, str], int] = defaultdict(int)
    for _sha, paths in commits:
        if not paths or len(paths) > max_files_per_commit:
            continue
        pathset = set(paths)
        touched_targets = sorted(changed & pathset)
        for target in touched_targets:
            target_hits[target] += 1
            for peer in paths:
                if peer != target:
                    pair_hits[(target, peer)] += 1

    relations: list[dict[str, Any]] = []
    for (target, peer), count in sorted(pair_hits.items()):
        denominator = target_hits.get(target, 0)
        if denominator < 3 or count < 2:
            continue
        ratio = count / denominator
        if ratio < 0.50:
            continue
        relations.append({
            "from": peer,
            "to": target,
            "type": "historical-cochange",
            "supportLevel": "INFERRED",
            "disposition": "INSPECT_ONLY",
            "evidence": {
                "kind": "bounded-git-cochange",
                "cochangeCount": count,
                "targetHistoryCount": denominator,
                "ratio": round(ratio, 6),
                "maxCommits": max_commits,
                "maxFilesPerCommit": max_files_per_commit,
                "minimumCochangeCount": 2,
                "minimumTargetHistoryCount": 3,
                "minimumRatio": 0.50,
            },
        })
    return relations[:64], []


def _ownership_inspect_only(
    changed_or_impacted: set[str],
    graphs: dict[str, Any],
    file_paths: set[str],
) -> list[dict[str, Any]]:
    owner_to_paths: dict[str, set[str]] = defaultdict(set)
    path_to_owners: dict[str, set[str]] = defaultdict(set)
    for edge in (graphs.get("ownershipGraph") or {}).get("edges") or []:
        path = str(edge.get("to") or "")
        owner = str(edge.get("owner") or "")
        if path and owner:
            owner_to_paths[owner].add(path)
            path_to_owners[path].add(owner)

    relations: list[dict[str, Any]] = []
    for target in sorted(changed_or_impacted):
        for owner in sorted(path_to_owners.get(target, set())):
            peers = sorted(path for path in owner_to_paths.get(owner, set()) if path in file_paths and path != target)
            if len(peers) > 24:
                continue
            for peer in peers[:12]:
                relations.append({
                    "from": peer,
                    "to": target,
                    "type": "shared-codeowner",
                    "supportLevel": "INFERRED",
                    "disposition": "INSPECT_ONLY",
                    "evidence": {
                        "kind": "repository-codeowners",
                        "owner": owner,
                        "sourceGraph": "ownershipGraph",
                    },
                })
    return relations[:96]


def _architecture_evidence(path: str, graphs: dict[str, Any]) -> dict[str, Any] | None:
    for row in (graphs.get("architectureLayerGraph") or {}).get("nodes") or []:
        if str(row.get("path") or "") == path:
            return {
                "layer": row.get("layer"),
                "confidence": row.get("confidence"),
                "evidence": row.get("evidence") or [],
            }
    return None


def _authority_evidence(path: str, graphs: dict[str, Any]) -> dict[str, Any] | None:
    for row in (graphs.get("authorityGraph") or {}).get("nodes") or []:
        if str(row.get("id") or "") == path:
            return {"state": row.get("state"), "score": row.get("score"), "sha256": row.get("sha256")}
    return None


def _reason_row(
    *,
    path: str,
    kind: str,
    support_level: str,
    disposition: str,
    evidence: Any,
    source: str | None = None,
    target: str | None = None,
) -> dict[str, Any]:
    row = {
        "path": path,
        "kind": kind,
        "supportLevel": support_level,
        "disposition": disposition,
        "evidence": evidence,
    }
    if source is not None:
        row["from"] = source
    if target is not None:
        row["to"] = target
    return row


def enrich_change_impact(
    repo_root: str | Path,
    inventory: dict[str, Any],
    graphs: dict[str, Any],
    *,
    changed_paths: Iterable[str] | None = None,
    semantic_query: str = "",
) -> dict[str, Any]:
    """Enrich the canonical conservative change-impact view with bounded inspection evidence.

    The existing ``impacted`` projection remains untouched for compatibility. The V2
    inspection projection may recommend additional paths to inspect, but it never
    expands edit authorization and never turns inferred/history/ownership evidence
    into authority.
    """

    repo = Path(repo_root).resolve()
    file_paths = _existing_file_paths(inventory)
    raw_changed = list(changed_paths or [])
    changed: set[str] = set()
    for value in raw_changed:
        changed.add(safe_repo_relative(repo, value))

    impact = dict(graphs.get("changeImpact") or {})
    legacy_impacted = {str(path) for path in impact.get("impacted") or [] if str(path)}
    reasons: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unknown_rows: list[dict[str, Any]] = []

    for path in sorted(changed):
        reasons[path].append(_reason_row(
            path=path,
            kind="explicit-change-target",
            support_level="SUPPORTED" if path in file_paths else "UNKNOWN",
            disposition="CHANGE_TARGET",
            evidence={"kind": "caller-supplied-repository-relative-path", "exists": path in file_paths},
        ))
        if path not in file_paths:
            unknown_rows.append({
                "path": path,
                "type": "change-target",
                "supportLevel": "UNKNOWN",
                "disposition": "UNRESOLVED",
                "reason": "CHANGED_PATH_NOT_PRESENT_IN_REPOSITORY_INVENTORY",
            })
        elif Path(path).suffix.lower() in _RECOGNIZED_BUT_UNSUPPORTED_SUFFIXES:
            unknown_rows.append({
                "path": path,
                "type": "language-static-relations",
                "supportLevel": "UNKNOWN",
                "disposition": "UNSUPPORTED",
                "reason": "STATIC_FILE_RELATIONSHIP_PARSER_NOT_SUPPORTED_FOR_LANGUAGE",
                "suffix": Path(path).suffix.lower(),
            })

    base_relations = _base_dependency_relations(graphs)
    cpp_relations, cpp_unknown = _c_family_include_relations(repo, inventory)
    structured_relations, structured_unknown = _structured_reference_relations(repo, inventory)
    companion_relations = _typed_companion_relations(inventory)
    unknown_rows.extend(cpp_unknown)
    unknown_rows.extend(structured_unknown)

    inspection = set(legacy_impacted) | set(changed)
    for path in sorted(legacy_impacted - changed):
        reasons[path].append(_reason_row(
            path=path,
            kind="legacy-static-impact",
            support_level="SUPPORTED",
            disposition="INSPECT",
            evidence={
                "kind": "canonical-change-impact",
                "impactRule": impact.get("impactRule"),
            },
        ))

    supplemental_static = [
        row for row in [*cpp_relations, *structured_relations]
        if row.get("supportLevel") == "SUPPORTED" and row.get("from") in file_paths and row.get("to") in file_paths
    ]
    reverse: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in supplemental_static:
        reverse[str(row["to"])].append(row)
    for target in reverse:
        reverse[target] = sorted(
            reverse[target],
            key=lambda row: (str(row.get("from")), str(row.get("type")), _canonical_digest(row.get("evidence"))),
        )

    query_terms = _query_terms(semantic_query)
    deferred_static: list[dict[str, Any]] = []
    frontier: deque[str] = deque(sorted(inspection))
    expanded_static: set[str] = set()
    while frontier:
        current = frontier.popleft()
        if current in expanded_static:
            continue
        expanded_static.add(current)
        selected, deferred = _bounded_reverse_relations(repo, reverse, current, query_terms)
        deferred_static.extend(deferred)
        for relation in selected:
            source = str(relation["from"])
            reasons[source].append(_reason_row(
                path=source,
                kind=str(relation.get("type") or "static-dependency"),
                support_level="SUPPORTED",
                disposition="INSPECT",
                evidence={
                    "relation": relation.get("evidence"),
                    "boundedFanout": True,
                    "semanticQueryUsedOnlyForInspectionRanking": bool(query_terms),
                },
                source=source,
                target=current,
            ))
            if source not in inspection:
                inspection.add(source)
                frontier.append(source)

    companion_adjacency: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for relation in companion_relations:
        left, right = str(relation["from"]), str(relation["to"])
        companion_adjacency[left].append((right, relation))
        companion_adjacency[right].append((left, relation))

    expansion: deque[str] = deque(sorted(inspection))
    expanded: set[str] = set()
    while expansion:
        current = expansion.popleft()
        if current in expanded:
            continue
        expanded.add(current)
        selected, deferred = _bounded_reverse_relations(repo, reverse, current, query_terms)
        deferred_static.extend(deferred)
        for relation in selected:
            source = str(relation["from"])
            reasons[source].append(_reason_row(
                path=source,
                kind=str(relation.get("type") or "static-dependency"),
                support_level="SUPPORTED",
                disposition="INSPECT",
                evidence={
                    "relation": relation.get("evidence"),
                    "boundedFanout": True,
                    "semanticQueryUsedOnlyForInspectionRanking": bool(query_terms),
                },
                source=source,
                target=current,
            ))
            if source not in inspection:
                inspection.add(source)
                expansion.append(source)
        for peer, relation in sorted(companion_adjacency.get(current, []), key=lambda item: item[0]):
            if peer not in file_paths:
                continue
            reasons[peer].append(_reason_row(
                path=peer,
                kind="typed-test-companion",
                support_level="SUPPORTED",
                disposition="INSPECT",
                evidence=relation.get("evidence"),
                source=peer,
                target=current,
            ))
            if peer not in inspection:
                inspection.add(peer)
                expansion.append(peer)

    deferred_static_relations: list[dict[str, Any]] = []
    for relation in sorted(
        {json.dumps(row, ensure_ascii=False, sort_keys=True): row for row in deferred_static}.values(),
        key=lambda row: (str(row.get("from")), str(row.get("to")), str(row.get("type"))),
    )[:64]:
        deferred_static_relations.append({
            **relation,
            "supportLevel": "INFERRED",
            "disposition": "INSPECT_ONLY",
            "evidence": {
                "relation": relation.get("evidence"),
                "reason": "BOUNDED_STATIC_FANOUT_DEFERRED_FROM_PRIMARY_INSPECTION",
                "semanticQueryUsedOnlyForInspectionRanking": bool(query_terms),
            },
        })

    history_relations, history_unknown = _historical_cochange_relations(repo, changed, file_paths)
    unknown_rows.extend(history_unknown)
    ownership_relations = _ownership_inspect_only(inspection | legacy_impacted, graphs, file_paths)
    inspect_only_candidates: set[str] = set()
    for relation in [*deferred_static_relations, *history_relations, *ownership_relations]:
        peer = str(relation.get("from") or "")
        target = str(relation.get("to") or "")
        if not peer or peer not in file_paths or peer in inspection:
            continue
        inspect_only_candidates.add(peer)
        reasons[peer].append(_reason_row(
            path=peer,
            kind=str(relation.get("type") or "inspect-only-evidence"),
            support_level=str(relation.get("supportLevel") or "INFERRED"),
            disposition="INSPECT_ONLY",
            evidence=relation.get("evidence"),
            source=peer,
            target=target or None,
        ))

    why_rows: list[dict[str, Any]] = []
    for path in sorted(set(reasons) | inspection | inspect_only_candidates):
        path_reasons = sorted(
            reasons.get(path, []),
            key=lambda row: (
                str(row.get("disposition")), str(row.get("kind")), str(row.get("from")),
                str(row.get("to")), _canonical_digest(row.get("evidence")),
            ),
        )
        why_rows.append({
            "path": path,
            "reasons": path_reasons,
            "architecture": _architecture_evidence(path, graphs),
            "authorityEvidence": _authority_evidence(path, graphs),
            "authorizationGranted": False,
        })

    unknown_rows = sorted(
        {json.dumps(row, ensure_ascii=False, sort_keys=True): row for row in unknown_rows}.values(),
        key=lambda row: (
            str(row.get("path") or row.get("from") or ""),
            str(row.get("type") or ""),
            str(row.get("reason") or ""),
            str(row.get("specifier") or ""),
        ),
    )

    v2 = {
        "schemaVersion": "code_atlas_impact_inspection.v2",
        "changed": sorted(changed),
        "inspectionPaths": sorted(inspection),
        "inspectOnlyCandidates": sorted(inspect_only_candidates),
        "whyIsThisInBlast": why_rows,
        "relations": sorted(
            [*cpp_relations, *structured_relations, *companion_relations, *deferred_static_relations, *history_relations, *ownership_relations],
            key=lambda row: (
                str(row.get("disposition")), str(row.get("type")), str(row.get("from")), str(row.get("to")),
                _canonical_digest(row.get("evidence")),
            ),
        ),
        "unknownOrUnsupported": unknown_rows,
        "supportTiers": {
            "SUPPORTED": "repository-provable static or typed companion evidence",
            "INFERRED": "bounded inspect-only evidence that cannot authorize edits",
            "UNKNOWN": "unresolved or unsupported relationship evidence",
        },
        "legacyImpactPreserved": sorted(legacy_impacted),
        "authorizationRule": "IMPACT_INSPECTION_NEVER_EXPANDS_ALLOWED_SCOPE",
        "impactRadiusIsAuthorization": False,
        "historicalCochangeIsInspectOnly": True,
        "ownershipIsInspectOnly": True,
        "semanticQueryAffectsInspectionRankingOnly": bool(query_terms),
        "semanticQueryTerms": sorted(query_terms),
        "retrievalIsProof": False,
        "candidateIsAuthority": False,
        "productionCertified": False,
        "doesNotProve": [
            "runtime or reflection-generated dependencies not present in repository evidence",
            "complete dependency semantics for unsupported languages",
            "authorization to edit any inspection or inspect-only candidate",
            "production readiness or universal repository completeness",
        ],
    }
    v2["blastDigest"] = _canonical_digest(v2)

    impact["inspectionV2"] = v2
    impact["inspectionPaths"] = v2["inspectionPaths"]
    impact["inspectOnlyCandidates"] = v2["inspectOnlyCandidates"]
    impact["whyIsThisInBlast"] = v2["whyIsThisInBlast"]
    impact["unknownOrUnsupported"] = v2["unknownOrUnsupported"]
    impact["blastDigest"] = v2["blastDigest"]
    impact["authorizationRule"] = "IMPACT_RADIUS_AND_INSPECTION_NEVER_EXPAND_ALLOWED_SCOPE"
    impact["impactRadiusIsAuthorization"] = False
    graphs["changeImpact"] = impact
    return graphs


__all__ = ["enrich_change_impact"]
