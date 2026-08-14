from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .evidence_foundation import ScopeIdentity, canonical_digest

GRAPH_SCHEMA_VERSION = "code_atlas_lineage_graph.v1"

SECTION_KIND = {
    "clients": "client",
    "licenses": "license",
    "devices": "device",
    "sales": "sale",
}

RELATIONS = (
    ("license", "clientId", "client", "license.client"),
    ("device", "clientId", "client", "device.client"),
    ("sale", "originDeviceId", "device", "sale.origin_device"),
)

SCOPE_REFERENCE_FIELDS = {
    "tenantId": "tenant",
    "businessId": "business",
    "storeId": "store",
    "terminalId": "terminal",
}


@dataclass(frozen=True)
class LineageNode:
    kind: str
    entity_id: str
    scope: ScopeIdentity = field(default_factory=ScopeIdentity)
    source_ref: str = ""
    fields_digest: str = ""

    @property
    def node_id(self) -> str:
        return f"{self.kind}:{self.entity_id}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "nodeId": self.node_id,
            "kind": self.kind,
            "entityId": self.entity_id,
            "scope": self.scope.as_dict(),
            "sourceRef": self.source_ref,
            "fieldsDigest": self.fields_digest,
        }


@dataclass(frozen=True)
class LineageEdge:
    source: str
    target: str
    relation: str
    source_field: str
    status: str
    evidence_ref: str = ""

    @property
    def edge_id(self) -> str:
        return canonical_digest({
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "sourceField": self.source_field,
        })

    def as_dict(self) -> dict[str, Any]:
        return {
            "edgeId": self.edge_id,
            "from": self.source,
            "to": self.target,
            "type": self.relation,
            "sourceField": self.source_field,
            "status": self.status,
            "evidenceRef": self.evidence_ref,
        }


def _entity_id(row: Mapping[str, Any]) -> str:
    raw = row.get("entityId") or row.get("id") or row.get("uuid")
    return "" if raw in (None, "") else str(raw)


def _fields(row: Mapping[str, Any]) -> Mapping[str, Any]:
    value = row.get("fields")
    return value if isinstance(value, Mapping) else row


def build_nodes(payload: Mapping[str, Any]) -> tuple[list[LineageNode], list[dict[str, Any]]]:
    nodes: list[LineageNode] = []
    invalid: list[dict[str, Any]] = []
    seen: set[str] = set()
    for section, kind in SECTION_KIND.items():
        rows = payload.get(section) or []
        if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)):
            continue
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                invalid.append({"section": section, "index": index, "reason": "NON_MAPPING_ROW"})
                continue
            entity_id = _entity_id(row)
            if not entity_id:
                invalid.append({"section": section, "index": index, "reason": "MISSING_ENTITY_ID"})
                continue
            fields = _fields(row)
            scope = ScopeIdentity.from_mapping(fields)
            node = LineageNode(
                kind=kind,
                entity_id=entity_id,
                scope=scope,
                source_ref=f"{section}:{row.get('sourceDb','')}:{row.get('sourceTable','')}",
                fields_digest=canonical_digest(fields),
            )
            if node.node_id in seen:
                invalid.append({"nodeId": node.node_id, "reason": "DUPLICATE_NODE_ID"})
                continue
            seen.add(node.node_id)
            nodes.append(node)
    return nodes, invalid


