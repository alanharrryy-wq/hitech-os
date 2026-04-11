from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pya.contracts.base import deterministic_id, utc_now_z
from pya.kernel.config import RuntimeConfig
from pya.kernel.events import EventBus
from pya.kernel.storage import GovernedStorage
from pya.system.root_manifest import get_root_manifest


@dataclass
class RuntimePaths:
    root: Path
    target: Path
    out: Path
    reports: Path
    registries: Path
    indices: Path
    snapshots: Path
    deltas: Path
    traces: Path
    annotations: Path
    logs: Path
    artifacts: Path


@dataclass
class RuntimeContext:
    config: RuntimeConfig
    paths: RuntimePaths
    execution_id: str
    execution_time: str
    root_manifest: dict[str, object]
    storage: GovernedStorage
    event_bus: EventBus

    @classmethod
    def build(cls, *, root: Path, target: Path, out: Path, strict: bool = True, switch_overrides: dict[str, bool] | None = None, execution_time: str | None = None) -> "RuntimeContext":
        root = root.expanduser().resolve()
        target = target.expanduser().resolve()
        out = out.expanduser().resolve()
        execution_time = execution_time or utc_now_z()
        execution_id = deterministic_id("run", root, target, out, execution_time)
        paths = RuntimePaths(
            root=root,
            target=target,
            out=out,
            reports=out / "reports",
            registries=out / "registries",
            indices=out / "indices",
            snapshots=out / "snapshots",
            deltas=out / "deltas",
            traces=out / "traces",
            annotations=out / "annotations",
            logs=out / "logs",
            artifacts=out / "artifacts",
        )
        for path in paths.__dict__.values():
            Path(path).mkdir(parents=True, exist_ok=True)
        config = RuntimeConfig(root=root, target=target, out=out, strict=strict, switch_overrides=dict(switch_overrides or {}))
        storage = GovernedStorage(paths=paths, execution_id=execution_id, timestamp=execution_time)
        event_bus = EventBus(paths.traces, execution_id=execution_id, timestamp=execution_time)
        return cls(
            config=config,
            paths=paths,
            execution_id=execution_id,
            execution_time=execution_time,
            root_manifest=get_root_manifest(),
            storage=storage,
            event_bus=event_bus,
        )
