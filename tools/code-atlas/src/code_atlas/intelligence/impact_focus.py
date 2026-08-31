from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


_C_FAMILY_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
_STATIC_FOCUS_TYPES = {"c-family-include", "structured-path-reference"}
_COMPANION_TYPE = "typed-test-companion"
_QUERY_STOPWORDS = {
    "about", "after", "again", "allow", "before", "change", "changing", "could", "from", "have",
    "into", "only", "repository", "should", "that", "their", "there", "these", "this", "those", "under",
    "using", "when", "where", "which", "while", "with", "without", "would", "return", "returns", "type",
    "types", "value", "values", "function", "functions", "class", "classes", "code", "file", "files",
}
_DIRECT_FANOUT_LIMIT = 4
_MIN_BRANCH_SCORE = 10
_MIN_BRANCH_MARGIN = 5
_MAX_FOCUS_DEPTH = 8


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _simple_stem(token: str) -> str:
    value = token.lower()
    for suffix in ("ability", "ibility", "able", "ible", "ing", "ed", "ers", "er", "s"):
        if value.endswith(suffix) and len(value) - len(suffix) >= 4:
            value = value[: -len(suffix)]
            break
    return value


def _query_terms(value: str) -> set[str]:
    terms: set[str] = set()
    for raw in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", value.lower()):
        for part in raw.split("_"):
            if len(part) < 4 or part in _QUERY_STOPWORDS:
                continue
            terms.add(_simple_stem(part))
    return {term for term in terms if len(term) >= 4 and term not in _QUERY_STOPWORDS}


def _path_terms(path: str) -> set[str]:
    tokens = re.findall(r"[A-Za-z0-9]+", path.lower())
    return {_simple_stem(token) for token in tokens if len(token) >= 3}


def _is_test_path(path: str) -> bool:
    normalized = "/" + path.replace("\\", "/").lower().strip("/") + "/"
    return any(marker in normalized for marker in ("/test/", "/tests/", "/spec/", "/specs/", "/e2e/")) or bool(
        re.search(r"(?:^|/)(?:test[_-]|[^/]+[._-](?:test|spec))(?:[^/]*)$", path, re.I)
    )


def _semantic_path_score(path: str, query_terms: set[str]) -> int:
    if not query_terms:
        return 0
    tokens = _path_terms(path)
    hits = {term for term in query_terms if term in tokens or any(term in token or token in term for token in tokens if len(token) >= 4)}
    if not hits:
        return 0
    score = len(hits) * 10
    if _is_test_path(path):
        score += 3
    return score


