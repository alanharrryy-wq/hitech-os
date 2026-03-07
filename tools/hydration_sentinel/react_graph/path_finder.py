from __future__ import annotations

from collections import deque

from .models import GraphPath, ReactGraph


class GraphPathFinder:
    def iter_paths_to_signal(self, graph: ReactGraph, *, source_predicate, target_signal: str, limit: int = 20, max_depth: int = 6) -> list[GraphPath]:
        results: list[GraphPath] = []
        for source in graph.entrypoints:
            node = graph.nodes.get(source)
            if node is None or not source_predicate(node):
                continue
            path = self._find_path(graph, source, target_signal=target_signal, max_depth=max_depth)
            if path is None:
                continue
            results.append(path)
            if len(results) >= limit:
                break
        return results

    def _find_path(self, graph: ReactGraph, source: str, *, target_signal: str, max_depth: int) -> GraphPath | None:
        queue = deque([(source, [source])])
        visited = {source}
        while queue:
            current, hops = queue.popleft()
            if len(hops) > max_depth + 1:
                continue
            node = graph.nodes.get(current)
            if node and current != source and target_signal in node.signals:
                return GraphPath(
                    source=source,
                    target=current,
                    hops=tuple(hops),
                    signal=target_signal,
                    severity=self._severity_for(target_signal, hops, node.boundary_kind),
                    rationale=self._rationale(target_signal, current, hops),
                )
            for target in graph.import_graph.get(current, tuple()):
                if target in visited:
                    continue
                visited.add(target)
                queue.append((target, [*hops, target]))
        return None

    @staticmethod
    def _severity_for(target_signal: str, hops: list[str], boundary_kind: str) -> str:
        if target_signal in {'storage_api', 'nondeterministic'}:
            return 'high' if boundary_kind != 'tooling' else 'medium'
        if target_signal == 'dom_mutation':
            return 'medium'
        if target_signal == 'use_client':
            return 'medium' if len(hops) > 2 else 'low'
        return 'low'

    @staticmethod
    def _rationale(target_signal: str, target: str, hops: list[str]) -> str:
        chain = ' -> '.join(hops)
        return f'Entrypoint reaches {target_signal} surface at {target} via {chain}.'
