from __future__ import annotations

import copy
from typing import Any

CONFIDENCE_STATES = ("supported", "inferred", "unknown")


def _normalized_declarations(authorities: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in authorities.get("declarations") or []:
        if not isinstance(item, dict):
            continue
        rows.append({
            "declarationFile": item.get("declarationFile"),
            "path": item.get("path"),
            "scope": item.get("scope"),
            "kind": item.get("kind"),
            "priority": item.get("priority"),
        })
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("scope") or ""),
            str(row.get("declarationFile") or ""),
            str(row.get("path") or ""),
            str(row.get("kind") or ""),
            int(row.get("priority") or 0),
        ),
    )


def _candidate_by_path(authorities: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in authorities.get("candidates") or []:
        if isinstance(row, dict) and row.get("path"):
            out[str(row["path"])] = row
    return out


def _unknown_provenance(graph_name: str, edge: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "kind": "unresolved-edge-provenance",
        "sourceGraph": graph_name,
        "edgeType": str(edge.get("type") or ""),
        "reason": reason,
    }


def _declaration_records(
    declarations: list[dict[str, Any]],
    *,
    declaration_file: str | None = None,
    path: str | None = None,
    scope: str | None = None,
) -> list[dict[str, Any]]:
    rows = []
    for row in declarations:
        if declaration_file is not None and str(row.get("declarationFile") or "") != declaration_file:
            continue
        if path is not None and str(row.get("path") or "") != path:
            continue
        if scope is not None and str(row.get("scope") or "") != scope:
            continue
        rows.append(copy.deepcopy(row))
    return rows


def _derived_provenance(
    graph_name: str,
    edge: dict[str, Any],
    authorities: dict[str, Any],
    declarations: list[dict[str, Any]],
    candidates: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any] | None, str | None]:
    edge_type = str(edge.get("type") or "")
    source = str(edge.get("from") or "")
    target = str(edge.get("to") or "")
    scope = str(edge.get("scope") or "")

    if edge_type in {"authority-declaration", "declares-authority"}:
        records = _declaration_records(
            declarations,
            declaration_file=source or None,
            path=target or None,
            scope=scope or None,
        )
        if records:
            return {
                "kind": "repository-authority-declaration",
                "sourceGraph": graph_name,
                "records": records,
            }, "supported"

    if edge_type == "authority-conflict":
        conflict_scope = source.removeprefix("conflict:") if source.startswith("conflict:") else scope
        conflict_paths = sorted({str(path) for path in (authorities.get("conflicts") or {}).get(conflict_scope, [])})
        records = _declaration_records(declarations, scope=conflict_scope or None)
        declared_paths = sorted({str(row.get("path") or "") for row in records if row.get("path")})
        if target in conflict_paths and len(conflict_paths) >= 2 and set(conflict_paths).issubset(set(declared_paths)):
            return {
                "kind": "repository-authority-conflict",
                "sourceGraph": graph_name,
                "scope": conflict_scope,
                "conflictingPaths": conflict_paths,
                "records": records,
            }, "supported"

    if edge_type == "supports-selection" and source.startswith("reason:"):
        reason = source[len("reason:") :]
        candidate = candidates.get(target)
        if candidate and reason in [str(value) for value in candidate.get("whySelected") or []]:
            return {
                "kind": "authority-selection-reason",
                "sourceGraph": graph_name,
                "path": target,
                "reason": reason,
                "state": candidate.get("state"),
            }, "supported"

    return None, None


def _normalize_edge(
    graph_name: str,
    raw_edge: dict[str, Any],
    authorities: dict[str, Any],
    declarations: list[dict[str, Any]],
    candidates: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    edge = copy.deepcopy(raw_edge)
    raw_confidence = str(edge.get("confidence") or "").strip().lower()
    confidence = raw_confidence if raw_confidence in CONFIDENCE_STATES else None

    provenance = edge.get("provenance")
    if provenance:
        normalized_provenance = copy.deepcopy(provenance)
    elif edge.get("evidence") not in (None, "", [], {}):
        normalized_provenance = {
            "kind": "edge-evidence",
            "sourceGraph": graph_name,
            "evidence": copy.deepcopy(edge.get("evidence")),
        }
    elif edge.get("source") not in (None, "", [], {}):
        normalized_provenance = {
            "kind": "edge-source",
            "sourceGraph": graph_name,
            "source": copy.deepcopy(edge.get("source")),
        }
    else:
        normalized_provenance, derived_confidence = _derived_provenance(
            graph_name, edge, authorities, declarations, candidates,
        )
        if normalized_provenance is None:
            normalized_provenance = _unknown_provenance(
                graph_name,
                edge,
                "EDGE_LEVEL_PROVENANCE_NOT_PROVEN_FROM_CANONICAL_REPOSITORY_FACTS",
            )
            derived_confidence = None
        if confidence is None and derived_confidence in CONFIDENCE_STATES:
            confidence = derived_confidence

    if confidence is None:
        confidence = "unknown"
    if confidence == "supported" and (
        not isinstance(normalized_provenance, dict)
        or normalized_provenance.get("kind") == "unresolved-edge-provenance"
    ):
        confidence = "unknown"

    edge["confidence"] = confidence
    edge["provenance"] = normalized_provenance
    return edge


def normalize_system_graph_edge_provenance(
    graphs: dict[str, Any],
    authorities: dict[str, Any],
) -> dict[str, Any]:
    """Return a deterministic, fail-closed edge-provenance view of system graphs.

    The raw graph producer is not mutated. Existing evidence/confidence is
    preserved. Repository authority declaration/conflict provenance may be
    derived only from canonical authority-discovery facts. Any edge whose
    support cannot be proven remains explicit ``unknown`` instead of being
    promoted to supported.
    """
    normalized = copy.deepcopy(graphs)
    declarations = _normalized_declarations(authorities)
    candidates = _candidate_by_path(authorities)
    counts = {state: 0 for state in CONFIDENCE_STATES}
    normalized_edge_count = 0
    graph_edge_counts: dict[str, int] = {}

    for graph_name in sorted(normalized):
        graph = normalized.get(graph_name)
        if not isinstance(graph, dict) or not isinstance(graph.get("edges"), list):
            continue
        edges = []
        for raw_edge in graph["edges"]:
            if not isinstance(raw_edge, dict):
                continue
            edge = _normalize_edge(graph_name, raw_edge, authorities, declarations, candidates)
            edges.append(edge)
            counts[edge["confidence"]] += 1
        graph["edges"] = edges
        graph["edgeCount"] = len(edges)
        graph_edge_counts[graph_name] = len(edges)
        normalized_edge_count += len(edges)

    normalized["edgeProvenance"] = {
        "schemaVersion": "code_atlas_edge_provenance.v1",
        "rule": "PROVENANCE_AND_CONFIDENCE_REQUIRED_FOR_MATERIAL_EDGES_UNKNOWN_WHEN_UNPROVEN",
        "confidenceStates": list(CONFIDENCE_STATES),
        "normalizedEdgeCount": normalized_edge_count,
        "graphEdgeCounts": graph_edge_counts,
        "confidenceCounts": counts,
        "rawGraphMutated": False,
        "candidateIsAuthority": False,
        "retrievalIsProof": False,
        "impactRadiusIsAuthorization": False,
        "productionCertified": False,
    }
    return normalized