def _branch_score(candidate: str, reverse: dict[str, list[str]], query_terms: set[str]) -> dict[str, Any]:
    own = _semantic_path_score(candidate, query_terms)
    descendants = sorted(set(reverse.get(candidate, [])))
    descendant_scores = [(_semantic_path_score(path, query_terms), path) for path in descendants]
    best_descendant_score = max((score for score, _path in descendant_scores), default=0)
    best_descendants = sorted(path for score, path in descendant_scores if score == best_descendant_score and score > 0)
    fanout_penalty = min(18, len(descendants) // 3)
    transit_bonus = 2 if best_descendant_score > own and Path(candidate).suffix.lower() in {".h", ".hh", ".hpp", ".hxx"} else 0
    score = own + (2 * best_descendant_score) + transit_bonus - fanout_penalty
    return {
        "path": candidate,
        "score": score,
        "ownSemanticScore": own,
        "bestDescendantSemanticScore": best_descendant_score,
        "bestDescendants": best_descendants[:6],
        "reverseFanout": len(descendants),
        "fanoutPenalty": fanout_penalty,
        "transitBonus": transit_bonus,
    }


def _select_reverse_branches(
    current: str,
    reverse: dict[str, list[str]],
    query_terms: set[str],
) -> tuple[list[str], list[str], dict[str, Any] | None]:
    candidates = sorted(set(reverse.get(current, [])))
    if not candidates:
        return [], [], None
    if len(candidates) <= _DIRECT_FANOUT_LIMIT:
        return candidates, [], {
            "path": current,
            "mode": "BOUNDED_DIRECT_FANOUT",
            "fanout": len(candidates),
            "selected": candidates,
            "deferred": [],
        }

    ranked = sorted(
        (_branch_score(candidate, reverse, query_terms) for candidate in candidates),
        key=lambda row: (-int(row["score"]), str(row["path"])),
    )
    top = ranked[0]
    runner_up = ranked[1] if len(ranked) > 1 else None
    margin = int(top["score"]) - int(runner_up["score"]) if runner_up else int(top["score"])
    if int(top["score"]) < _MIN_BRANCH_SCORE or margin < _MIN_BRANCH_MARGIN:
        return [], candidates, {
            "path": current,
            "mode": "AMBIGUOUS_HIGH_FANOUT_DEFERRED",
            "fanout": len(candidates),
            "selected": [],
            "deferred": candidates,
            "top": top,
            "runnerUp": runner_up,
            "margin": margin,
            "minimumScore": _MIN_BRANCH_SCORE,
            "minimumMargin": _MIN_BRANCH_MARGIN,
        }
    selected = [str(top["path"])]
    deferred = [candidate for candidate in candidates if candidate not in selected]
    return selected, deferred, {
        "path": current,
        "mode": "SEMANTIC_HIGH_FANOUT_FOCUS",
        "fanout": len(candidates),
        "selected": selected,
        "deferred": deferred,
        "top": top,
        "runnerUp": runner_up,
        "margin": margin,
        "minimumScore": _MIN_BRANCH_SCORE,
        "minimumMargin": _MIN_BRANCH_MARGIN,
    }


def _supported_relations(v2: dict[str, Any], relation_types: set[str]) -> list[dict[str, Any]]:
    return [
        row for row in v2.get("relations") or []
        if isinstance(row, dict)
        and str(row.get("type") or "") in relation_types
        and str(row.get("supportLevel") or "").upper() == "SUPPORTED"
        and row.get("from")
        and row.get("to")
    ]


def _focus_c_family(
    changed: set[str],
    v2: dict[str, Any],
    semantic_query: str,
) -> dict[str, Any] | None:
    static_relations = _supported_relations(v2, _STATIC_FOCUS_TYPES)
    if not static_relations:
        return None
    c_paths = {
        str(value)
        for row in static_relations
        if str(row.get("type")) == "c-family-include"
        for value in (row.get("from"), row.get("to"))
        if value
    }
    if not any(path in c_paths or Path(path).suffix.lower() in _C_FAMILY_SUFFIXES for path in changed):
        return None

    reverse: dict[str, list[str]] = defaultdict(list)
    relation_by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in static_relations:
        source = str(row["from"])
        target = str(row["to"])
        reverse[target].append(source)
        relation_by_pair[(source, target)].append(row)
    for target in reverse:
        reverse[target] = sorted(set(reverse[target]))

    query_terms = _query_terms(semantic_query)
    selected_edges: list[tuple[str, str]] = []
    decisions: list[dict[str, Any]] = []
    deferred: set[str] = set()
    reached: set[str] = set(changed)
    depth: dict[str, int] = {path: 0 for path in changed}
    queue: deque[str] = deque(sorted(changed))
    visited: set[str] = set()

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        current_depth = depth.get(current, 0)
        if current_depth >= _MAX_FOCUS_DEPTH:
            deferred.update(reverse.get(current, []))
            decisions.append({
                "path": current,
                "mode": "MAX_FOCUS_DEPTH_DEFERRED",
                "fanout": len(reverse.get(current, [])),
                "selected": [],
                "deferred": sorted(set(reverse.get(current, []))),
                "maxDepth": _MAX_FOCUS_DEPTH,
            })
            continue
        selected, not_selected, decision = _select_reverse_branches(current, reverse, query_terms)
        if decision:
            decisions.append(decision)
        deferred.update(not_selected)
        for source in selected:
            selected_edges.append((source, current))
            if source not in reached:
                reached.add(source)
                depth[source] = current_depth + 1
                queue.append(source)

    selected_children: dict[str, set[str]] = defaultdict(set)
    for source, target in selected_edges:
        selected_children[target].add(source)

    bridge_paths = {
        path for path in reached - changed
        if selected_children.get(path)
        and _semantic_path_score(path, query_terms) == 0
        and not _is_test_path(path)
    }
    primary = set(changed) | (reached - bridge_paths)

    companion_relations = _supported_relations(v2, {_COMPANION_TYPE})
    companion_adjacency: dict[str, set[str]] = defaultdict(set)
    for row in companion_relations:
        left = str(row["from"])
        right = str(row["to"])
        companion_adjacency[left].add(right)
        companion_adjacency[right].add(left)
    for path in sorted(list(primary)):
        for companion in sorted(companion_adjacency.get(path, set())):
            primary.add(companion)

    selected_relation_rows = [
        row
        for source, target in selected_edges
        for row in relation_by_pair.get((source, target), [])
    ]
    return {
        "mode": "C_FAMILY_SEMANTIC_BRANCH_FOCUS",
        "queryTerms": sorted(query_terms),
        "primaryInspectionPaths": sorted(primary),
        "bridgePaths": sorted(bridge_paths),
        "deferredStaticPaths": sorted(deferred - primary - bridge_paths),
        "selectedStaticRelations": selected_relation_rows,
        "branchDecisions": sorted(decisions, key=lambda row: str(row.get("path") or "")),
        "rule": "HIGH_FANOUT_STATIC_BRANCHES_REQUIRE_UNIQUE_SEMANTIC_SUPPORT;_TRANSIT_ONLY_PATHS_ARE_EVIDENCE_BRIDGES",
    }


def _focus_go_actionable(impact: dict[str, Any]) -> dict[str, Any] | None:
    actionable = impact.get("actionableReview") or {}
    if str(actionable.get("scope") or "") != "GO_BOUNDED_V1":
        return None
    paths = sorted({str(path) for path in actionable.get("paths") or [] if path})
    if not paths:
        return None
    legacy = {str(path) for path in impact.get("impacted") or [] if path}
    primary = set(paths)
    return {
        "mode": "REUSE_GO_BOUNDED_V1_ACTIONABLE_REVIEW",
        "primaryInspectionPaths": paths,
        "bridgePaths": [],
        "deferredStaticPaths": sorted(legacy - primary),
        "rule": "REUSE_EXISTING_GO_BOUNDED_ACTIONABLE_REVIEW;STRUCTURAL_ONLY_IMPACT_REMAINS_INSPECT_ONLY",
        "sourceActionableReview": actionable,
    }


def _normalize_why(
    existing_rows: list[dict[str, Any]],
    primary: set[str],
    inspect_only: set[str],
    bridge: set[str],
    focus: dict[str, Any],
) -> list[dict[str, Any]]:
    by_path = {
        str(row.get("path")): dict(row)
        for row in existing_rows
        if isinstance(row, dict) and row.get("path")
    }
    all_paths = sorted(primary | inspect_only | bridge)
    rows: list[dict[str, Any]] = []
    for path in all_paths:
        row = dict(by_path.get(path) or {
            "path": path,
            "reasons": [],
            "architecture": None,
            "authorityEvidence": None,
            "authorizationGranted": False,
        })
        reasons = []
        for reason in row.get("reasons") or []:
            normalized = dict(reason)
            if path in inspect_only and normalized.get("disposition") == "INSPECT":
                normalized["disposition"] = "INSPECT_ONLY"
            if path in bridge:
                normalized["disposition"] = "EVIDENCE_BRIDGE"
            reasons.append(normalized)
        if path in primary:
            reasons.append({
                "path": path,
                "kind": "blast-v2-focus",
                "supportLevel": "SUPPORTED",
                "disposition": "INSPECT",
                "evidence": {"mode": focus.get("mode"), "rule": focus.get("rule")},
            })
        elif path in bridge:
            reasons.append({
                "path": path,
                "kind": "blast-v2-focus",
                "supportLevel": "SUPPORTED",
                "disposition": "EVIDENCE_BRIDGE",
                "evidence": {"mode": focus.get("mode"), "rule": focus.get("rule")},
            })
        else:
            reasons.append({
                "path": path,
                "kind": "blast-v2-focus",
                "supportLevel": "INFERRED",
                "disposition": "INSPECT_ONLY",
                "evidence": {"mode": focus.get("mode"), "rule": focus.get("rule")},
            })
        row["reasons"] = sorted(
            reasons,
            key=lambda value: (
                str(value.get("disposition") or ""), str(value.get("kind") or ""),
                str(value.get("from") or ""), str(value.get("to") or ""), _digest(value.get("evidence")),
            ),
        )
        row["authorizationGranted"] = False
        rows.append(row)
    return rows


def focus_change_impact(
    repo_root: str | Path,
    graphs: dict[str, Any],
    *,
    semantic_query: str = "",
) -> dict[str, Any]:
    """Refine Blast V2 inspection without touching the legacy impact graph or edit authority.

    Go reuses the existing bounded actionable review. C/C++ uses a deterministic
    semantic beam only at high-fanout static include hubs, while intermediate
    traversal nodes are retained as evidence bridges rather than promoted into the
    primary inspection set. Ambiguous branches stay inspect-only/UNKNOWN-friendly.
    """
    del repo_root  # reserved for future repository-local scoring; no filesystem assumptions required here.
    impact = graphs.get("changeImpact") or {}
    v2 = impact.get("inspectionV2") or {}
    if not isinstance(v2, dict) or not v2:
        return graphs

    changed = {str(path) for path in impact.get("changed") or v2.get("changed") or [] if path}
    legacy = {str(path) for path in impact.get("impacted") or [] if path}
    raw_primary = {str(path) for path in impact.get("inspectionPaths") or v2.get("inspectionPaths") or [] if path}
    raw_inspect_only = {str(path) for path in impact.get("inspectOnlyCandidates") or v2.get("inspectOnlyCandidates") or [] if path}

    focus = _focus_go_actionable(impact)
    if focus is None:
        focus = _focus_c_family(changed, v2, semantic_query)
    if focus is None:
        return graphs

    primary = set(focus.get("primaryInspectionPaths") or [])
    primary.update(changed)
    bridge = set(focus.get("bridgePaths") or []) - primary
    inspect_only = (raw_primary | raw_inspect_only | set(focus.get("deferredStaticPaths") or []) | legacy) - primary - bridge

    unknown = list(v2.get("unknownOrUnsupported") or [])
    for decision in focus.get("branchDecisions") or []:
        if decision.get("mode") == "AMBIGUOUS_HIGH_FANOUT_DEFERRED":
            unknown.append({
                "path": decision.get("path"),
                "type": "blast-v2-focus",
                "supportLevel": "UNKNOWN",
                "disposition": "UNRESOLVED",
                "reason": "HIGH_FANOUT_STATIC_BRANCH_NOT_UNIQUELY_SUPPORTED_BY_SEMANTIC_EVIDENCE",
                "fanout": decision.get("fanout"),
                "top": decision.get("top"),
                "runnerUp": decision.get("runnerUp"),
                "margin": decision.get("margin"),
            })
    unknown = sorted(
        {json.dumps(row, ensure_ascii=False, sort_keys=True): row for row in unknown}.values(),
        key=lambda row: (
            str(row.get("path") or row.get("from") or ""), str(row.get("type") or ""),
            str(row.get("reason") or ""), str(row.get("specifier") or ""),
        ),
    )

    focus_payload = {
        **focus,
        "schemaVersion": "code_atlas_impact_focus.v1",
        "rawInspectionPaths": sorted(raw_primary),
        "rawInspectOnlyCandidates": sorted(raw_inspect_only),
        "focusedInspectionPaths": sorted(primary),
        "evidenceBridgePaths": sorted(bridge),
        "focusedInspectOnlyCandidates": sorted(inspect_only),
        "authorizationRule": "FOCUS_NEVER_EXPANDS_ALLOWED_SCOPE",
        "impactRadiusIsAuthorization": False,
        "productionCertified": False,
    }
    focus_payload["focusDigest"] = _digest(focus_payload)

    why = _normalize_why(
        list(v2.get("whyIsThisInBlast") or impact.get("whyIsThisInBlast") or []),
        primary,
        inspect_only,
        bridge,
        focus_payload,
    )

    v2["rawInspectionPaths"] = sorted(raw_primary)
    v2["rawInspectOnlyCandidates"] = sorted(raw_inspect_only)
    v2["inspectionPaths"] = sorted(primary)
    v2["inspectOnlyCandidates"] = sorted(inspect_only)
    v2["evidenceBridgePaths"] = sorted(bridge)
    v2["whyIsThisInBlast"] = why
    v2["unknownOrUnsupported"] = unknown
    v2["focusV2"] = focus_payload
    v2["blastDigestBeforeFocus"] = v2.get("blastDigest")
    v2_no_digest = dict(v2)
    v2_no_digest.pop("blastDigest", None)
    v2["blastDigest"] = _digest(v2_no_digest)

    impact["inspectionV2"] = v2
    impact["rawInspectionPaths"] = sorted(raw_primary)
    impact["inspectionPaths"] = sorted(primary)
    impact["inspectOnlyCandidates"] = sorted(inspect_only)
    impact["evidenceBridgePaths"] = sorted(bridge)
    impact["whyIsThisInBlast"] = why
    impact["unknownOrUnsupported"] = unknown
    impact["focusV2"] = focus_payload
    impact["blastDigest"] = v2["blastDigest"]
    impact["impactRadiusIsAuthorization"] = False
    impact["authorizationRule"] = "IMPACT_RADIUS_FOCUS_AND_INSPECTION_NEVER_EXPAND_ALLOWED_SCOPE"
    graphs["changeImpact"] = impact
    return graphs


__all__ = ["focus_change_impact"]
