from __future__ import annotations

import json
from urllib.request import Request, urlopen

from forgeos.shared.pyside6_glass.integration import (
    InProcessIntegrationAdapter,
    IntegrationCommandEnvelope,
    IntegrationQueryEnvelope,
    IntegrationService,
    IntegrationSnapshotRequest,
    LocalHttpIntegrationAdapter,
    LocalHttpIntegrationConfig,
)


def _create_demo_service() -> IntegrationService:
    service = IntegrationService(debug=False)
    state = {
        "workspace_id": "workspace-demo",
        "active_view": "overview",
        "item_count": 0,
        "panel_states": {
            "main": "visible",
            "side": "visible",
        },
        "items": {},
    }

    def command_upsert_item(envelope: IntegrationCommandEnvelope) -> dict[str, object]:
        item_id = str(envelope.payload.get("item_id") or "").strip()
        if not item_id:
            raise ValueError("item_id is required")
        item_payload = envelope.payload.get("item") or {}
        if not isinstance(item_payload, dict):
            raise ValueError("item must be a mapping")
        state["items"][item_id] = dict(item_payload)
        state["item_count"] = len(state["items"])
        return {"item_id": item_id, "item_count": state["item_count"]}

    def command_set_panel_state(envelope: IntegrationCommandEnvelope) -> dict[str, object]:
        panel_id = str(envelope.payload.get("panel_id") or "").strip()
        panel_state = str(envelope.payload.get("state") or "").strip()
        if not panel_id:
            raise ValueError("panel_id is required")
        if not panel_state:
            raise ValueError("state is required")
        state["panel_states"][panel_id] = panel_state
        return {"panel_id": panel_id, "state": panel_state}

    def query_summary(_envelope: IntegrationQueryEnvelope) -> dict[str, object]:
        return {
            "workspace_id": state["workspace_id"],
            "active_view": state["active_view"],
            "item_count": state["item_count"],
            "panel_states": dict(state["panel_states"]),
        }

    def snapshot_workspace(_request: IntegrationSnapshotRequest) -> dict[str, object]:
        return {
            "workspace": {
                "workspace_id": state["workspace_id"],
                "active_view": state["active_view"],
                "panel_states": dict(state["panel_states"]),
                "item_count": state["item_count"],
            }
        }

    service.register_command(
        "workspace.item.upsert",
        command_upsert_item,
        required_capabilities=("workspace.write",),
        description="Insert or replace a generic workspace item.",
    )
    service.register_command(
        "workspace.panel.state.set",
        command_set_panel_state,
        required_capabilities=("workspace.write",),
        description="Set panel state using neutral workspace contract.",
    )
    service.register_query(
        "workspace.summary.get",
        query_summary,
        description="Read workspace summary payload.",
    )
    service.register_snapshot_provider(
        "workspace",
        snapshot_workspace,
        description="Get current workspace snapshot.",
    )
    return service


def run_demo() -> int:
    service = _create_demo_service()
    inproc = InProcessIntegrationAdapter(service)

    command_payload = {
        "command": "workspace.item.upsert",
        "payload": {"item_id": "alpha", "item": {"title": "First Item", "status": "active"}},
        "context": {"client_id": "demo-client", "capabilities": ["workspace.write"]},
        "idempotency_key": "item-alpha-upsert-v1",
    }
    command_response = inproc.command(command_payload)
    command_response_repeat = inproc.command(command_payload)

    query_response = inproc.query(
        {
            "query": "workspace.summary.get",
            "params": {},
            "context": {"client_id": "demo-client"},
        }
    )
    snapshot_response = inproc.snapshot({"snapshot_id": "workspace", "context": {"client_id": "demo-client"}})
    events_response = inproc.poll_events()
    contracts_response = inproc.contracts()
    event_stream_frame = inproc.event_stream_once()

    print("INPROC_COMMAND:", json.dumps(command_response, indent=2, ensure_ascii=True))
    print("INPROC_COMMAND_REPEAT:", json.dumps(command_response_repeat, indent=2, ensure_ascii=True))
    print("INPROC_QUERY:", json.dumps(query_response, indent=2, ensure_ascii=True))
    print("INPROC_SNAPSHOT:", json.dumps(snapshot_response, indent=2, ensure_ascii=True))
    print("INPROC_EVENTS:", json.dumps(events_response, indent=2, ensure_ascii=True))
    print("INPROC_CONTRACTS:", json.dumps(contracts_response, indent=2, ensure_ascii=True))
    print("INPROC_EVENT_STREAM_FRAME:", event_stream_frame.strip())

    http = LocalHttpIntegrationAdapter(service, LocalHttpIntegrationConfig(host="127.0.0.1", port=0, debug=False))
    with http:
        query_body = json.dumps(
            {
                "query": "workspace.summary.get",
                "params": {},
                "context": {"client_id": "http-demo"},
            },
            ensure_ascii=True,
        ).encode("utf-8")
        request = Request(
            f"{http.base_url}/v1/query",
            data=query_body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=2.0) as response:  # noqa: S310 - local-only adapter
            http_query = json.loads(response.read().decode("utf-8"))
        with urlopen(f"{http.base_url}/v1/contracts", timeout=2.0) as response:  # noqa: S310 - local-only adapter
            http_contracts = json.loads(response.read().decode("utf-8"))
        with urlopen(f"{http.base_url}/v1/events/stream?since=0&limit=5", timeout=2.0) as response:  # noqa: S310
            http_sse_frame = response.read().decode("utf-8")
        print("HTTP_QUERY:", json.dumps(http_query, indent=2, ensure_ascii=True))
        print("HTTP_CONTRACTS:", json.dumps(http_contracts, indent=2, ensure_ascii=True))
        print("HTTP_SSE_FRAME:", http_sse_frame.strip())

    return 0


if __name__ == "__main__":
    raise SystemExit(run_demo())
