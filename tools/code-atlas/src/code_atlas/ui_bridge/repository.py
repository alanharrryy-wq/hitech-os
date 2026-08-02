from __future__ import annotations
import glob
from pathlib import Path
from typing import Any, Iterable

from .canonical import canonical_sha256, read_json
from .errors import ContractError, ResolutionError
from .validation import validate_batches


def discover_json_inputs(inputs: Iterable[str | Path]) -> list[Path]:
    found: set[Path] = set()
    for raw in inputs:
        text = str(raw)
        matches = [Path(p) for p in glob.glob(text, recursive=True)] if any(ch in text for ch in "*?[]") else [Path(text)]
        for path in matches:
            if path.is_dir():
                current_batches = sorted(
                    child for child in path.glob("[0-9][0-9]_*.json")
                    if child.name != "00_contract.json"
                )
                candidates = current_batches or sorted(
                    child for child in path.rglob("*.json")
                    if "history" not in {part.lower() for part in child.parts}
                )
                for child in candidates:
                    found.add(child.resolve())
            elif path.is_file():
                found.add(path.resolve())
    return sorted(found, key=lambda p: p.as_posix().lower())


def _as_batch(data: Any, source: Path) -> list[dict[str, Any]]:
    if isinstance(data, dict) and isinstance(data.get("components"), list) and "batchId" in data:
        return [data]
    if isinstance(data, dict) and isinstance(data.get("batches"), list):
        return [b for b in data["batches"] if isinstance(b, dict)]
    if isinstance(data, dict) and isinstance(data.get("components"), list):
        return [{
            "schema": data.get("schema", "prisma.ui.component.atlas.v1"),
            "schemaVersion": data.get("schemaVersion", "1.0.0"),
            "batchId": data.get("atlasId", f"ATLAS.{canonical_sha256(data)[:16]}"),
            "supersedesBatchId": None,
            "contractHash": data.get("contractHash", canonical_sha256(data.get("contract", {}))),
            "runtimeAlias": data.get("runtimeAlias", "contract"),
            "sourceSnapshotHash": data.get("sourceSnapshotHash", "UNSPECIFIED"),
            "components": data["components"],
            "aliases": data.get("aliases", []),
            "conflicts": data.get("conflicts", []),
            "coverage": data.get("coverage", {}),
            "integrity": data.get("integrity", {"source": source.as_posix()}),
        }]
    return []


class BridgeRepository:
    def __init__(self, batches: list[dict[str, Any]], source_files: list[Path]):
        self.batches = batches
        self.source_files = source_files
        self.validation = validate_batches(batches)
        self.components_by_id: dict[str, dict[str, Any]] = {}
        self.aliases: dict[str, str] = {}
        self.conflicts: list[dict[str, Any]] = []
        self.visual_targets_by_selector: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = {}
        for batch in batches:
            self.conflicts.extend(c for c in batch.get("conflicts", []) if isinstance(c, dict))
            for component in batch.get("components", []):
                if not isinstance(component, dict): continue
                for key in ("componentId", "componentUiId"):
                    value = component.get(key)
                    if value: self.components_by_id[str(value)] = component
                for target in component.get("visualTargets", []):
                    if not isinstance(target, dict):
                        continue
                    selector = target.get("selector")
                    if selector:
                        self.visual_targets_by_selector.setdefault(str(selector), []).append((component, target))
            for alias in batch.get("aliases", []):
                if not isinstance(alias, dict): continue
                if not alias.get("canonicalComponentUiId") and alias.get("aliasKind") not in (None, "componentUiId"):
                    continue
                source = alias.get("aliasId") or alias.get("legacyId") or alias.get("from")
                target = alias.get("canonicalComponentUiId") or alias.get("canonicalId") or alias.get("to")
                if source and target: self.aliases[str(source)] = str(target)

    @classmethod
    def load(cls, inputs: Iterable[str | Path], require_valid: bool = True) -> "BridgeRepository":
        files = discover_json_inputs(inputs)
        batches: list[dict[str, Any]] = []
        errors: list[str] = []
        for path in files:
            try:
                data = read_json(path)
                batches.extend(_as_batch(data, path))
            except Exception as exc:
                errors.append(f"{path}: {type(exc).__name__}: {exc}")
        if errors:
            raise ContractError("Invalid JSON inputs: " + " | ".join(errors))
        if not batches:
            raise ContractError("No UIMAP batch or component atlas inputs were found")
        repo = cls(batches, files)
        if require_valid and not repo.validation["ok"]:
            raise ContractError(f"Bridge contract validation failed with {len(repo.validation['issues'])} issue(s)")
        return repo

    def resolve_alias(self, value: str) -> str:
        seen: set[str] = set()
        current = value
        while current in self.aliases:
            if current in seen:
                raise ContractError(f"Alias cycle detected at {current}")
            seen.add(current)
            current = self.aliases[current]
        return current

    def component(self, value: str) -> dict[str, Any]:
        canonical = self.resolve_alias(value)
        component = self.components_by_id.get(canonical)
        if not component:
            raise ResolutionError(f"Component not found: {value}")
        return component

    def related_visual_targets(
        self,
        component: dict[str, Any],
        selector: str | None,
    ) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        if not selector:
            return []
        runtime = component.get("runtimeAlias")
        owner_file = component.get("ownerFile")
        rows = [
            (candidate, target)
            for candidate, target in self.visual_targets_by_selector.get(selector, [])
            if candidate.get("runtimeAlias") == runtime and candidate.get("ownerFile") == owner_file
        ]
        deduplicated = {
            str(target.get("visualTargetId")): (candidate, target)
            for candidate, target in rows
            if target.get("visualTargetId")
        }
        return [deduplicated[key] for key in sorted(deduplicated)]
