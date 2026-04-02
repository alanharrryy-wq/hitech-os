from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

from forgeos.shared.pyside6_glass.integration import (
    GlassRuntimeIntegrationBridge,
    InProcessIntegrationAdapter,
    IntegrationCommandEnvelope,
    IntegrationQueryEnvelope,
    IntegrationService,
    IntegrationSnapshotRequest,
    IntegrationValidationError,
    LocalHttpIntegrationAdapter,
    LocalHttpIntegrationConfig,
)
from forgeos.shared.pyside6_glass.runtime import GlassWorkspaceRuntime

from ..runtime.engine import NEXUS_STAGE_SEQUENCE, NexusRuntimeEngine


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_NEXUS_WORKSPACE_STATE_PATH = REPO_ROOT / "tools" / "_local" / "tmp" / "nexus_workspace_state.json"


def _required_text(payload: dict[str, Any], key: str) -> str:
    value = str(payload.get(key) or "").strip()
    if not value:
        raise IntegrationValidationError(f"{key} is required")
    return value


def register_nexus_contracts(
    service: IntegrationService,
    engine: NexusRuntimeEngine,
    *,
    namespace: str = "nexus",
    required_write_capabilities: tuple[str, ...] = ("nexus.write",),
) -> None:
    ns = str(namespace or "nexus").strip().lower() or "nexus"
    write_caps = tuple(str(item).strip() for item in required_write_capabilities if str(item).strip())

    def _command_record_upsert(envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        record_id = _required_text(envelope.payload, "record_id")
        record_payload = envelope.payload.get("record")
        if not isinstance(record_payload, dict):
            raise IntegrationValidationError("record must be a mapping")
        actor = envelope.context.client_id or "desktop-client"
        record = engine.upsert_record(record_id, record_payload, actor=actor)
        service.emit_event(
            f"{ns}.record.upserted",
            {"record_id": record_id, "stage": record.get("stage"), "owner": record.get("owner")},
            topic=ns,
            context=envelope.context,
            correlation_id=envelope.meta.request_id,
            source="nexus.integration",
        )
        return {"record": record}

    def _command_record_stage_set(envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        record_id = _required_text(envelope.payload, "record_id")
        stage = _required_text(envelope.payload, "stage").lower()
        if stage not in NEXUS_STAGE_SEQUENCE:
            raise IntegrationValidationError(f"unsupported stage '{stage}'")
        note = str(envelope.payload.get("note") or "")
        actor = envelope.context.client_id or "desktop-client"
        record = engine.set_record_stage(record_id, stage, actor=actor, note=note)
        service.emit_event(
            f"{ns}.record.stage_changed",
            {"record_id": record_id, "stage": stage},
            topic=ns,
            context=envelope.context,
            correlation_id=envelope.meta.request_id,
            source="nexus.integration",
        )
        return {"record": record}

    def _command_approval_state_set(envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        record_id = _required_text(envelope.payload, "record_id")
        state = _required_text(envelope.payload, "state").lower()
        note = str(envelope.payload.get("note") or "")
        actor = envelope.context.client_id or "desktop-client"
        approval = engine.set_approval_state(record_id, state, actor=actor, note=note)
        service.emit_event(
            f"{ns}.approval.state_changed",
            {"record_id": record_id, "state": state},
            topic=ns,
            context=envelope.context,
            correlation_id=envelope.meta.request_id,
            source="nexus.integration",
        )
        return {"approval": approval}

    def _command_note_append(envelope: IntegrationCommandEnvelope) -> dict[str, Any]:
        record_id = _required_text(envelope.payload, "record_id")
        note = _required_text(envelope.payload, "note")
        actor = envelope.context.client_id or "desktop-client"
        result = engine.append_note(record_id, note, actor=actor)
        service.emit_event(
            f"{ns}.note.appended",
            {"record_id": record_id, "note": note},
            topic=ns,
            context=envelope.context,
            correlation_id=envelope.meta.request_id,
            source="nexus.integration",
        )
        return result

    def _query_summary(_envelope: IntegrationQueryEnvelope) -> dict[str, Any]:
        return engine.summary()

    def _query_records(_envelope: IntegrationQueryEnvelope) -> dict[str, Any]:
        return {"records": engine.list_records()}

    def _query_record(envelope: IntegrationQueryEnvelope) -> dict[str, Any]:
        record_id = _required_text(envelope.params, "record_id")
        record = engine.get_record(record_id)
        return {"record_id": record_id, "exists": record is not None, "record": record or {}}

    def _query_approvals(_envelope: IntegrationQueryEnvelope) -> dict[str, Any]:
        return {"approvals": engine.list_approvals()}

    def _query_health(_envelope: IntegrationQueryEnvelope) -> dict[str, Any]:
        return engine.health_snapshot()["health"]

    def _snapshot_workspace(_request: IntegrationSnapshotRequest) -> dict[str, Any]:
        return engine.workspace_snapshot()

    def _snapshot_timeline(request: IntegrationSnapshotRequest) -> dict[str, Any]:
        raw_limit = request.selector.get("limit") if isinstance(request.selector, dict) else None
        try:
            limit = int(raw_limit) if raw_limit is not None else 60
        except Exception:  # noqa: BLE001
            limit = 60
        return engine.timeline_snapshot(limit=limit)

    def _snapshot_health(_request: IntegrationSnapshotRequest) -> dict[str, Any]:
        return engine.health_snapshot()

    service.register_command(
        f"{ns}.record.upsert",
        _command_record_upsert,
        required_capabilities=write_caps,
        description="Upsert Nexus runtime record.",
    )
    service.register_command(
        f"{ns}.record.stage.set",
        _command_record_stage_set,
        required_capabilities=write_caps,
        description="Set Nexus runtime record stage.",
    )
    service.register_command(
        f"{ns}.approval.state.set",
        _command_approval_state_set,
        required_capabilities=write_caps,
        description="Set Nexus runtime approval state.",
    )
    service.register_command(
        f"{ns}.note.append",
        _command_note_append,
        required_capabilities=write_caps,
        description="Append note to Nexus runtime record.",
    )
    service.register_query(
        f"{ns}.summary.get",
        _query_summary,
        description="Get Nexus summary data.",
    )
    service.register_query(
        f"{ns}.records.list",
        _query_records,
        description="List Nexus records.",
    )
    service.register_query(
        f"{ns}.record.get",
        _query_record,
        description="Get one Nexus record by id.",
    )
    service.register_query(
        f"{ns}.approvals.list",
        _query_approvals,
        description="List Nexus approval states.",
    )
    service.register_query(
        f"{ns}.health.get",
        _query_health,
        description="Get Nexus runtime health summary.",
    )
    service.register_snapshot_provider(
        f"{ns}.workspace",
        _snapshot_workspace,
        description="Snapshot with summary, records and approvals.",
    )
    service.register_snapshot_provider(
        f"{ns}.timeline",
        _snapshot_timeline,
        description="Snapshot with recent timeline entries.",
    )
    service.register_snapshot_provider(
        f"{ns}.health",
        _snapshot_health,
        description="Snapshot with health runtime payload.",
    )


@dataclass(slots=True)
class NexusHostedModule:
    namespace: str
    runtime: GlassWorkspaceRuntime
    engine: NexusRuntimeEngine
    service: IntegrationService
    adapter: InProcessIntegrationAdapter
    runtime_bridge: GlassRuntimeIntegrationBridge
    workspace_state_path: Path
    session_id: str = field(default_factory=lambda: str(uuid4()))
    _http_adapter: LocalHttpIntegrationAdapter | None = field(default=None, init=False)

    def context(self, *, capabilities: tuple[str, ...] = ()) -> dict[str, Any]:
        return {
            "client_id": "nexus.desktop.host",
            "session_id": self.session_id,
            "origin": "desktop",
            "workspace_id": self.engine.workspace_id,
            "device_hint": "desktop",
            "capabilities": list(capabilities),
            "metadata": {"module": "nexus"},
        }

    def command(
        self,
        command: str,
        payload: dict[str, Any] | None = None,
        *,
        capabilities: tuple[str, ...] = ("nexus.write",),
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        return self.adapter.command(
            {
                "command": str(command),
                "payload": dict(payload or {}),
                "context": self.context(capabilities=capabilities),
                "idempotency_key": idempotency_key,
            }
        )

    def query(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        *,
        capabilities: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        return self.adapter.query(
            {
                "query": str(query),
                "params": dict(params or {}),
                "context": self.context(capabilities=capabilities),
            }
        )

    def snapshot(
        self,
        snapshot_id: str,
        selector: dict[str, Any] | None = None,
        *,
        capabilities: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        return self.adapter.snapshot(
            {
                "snapshot_id": str(snapshot_id),
                "selector": dict(selector or {}),
                "context": self.context(capabilities=capabilities),
            }
        )

    def poll_events(self, *, since_sequence: int | None = None, limit: int = 100) -> dict[str, Any]:
        return self.adapter.poll_events(since_sequence=since_sequence, limit=limit)

    def contracts(self) -> dict[str, Any]:
        return self.adapter.contracts()

    def save_workspace_state(self) -> Path | None:
        self.workspace_state_path.parent.mkdir(parents=True, exist_ok=True)
        return self.runtime.save_workspace_state(path=self.workspace_state_path)

    def load_workspace_state(self) -> bool:
        state = self.runtime.load_workspace_state(path=self.workspace_state_path)
        return state is not None

    def start_local_http(self, *, host: str = "127.0.0.1", port: int = 0) -> str:
        if self._http_adapter is None:
            self._http_adapter = LocalHttpIntegrationAdapter(
                self.service,
                LocalHttpIntegrationConfig(host=host, port=int(port), debug=False),
            )
        return self._http_adapter.start()

    def stop_local_http(self) -> None:
        if self._http_adapter is None:
            return
        self._http_adapter.stop()
        self._http_adapter = None


def create_nexus_hosted_module(
    runtime: GlassWorkspaceRuntime,
    *,
    namespace: str = "nexus",
    workspace_state_path: Path | None = None,
    debug: bool = False,
) -> NexusHostedModule:
    service = IntegrationService(debug=debug)
    runtime_bridge = GlassRuntimeIntegrationBridge(
        runtime,
        service=service,
        namespace="workspace",
        required_write_capabilities=("workspace.write",),
        register_defaults=True,
    )
    engine = NexusRuntimeEngine(workspace_id=f"{namespace}-workspace")
    register_nexus_contracts(
        service,
        engine,
        namespace=namespace,
        required_write_capabilities=("nexus.write",),
    )
    adapter = InProcessIntegrationAdapter(service)
    state_path = workspace_state_path or DEFAULT_NEXUS_WORKSPACE_STATE_PATH
    return NexusHostedModule(
        namespace=namespace,
        runtime=runtime,
        engine=engine,
        service=service,
        adapter=adapter,
        runtime_bridge=runtime_bridge,
        workspace_state_path=Path(state_path),
    )