def build_edges(nodes: Sequence[LineageNode], payload: Mapping[str, Any]) -> list[LineageEdge]:
    by_kind_id = {(node.kind, node.entity_id): node for node in nodes}
    edges: list[LineageEdge] = []
    seen_edges: set[tuple[str, str, str, str]] = set()

    rows_by_kind: dict[str, list[Mapping[str, Any]]] = {}
    for section, kind in SECTION_KIND.items():
        values = payload.get(section) or []
        rows_by_kind[kind] = [row for row in values if isinstance(row, Mapping)] if isinstance(values, list) else []

    for source_kind, field_name, target_kind, relation in RELATIONS:
        for row in rows_by_kind.get(source_kind, []):
            source_id = _entity_id(row)
            fields = _fields(row)
            target_value = fields.get(field_name)
            if not source_id or target_value in (None, ""):
                continue
            source_node = by_kind_id.get((source_kind, source_id))
            if source_node is None:
                continue
            target_id = str(target_value)
            target_node = by_kind_id.get((target_kind, target_id))
            target_node_id = f"{target_kind}:{target_id}"
            status = "RESOLVED" if target_node else "UNRESOLVED_TARGET"
            if target_node and source_node.scope.relation(target_node.scope) == "CONFLICT":
                status = "CROSS_SCOPE_CONFLICT"
            key = (source_node.node_id, target_node_id, relation, field_name)
            if key in seen_edges:
                status = "DUPLICATE_EDGE"
            seen_edges.add(key)
            edges.append(LineageEdge(
                source=source_node.node_id,
                target=target_node_id,
                relation=relation,
                source_field=field_name,
                status=status,
                evidence_ref=source_node.source_ref,
            ))

    for kind, rows in rows_by_kind.items():
        for row in rows:
            source_id = _entity_id(row)
            source_node = by_kind_id.get((kind, source_id))
            if source_node is None:
                continue
            fields = _fields(row)
            for field_name, target_kind in SCOPE_REFERENCE_FIELDS.items():
                target_value = fields.get(field_name)
                if target_value in (None, ""):
                    continue
                target = f"{target_kind}-scope-ref:{target_value}"
                relation = f"{kind}.scope.{target_kind}"
                key = (source_node.node_id, target, relation, field_name)
                if key in seen_edges:
                    continue
                seen_edges.add(key)
                edges.append(LineageEdge(
                    source=source_node.node_id,
                    target=target,
                    relation=relation,
                    source_field=field_name,
                    status="REFERENCE_ONLY_NOT_ENTITY_PROOF",
                    evidence_ref=source_node.source_ref,
                ))
    return edges


def _find_cycles(edges: Sequence[LineageEdge]) -> list[list[str]]:
    adjacency: dict[str, set[str]] = {}
    for edge in edges:
        if edge.status not in {"RESOLVED", "CROSS_SCOPE_CONFLICT"}:
            continue
        adjacency.setdefault(edge.source, set()).add(edge.target)
    cycles: set[tuple[str, ...]] = set()
    visiting: list[str] = []
    visiting_set: set[str] = set()
    visited: set[str] = set()

    def walk(node: str) -> None:
        if node in visiting_set:
            start = visiting.index(node)
            cycles.add(tuple(visiting[start:] + [node]))
            return
        if node in visited:
            return
        visiting.append(node)
        visiting_set.add(node)
        for target in sorted(adjacency.get(node, ())):
            walk(target)
        visiting.pop()
        visiting_set.remove(node)
        visited.add(node)

    for node in sorted(adjacency):
        walk(node)
    return [list(item) for item in sorted(cycles)]


