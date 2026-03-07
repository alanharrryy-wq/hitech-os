from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class GraphNode:
    relpath: str
    boundary_kind: str
    signals: tuple[str, ...] = field(default_factory=tuple)
    imports: tuple[str, ...] = field(default_factory=tuple)
    imported_by: tuple[str, ...] = field(default_factory=tuple)
    import_count: int = 0
    imported_by_count: int = 0
    is_entrypoint: bool = False

    def to_dict(self) -> dict:
        return {
            'relpath': self.relpath,
            'boundary_kind': self.boundary_kind,
            'signals': list(self.signals),
            'imports': list(self.imports),
            'imported_by': list(self.imported_by),
            'import_count': self.import_count,
            'imported_by_count': self.imported_by_count,
            'is_entrypoint': self.is_entrypoint,
        }


@dataclass(slots=True)
class GraphPath:
    source: str
    target: str
    hops: tuple[str, ...]
    signal: str
    severity: str
    rationale: str

    def to_dict(self) -> dict:
        return {
            'source': self.source,
            'target': self.target,
            'hops': list(self.hops),
            'hop_count': max(0, len(self.hops) - 1),
            'signal': self.signal,
            'severity': self.severity,
            'rationale': self.rationale,
        }


@dataclass(slots=True)
class GraphSummary:
    node_count: int
    edge_count: int
    client_node_count: int
    serverish_node_count: int
    shared_node_count: int
    tooling_node_count: int
    entrypoint_count: int
    signal_counts: dict[str, int] = field(default_factory=dict)
    path_counts: dict[str, int] = field(default_factory=dict)
    risky_paths: list[GraphPath] = field(default_factory=list)
    hottest_hubs: list[dict[str, object]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'node_count': self.node_count,
            'edge_count': self.edge_count,
            'client_node_count': self.client_node_count,
            'serverish_node_count': self.serverish_node_count,
            'shared_node_count': self.shared_node_count,
            'tooling_node_count': self.tooling_node_count,
            'entrypoint_count': self.entrypoint_count,
            'signal_counts': dict(sorted(self.signal_counts.items())),
            'path_counts': dict(sorted(self.path_counts.items())),
            'risky_paths': [item.to_dict() for item in self.risky_paths],
            'hottest_hubs': self.hottest_hubs,
            'notes': self.notes,
        }


@dataclass(slots=True)
class ReactGraph:
    nodes: dict[str, GraphNode]
    import_graph: dict[str, tuple[str, ...]]
    reverse_graph: dict[str, tuple[str, ...]]
    entrypoints: tuple[str, ...]

    @property
    def edge_count(self) -> int:
        return sum(len(targets) for targets in self.import_graph.values())
