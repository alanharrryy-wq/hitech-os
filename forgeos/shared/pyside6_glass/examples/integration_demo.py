from __future__ import annotations

import json
from urllib.request import Request, urlopen

from forgeos.shared.pyside6_glass.integration import (
    InProcessIntegrationAdapter,
    LocalHttpIntegrationAdapter,
    LocalHttpIntegrationConfig,
    create_reference_workspace_service,
)


def _create_demo_service():
    service, _ = create_reference_workspace_service(debug=False, namespace="workspace")
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