def detect_orphans(nodes: Sequence[LineageNode], edges: Sequence[LineageEdge], payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    resolved_by_source: dict[str, set[str]] = {}
    status_by_source: dict[str, list[str]] = {}
    for edge in edges:
        status_by_source.setdefault(edge.source, []).append(edge.status)
        if edge.status == "RESOLVED":
            resolved_by_source.setdefault(edge.source, set()).add(edge.relation)

    row_index: dict[tuple[str, str], Mapping[str, Any]] = {}
    for section, kind in SECTION_KIND.items():
        for row in payload.get(section) or []:
            if isinstance(row, Mapping):
                entity_id = _entity_id(row)
                if entity_id:
                    row_index[(kind, entity_id)] = row

    out: list[dict[str, Any]] = []
    for node in nodes:
        if node.kind not in {"license", "device", "sale"}:
            continue
        fields = _fields(row_index.get((node.kind, node.entity_id), {}))
        reasons: list[str] = []
        if node.kind == "license":
            if fields.get("clientId") in (None, "") and fields.get("businessId") in (None, ""):
                reasons.append("MISSING_CLIENT_OR_BUSINESS_SCOPE")
            elif fields.get("clientId") not in (None, "") and "license.client" not in resolved_by_source.get(node.node_id, set()):
                reasons.append("UNRESOLVED_CLIENT_PARENT")
        elif node.kind == "device":
            if fields.get("clientId") in (None, "") and fields.get("businessId") in (None, ""):
                reasons.append("MISSING_CLIENT_OR_BUSINESS_SCOPE")
            elif fields.get("clientId") not in (None, "") and "device.client" not in resolved_by_source.get(node.node_id, set()):
                reasons.append("UNRESOLVED_CLIENT_PARENT")
        elif node.kind == "sale":
            if fields.get("businessId") in (None, ""):
                reasons.append("MISSING_BUSINESS_SCOPE")
            if fields.get("originDeviceId") in (None, ""):
                reasons.append("MISSING_ORIGIN_DEVICE")
            elif "sale.origin_device" not in resolved_by_source.get(node.node_id, set()):
                reasons.append("UNRESOLVED_ORIGIN_DEVICE")
        if "CROSS_SCOPE_CONFLICT" in status_by_source.get(node.node_id, []):
            reasons.append("CROSS_SCOPE_PARENT_CONFLICT")
        out.append({
            "entityKind": node.kind,
            "entityId": node.entity_id,
            "status": "ORPHAN_OR_SCOPE_BLOCKED" if reasons else "PASS_EXPLICIT_RELATIONSHIP_REQUIREMENTS",
            "reasons": reasons,
            "scope": node.scope.as_dict(),
            "productionCertified": False,
        })
    return out or [{"status": "BLOCKED_NO_ELIGIBLE_ENTITY_ROWS", "productionCertified": False}]


def build_lineage_graph(payload: Mapping[str, Any]) -> dict[str, Any]:
    nodes, invalid_nodes = build_nodes(payload)
    edges = build_edges(nodes, payload)
    duplicate_edges = [edge.edge_id for edge in edges if edge.status == "DUPLICATE_EDGE"]
    unresolved = [edge.edge_id for edge in edges if edge.status == "UNRESOLVED_TARGET"]
    cross_scope = [edge.edge_id for edge in edges if edge.status == "CROSS_SCOPE_CONFLICT"]
    cycles = _find_cycles(edges)
    orphans = detect_orphans(nodes, edges, payload)
    orphan_blocked = [
        row for row in orphans
        if isinstance(row, Mapping) and row.get("status") == "ORPHAN_OR_SCOPE_BLOCKED"
    ]
    blockers = []
    if invalid_nodes:
        blockers.append("invalid_or_duplicate_nodes")
    if duplicate_edges:
        blockers.append("duplicate_edges")
    if unresolved:
        blockers.append("unresolved_targets")
    if cross_scope:
        blockers.append("cross_scope_conflicts")
    if cycles:
        blockers.append("cycles_detected")
    if orphan_blocked:
        blockers.append("orphan_or_scope_blocked")
    status = "GRAPH_CONTRACT_BACKED_WITH_BLOCKERS" if blockers else "GRAPH_CONTRACT_BACKED"
    return {
        "schemaVersion": GRAPH_SCHEMA_VERSION,
        "status": status,
        "nodes": [node.as_dict() for node in nodes],
        "edges": [edge.as_dict() for edge in edges],
        "orphans": orphans,
        "invalidNodes": invalid_nodes,
        "duplicateEdgeIds": duplicate_edges,
        "unresolvedEdgeIds": unresolved,
        "crossScopeEdgeIds": cross_scope,
        "cycles": cycles,
        "blockers": blockers,
        "certifiable": False,
        "productionCertified": False,
        "doesNotProve": [
            "A relationship that is not backed by an explicit identity field.",
            "Tenant isolation or runtime correctness from graph structure alone.",
        ],
    }
