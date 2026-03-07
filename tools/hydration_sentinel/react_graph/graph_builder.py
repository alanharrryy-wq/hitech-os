from __future__ import annotations

from ..engine.client_index import ClientBoundaryIndex
from ..engine.context import FileFacts, ScanOutput
from .models import GraphNode, ReactGraph
from .signal_extractor import GraphSignalExtractor


class ReactGraphBuilder:
    def __init__(self) -> None:
        self.signal_extractor = GraphSignalExtractor()

    def build(self, output: ScanOutput, client_index: ClientBoundaryIndex) -> ReactGraph:
        inventory_map = {facts.relpath: facts for facts in output.inventory}
        entrypoints = tuple(sorted(path for path, facts in inventory_map.items() if self._is_entrypoint(facts)))
        nodes: dict[str, GraphNode] = {}
        import_graph = {path: tuple(sorted(set(targets))) for path, targets in client_index.import_graph.items()}
        reverse_graph = {path: tuple(sorted(set(referrers))) for path, referrers in client_index.reverse_import_graph.items()}

        for relpath, facts in inventory_map.items():
            imports = import_graph.get(relpath, tuple())
            imported_by = reverse_graph.get(relpath, tuple())
            boundary_kind = self._boundary_kind(relpath, facts, client_index)
            signals = self.signal_extractor.signals_for_file(facts)
            nodes[relpath] = GraphNode(
                relpath=relpath,
                boundary_kind=boundary_kind,
                signals=signals,
                imports=imports,
                imported_by=imported_by,
                import_count=len(imports),
                imported_by_count=len(imported_by),
                is_entrypoint=relpath in entrypoints,
            )
        return ReactGraph(nodes=nodes, import_graph=import_graph, reverse_graph=reverse_graph, entrypoints=entrypoints)

    @staticmethod
    def _boundary_kind(relpath: str, facts: FileFacts, client_index: ClientBoundaryIndex) -> str:
        if facts.probable_tooling_path:
            return 'tooling'
        if relpath in client_index.client_files or facts.has_use_client:
            return 'client'
        if relpath in client_index.serverish_files or facts.probable_serverish_path:
            return 'serverish'
        return 'shared'

    @staticmethod
    def _is_entrypoint(facts: FileFacts) -> bool:
        relpath = facts.relpath.lower()
        if '/app/' in relpath and facts.extension in {'.tsx', '.jsx', '.ts', '.js'}:
            return True
        return relpath.endswith('/page.tsx') or relpath.endswith('/layout.tsx') or relpath.endswith('/route.ts') or relpath.endswith('/route.tsx')
