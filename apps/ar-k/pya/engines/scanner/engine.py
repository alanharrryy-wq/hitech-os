from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pya.contracts.engine_contracts import build_execution_summary
from pya.contracts.enums import Severity, State
from pya.contracts.signal_contract import build_signal
from pya.kernel.discovery import discover_files
from pya.kernel.identity import normalize_relpath
from pya.kernel.models import EngineRunResult
from pya.system.state_model import validate_state_producer

from .parser import classify_file, parse_python_file


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
        python_files = 0
        parse_errors = 0

        for path in discover_files(context.paths.target):
            relative_path = normalize_relpath(path, context.paths.target)
            file_kind = classify_file(relative_path)
            inventory.append(
                {
                    "path": relative_path,
                    "kind": file_kind,
                    "size_bytes": path.stat().st_size,
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
                    evidence={"kind": file_kind},
                    snapshot_id=context.execution_id,
                    created_at=context.execution_time,
                    tags=[file_kind],
                )
            )

            if file_kind != "python":
                continue

            python_files += 1
            module_name = relative_path[:-3].replace("/", ".")
            parsed = parse_python_file(path)
            if parsed["ok"]:
                validate_state_producer(self.engine_id, State.CANDIDATE.value)
                signals.append(
                    build_signal(
                        signal_type="module_candidate",
                        source_path=relative_path,
                        producer=self.engine_id,
                        state=State.CANDIDATE.value,
                        confidence=0.8,
                        evidence={
                            "imports": parsed["imports"],
                            "exports": parsed["exports"],
                            "kind": file_kind,
                        },
                        snapshot_id=context.execution_id,
                        created_at=context.execution_time,
                        tags=[file_kind, "module"],
                        module_name=module_name,
                    )
                )
                for imported in parsed["imports"]:
                    dependency_edges.append({"source": module_name, "target": imported})
                    signals.append(
                        build_signal(
                            signal_type="import_edge",
                            source_path=relative_path,
                            producer=self.engine_id,
                            state=State.OBSERVED.value,
                            confidence=0.7,
                            evidence={"target_import": imported, "module_name": module_name},
                            snapshot_id=context.execution_id,
                            created_at=context.execution_time,
                            tags=["dependency"],
                        )
                    )
            else:
                parse_errors += 1
                validate_state_producer(self.engine_id, State.AMBIGUOUS.value)
                signals.append(
                    build_signal(
                        signal_type="module_candidate",
                        source_path=relative_path,
                        producer=self.engine_id,
                        state=State.AMBIGUOUS.value,
                        confidence=0.2,
                        evidence={"parse_error": parsed["error"], "kind": file_kind},
                        snapshot_id=context.execution_id,
                        created_at=context.execution_time,
                        tags=[file_kind, "parse_error"],
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

        context.storage.write_registry(self.engine_id, "signals", signals)
        artifacts.append(context.storage.write_artifact(self.engine_id, "inventory", "scanner_inventory.json", inventory))
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
            "signals_emitted": len(signals),
            "parse_errors": parse_errors,
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
