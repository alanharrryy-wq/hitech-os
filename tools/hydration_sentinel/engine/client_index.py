from __future__ import annotations

from dataclasses import dataclass, field

from .context import FileFacts
from .resolver import ImportResolver


@dataclass(slots=True)
class ClientBoundaryIndex:
    client_files: frozenset[str]
    serverish_files: frozenset[str]
    import_graph: dict[str, list[str]] = field(default_factory=dict)
    reverse_import_graph: dict[str, list[str]] = field(default_factory=dict)

    def is_client(self, relpath: str) -> bool:
        return relpath in self.client_files

    def imports_client(self, relpath: str) -> list[str]:
        targets = self.import_graph.get(relpath, [])
        return [target for target in targets if target in self.client_files]


class ClientIndexBuilder:
    def __init__(self, repo_root: str) -> None:
        self.resolver = ImportResolver(repo_root)

    def build(self, inventory: list[FileFacts]) -> ClientBoundaryIndex:
        by_path = {facts.relpath: facts for facts in inventory}
        client_files = frozenset(path for path, facts in by_path.items() if facts.has_use_client)
        serverish_files = frozenset(path for path, facts in by_path.items() if facts.probable_serverish_path)
        import_graph: dict[str, list[str]] = {}
        reverse: dict[str, list[str]] = {}
        for facts in inventory:
            resolved_targets: list[str] = []
            for ref in facts.imports:
                target = self.resolver.resolve(facts.relpath, ref.specifier)
                if not target:
                    continue
                resolved_targets.append(target)
                reverse.setdefault(target, []).append(facts.relpath)
            import_graph[facts.relpath] = sorted(set(resolved_targets))
        for key, values in list(reverse.items()):
            reverse[key] = sorted(set(values))
        return ClientBoundaryIndex(
            client_files=client_files,
            serverish_files=serverish_files,
            import_graph=import_graph,
            reverse_import_graph=reverse,
        )
