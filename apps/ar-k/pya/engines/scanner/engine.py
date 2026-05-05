from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pya.contracts.engine_contracts import build_execution_summary
from pya.contracts.enums import Severity, State
from pya.contracts.signal_contract import build_signal
from pya.kernel.discovery import discover_files_with_stats
from pya.kernel.identity import normalize_relpath
from pya.kernel.models import EngineRunResult
from pya.system.canon_policy import classify_source_path
from pya.system.state_model import validate_state_producer

from .parser import classify_file, parse_python_file, parse_text_surface, read_text_file


@dataclass
class ScannerEngine:
    manifest: dict[str, Any]
    engine_id: str = "scanner"
    stage: str = "scan"

    def run(self, context) -> EngineRunResult:
        started_at = context.execution_time
        emitted_events: list[str] = []
        artifacts: list[dict[str, Any]] = []
        context.event_bus.emit(
            name="scanner.started",
            producer=self.engine_id,
            target=str(context.paths.target),
            payload={"stage": self.stage},
        )
        emitted_events.append("scanner.started")

        inventory: list[dict[str, Any]] = []
        signals: list[dict[str, Any]] = []
        dependency_edges: list[dict[str, str]] = []
        route_candidates: list[dict[str, Any]] = []
        boundary_candidates: list[dict[str, Any]] = []
        python_files = 0
        frontend_surface_files = 0
        parse_errors = 0
        skipped_noncanonical_surface_count = 0

        discovered_paths, discovery_stats = discover_files_with_stats(context.paths.target)
        for path in discovered_paths:
            relative_path = normalize_relpath(path, context.paths.target)
            path_policy = classify_source_path(relative_path)
            file_kind = classify_file(relative_path)
            if file_kind in {"python", "typescript", "javascript", "json", "html", "css", "markdown"}:
                _ = read_text_file(path)
            surface_kind = "python_module" if file_kind == "python" else None
            canonical_source = path_policy.canonical_source
            non_product_class = path_policy.non_product_class
            classification_tags: list[str] = [f"non-product:{non_product_class}"] if non_product_class else []
            tags: list[str] = list(classification_tags)
            routes: list[str] = []
            boundaries: list[str] = []
            imports: list[str] = []
            exports: list[str] = []
            module_name: str | None = None
            counted_as_noncanonical = False

            if file_kind == "python":
                python_files += 1
                module_name = relative_path[:-3].replace("/", ".")
                parsed = parse_python_file(path)
                imports = parsed["imports"]
                exports = parsed["exports"]
                if not canonical_source:
                    skipped_noncanonical_surface_count += 1
                    counted_as_noncanonical = True
                else:
                    if not parsed["ok"]:
                        parse_errors += 1
                        validate_state_producer(self.engine_id, State.AMBIGUOUS.value)
                        signals.append(
                            build_signal(
                                signal_type="module_candidate",
                                source_path=relative_path,
                                producer=self.engine_id,
                                state=State.AMBIGUOUS.value,
                                confidence=0.2,
                                evidence={
                                    "parse_error": parsed["error"],
                                    "kind": file_kind,
                                    "surface_kind": surface_kind,
                                    "canonical_source": canonical_source,
                                    "non_product_class": non_product_class,
                                },
                                snapshot_id=context.execution_id,
                                created_at=context.execution_time,
                                tags=[file_kind, "parse_error", *classification_tags],
                                module_name=module_name,
                            )
                        )
                        context.event_bus.emit(
                            name="scanner.parse_warning",
                            producer=self.engine_id,
                            target=relative_path,
                            payload={"error": parsed["error"]},
                            severity=Severity.WARNING.value,
                        )
                        emitted_events.append("scanner.parse_warning")
                    else:
                        validate_state_producer(self.engine_id, State.CANDIDATE.value)
                        signals.append(
                            build_signal(
                                signal_type="module_candidate",
                                source_path=relative_path,
                                producer=self.engine_id,
                                state=State.CANDIDATE.value,
                                confidence=0.8,
                                evidence={
                                    "imports": imports,
                                    "exports": exports,
                                    "kind": file_kind,
                                    "surface_kind": surface_kind,
                                    "routes": [],
                                    "boundaries": [],
                                    "canonical_source": canonical_source,
                                    "non_product_class": non_product_class,
                                },
                                snapshot_id=context.execution_id,
                                created_at=context.execution_time,
                                tags=[file_kind, "module", *classification_tags],
                                module_name=module_name,
                            )
                        )
            elif file_kind in {"typescript", "javascript", "json", "html", "css", "markdown"}:
                surface = parse_text_surface(path, relative_path)
                surface_kind = surface["surface_kind"]
                canonical_source = bool(surface["canonical_source"])
                non_product_class = surface.get("non_product_class") or non_product_class
                classification_tags = [f"non-product:{non_product_class}"] if non_product_class else []
                tags = sorted(set([*surface["tags"], *classification_tags]))
                routes = surface["routes"]
                boundaries = surface["boundaries"]
                imports = surface["imports"]
                module_name = surface["module_name"]
                if not canonical_source:
                    skipped_noncanonical_surface_count += 1
                    counted_as_noncanonical = True
                if surface["should_emit_module_candidate"]:
                    frontend_surface_files += 1
                    validate_state_producer(self.engine_id, State.CANDIDATE.value)
                    signal_tags = sorted(set([file_kind, surface_kind, *tags]))
                    signals.append(
                        build_signal(
                            signal_type="module_candidate",
                            source_path=relative_path,
                            producer=self.engine_id,
                            state=State.CANDIDATE.value,
                            confidence=0.55,
                            evidence={
                                "imports": imports,
                                "exports": [],
                                "kind": file_kind,
                                "surface_kind": surface_kind,
                                "routes": routes,
                                "boundaries": boundaries,
                                "canonical_source": canonical_source,
                                "non_product_class": non_product_class,
                            },
                            snapshot_id=context.execution_id,
                            created_at=context.execution_time,
                            tags=signal_tags,
                            module_name=module_name,
                        )
                    )
                for route in routes:
                    validate_state_producer(self.engine_id, State.OBSERVED.value)
                    route_candidates.append({"route_path": route, "source_path": relative_path, "surface_kind": surface_kind})
                    signals.append(
                        build_signal(
                            signal_type="route_candidate",
                            source_path=relative_path,
                            producer=self.engine_id,
                            state=State.OBSERVED.value,
                            confidence=0.65,
                            evidence={
                                "route_path": route,
                                "surface_kind": surface_kind,
                                "canonical_source": canonical_source,
                                "non_product_class": non_product_class,
                            },
                            snapshot_id=context.execution_id,
                            created_at=context.execution_time,
                            tags=sorted(set(["route", "route-aware", surface_kind, *tags])),
                            module_name=module_name,
                        )
                    )
                for boundary_kind in boundaries:
                    validate_state_producer(self.engine_id, State.OBSERVED.value)
                    boundary_candidates.append({"boundary_kind": boundary_kind, "source_path": relative_path, "surface_kind": surface_kind})
                    signals.append(
                        build_signal(
                            signal_type="boundary_candidate",
                            source_path=relative_path,
                            producer=self.engine_id,
                            state=State.OBSERVED.value,
                            confidence=0.6,
                            evidence={
                                "boundary_kind": boundary_kind,
                                "surface_kind": surface_kind,
                                "canonical_source": canonical_source,
                                "non_product_class": non_product_class,
                            },
                            snapshot_id=context.execution_id,
                            created_at=context.execution_time,
                            tags=sorted(set(["boundary", boundary_kind, surface_kind, *tags])),
                            module_name=module_name,
                        )
                    )

            inventory.append(
                {
                    "path": relative_path,
                    "kind": file_kind,
                    "surface_kind": surface_kind or file_kind,
                    "size_bytes": path.stat().st_size,
                    "imports": imports,
                    "exports": exports,
                    "routes": routes,
                    "boundaries": boundaries,
                    "tags": tags,
                    "canonical_source": canonical_source,
                    "non_product_class": non_product_class,
                }
            )
            validate_state_producer(self.engine_id, State.OBSERVED.value)
            signals.append(
                build_signal(
                    signal_type="file_observed",
                    source_path=relative_path,
                    producer=self.engine_id,
                    state=State.OBSERVED.value,
                    confidence=1.0,
                    evidence={
                        "kind": file_kind,
                        "surface_kind": surface_kind or file_kind,
                        "routes": routes,
                        "boundaries": boundaries,
                        "tags": tags,
                        "canonical_source": canonical_source,
                        "non_product_class": non_product_class,
                    },
                    snapshot_id=context.execution_id,
                    created_at=context.execution_time,
                    tags=sorted(set([file_kind, surface_kind or file_kind, *tags])),
                )
            )

            if imports and canonical_source:
                source_label = module_name or relative_path
                for imported in sorted(set(imports)):
                    dependency_edges.append({"source": source_label, "target": imported})
                    signals.append(
                        build_signal(
                            signal_type="import_edge",
                            source_path=relative_path,
                            producer=self.engine_id,
                            state=State.OBSERVED.value,
                            confidence=0.7,
                            evidence={
                                "target_import": imported,
                                "module_name": source_label,
                                "surface_kind": surface_kind or file_kind,
                                "canonical_source": canonical_source,
                            },
                            snapshot_id=context.execution_id,
                            created_at=context.execution_time,
                            tags=["dependency", surface_kind or file_kind],
                        )
                    )
            if not canonical_source and not counted_as_noncanonical:
                skipped_noncanonical_surface_count += 1

        inventory = sorted(inventory, key=lambda item: item["path"])
        route_candidates = sorted(route_candidates, key=lambda item: (item["route_path"], item["source_path"]))
        boundary_candidates = sorted(boundary_candidates, key=lambda item: (item["boundary_kind"], item["source_path"]))
        dependency_edges = sorted(dependency_edges, key=lambda item: (item["source"], item["target"]))

        context.storage.write_registry(self.engine_id, "signals", signals)
        artifacts.append(context.storage.write_artifact(self.engine_id, "inventory", "scanner_inventory.json", inventory))
        artifacts.append(context.storage.write_artifact(self.engine_id, "routes", "route_candidates.json", route_candidates))
        artifacts.append(context.storage.write_artifact(self.engine_id, "boundaries", "boundary_candidates.json", boundary_candidates))
        artifacts.append(
            context.storage.write_artifact(
                self.engine_id,
                "graph",
                "dependency_graph.json",
                {"nodes": sorted({edge["source"] for edge in dependency_edges}), "edges": dependency_edges},
            )
        )
        metrics = {
            "files_scanned": len(inventory),
            "python_files": python_files,
            "frontend_surface_files": frontend_surface_files,
            "signals_emitted": len(signals),
            "parse_errors": parse_errors,
            "route_candidate_count": len(route_candidates),
            "boundary_candidate_count": len(boundary_candidates),
            "dependency_edge_count": len(dependency_edges),
            "skipped_noncanonical_surface_count": skipped_noncanonical_surface_count,
            **discovery_stats,
        }
        artifacts.append(context.storage.write_artifact(self.engine_id, "metrics", "scanner_metrics.json", metrics))
        context.event_bus.emit(
            name="scanner.completed",
            producer=self.engine_id,
            target=str(context.paths.target),
            payload=metrics,
        )
        emitted_events.append("scanner.completed")

        summary = build_execution_summary(
            execution_id=context.execution_id,
            engine_id=self.engine_id,
            stage=self.stage,
            status="ok",
            started_at=started_at,
            finished_at=context.execution_time,
            metrics=metrics,
            registries_written=context.storage.written_registries(self.engine_id),
            artifacts=artifacts,
            events=emitted_events,
        )
        return EngineRunResult(execution_summary=summary)
