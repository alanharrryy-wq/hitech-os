from __future__ import annotations

from collections import Counter

from ..engine.context import Finding
from .models import GraphSummary, ReactGraph
from .path_finder import GraphPathFinder


class GraphBoundaryAnalyzer:
    def __init__(self) -> None:
        self.path_finder = GraphPathFinder()

    def analyze(self, graph: ReactGraph) -> tuple[list[Finding], GraphSummary]:
        findings: list[Finding] = []
        risky_paths = []
        signal_counts = Counter(signal for node in graph.nodes.values() for signal in node.signals)
        path_counts: dict[str, int] = {}

        for signal, rule_id, message in [
            ('use_client', 'graph_server_client_chain', 'Serverish entrypoint reaches a client boundary through an import chain. Validate the island split and data handoff.'),
            ('storage_api', 'graph_storage_reachability', 'Entrypoint reaches storage-backed render logic. Prefer post-mount hydration or server-safe defaults.'),
            ('nondeterministic', 'graph_nondeterministic_reachability', 'Entrypoint reaches nondeterministic render logic. Stabilize values before crossing SSR/CSR boundaries.'),
            ('dom_mutation', 'graph_dom_mutation_reachability', 'Entrypoint reaches DOM mutation logic. Gate it behind effects or tooling-only islands.'),
        ]:
            paths = self.path_finder.iter_paths_to_signal(
                graph,
                source_predicate=lambda node: node.boundary_kind in {'serverish', 'shared'} or node.is_entrypoint,
                target_signal=signal,
            )
            path_counts[signal] = len(paths)
            risky_paths.extend(paths)
            for item in paths:
                findings.append(self._path_finding(item, rule_id, message))

        for node in sorted(graph.nodes.values(), key=lambda item: (-item.imported_by_count, item.relpath))[:12]:
            if node.boundary_kind != 'client' or node.imported_by_count < 3:
                continue
            findings.append(
                Finding(
                    rule_id='graph_client_island_pressure',
                    severity='medium' if node.imported_by_count < 6 else 'high',
                    relpath=node.relpath,
                    line_number=1,
                    column_number=1,
                    message='Client island is imported by many callers. Consider splitting the boundary to reduce hydration blast radius.',
                    snippet=node.relpath,
                    excerpt='\n'.join(f'- {path}' for path in node.imported_by[:8]),
                    tags=('graph', 'boundary', 'client-island'),
                    details={'imported_by_count': node.imported_by_count, 'imported_by': list(node.imported_by[:12])},
                ).ensure_fingerprint()
            )

        hottest_hubs = [
            {
                'relpath': node.relpath,
                'boundary_kind': node.boundary_kind,
                'imported_by_count': node.imported_by_count,
                'signals': list(node.signals),
            }
            for node in sorted(graph.nodes.values(), key=lambda item: (-item.imported_by_count, item.relpath))[:10]
        ]
        summary = GraphSummary(
            node_count=len(graph.nodes),
            edge_count=graph.edge_count,
            client_node_count=sum(1 for node in graph.nodes.values() if node.boundary_kind == 'client'),
            serverish_node_count=sum(1 for node in graph.nodes.values() if node.boundary_kind == 'serverish'),
            shared_node_count=sum(1 for node in graph.nodes.values() if node.boundary_kind == 'shared'),
            tooling_node_count=sum(1 for node in graph.nodes.values() if node.boundary_kind == 'tooling'),
            entrypoint_count=len(graph.entrypoints),
            signal_counts=dict(signal_counts),
            path_counts=path_counts,
            risky_paths=risky_paths[:20],
            hottest_hubs=hottest_hubs,
            notes=self._notes(graph, path_counts),
        )
        return findings, summary

    @staticmethod
    def _path_finding(path, rule_id: str, message: str) -> Finding:
        return Finding(
            rule_id=rule_id,
            severity=path.severity,
            relpath=path.source,
            line_number=1,
            column_number=1,
            message=message,
            snippet=' -> '.join(path.hops),
            excerpt=path.rationale,
            tags=('graph', 'react-boundary', path.signal),
            details={'target': path.target, 'hops': list(path.hops), 'signal': path.signal},
        ).ensure_fingerprint()

    @staticmethod
    def _notes(graph: ReactGraph, path_counts: dict[str, int]) -> list[str]:
        notes: list[str] = []
        if path_counts.get('storage_api', 0):
            notes.append('Storage APIs are reachable from entrypoints. Focus on client-only post-mount hydration for those branches.')
        if path_counts.get('nondeterministic', 0):
            notes.append('Nondeterministic render sources are still reachable through the import graph. Stabilize them before SSR boundaries.')
        if not notes:
            notes.append('Graph scan found no high-signal reachability chains beyond the baseline rule engine.')
        if any(node.boundary_kind == 'client' and node.imported_by_count >= 4 for node in graph.nodes.values()):
            notes.append('At least one client island has high import fan-in. Consider slicing it into smaller islands.')
        return notes
