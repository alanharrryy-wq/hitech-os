# External Integration Boundary

This document defines the neutral ingress/egress architecture for future lightweight external clients.

## Scope

The integration boundary is for:

- command ingress (`do something`)
- query ingress (`read information`)
- snapshot ingress (`fetch structured state views`)
- event egress (`observe state changes/results`)

It is not a product-specific API.

## Module map

- `integration/contracts.py`
  - envelope and payload contracts
  - client/session context
  - structured error/response/event models
  - protocol version marker
- `integration/service.py`
  - application-facing command/query/snapshot dispatch
  - endpoint registration and capability checks
  - event emission and polling
  - diagnostics metadata
- `integration/adapters.py`
  - `InProcessIntegrationAdapter` (fully implemented)
  - `LocalHttpIntegrationAdapter` (local-only transport adapter)
- `integration/runtime_bridge.py`
  - bridge between desktop runtime and neutral integration contracts
  - exposes workspace operations as structured contracts

## Contracts

Inbound envelopes:

- `IntegrationCommandEnvelope`
- `IntegrationQueryEnvelope`
- `IntegrationSnapshotRequest`

Outbound payloads:

- `IntegrationResponse`
- `IntegrationError`
- `IntegrationEvent`

All envelopes carry:

- `meta.protocol_version`
- `meta.request_id`
- `meta.correlation_id` (optional)
- `meta.timestamp_utc`
- `meta.source`

All envelopes can include:

- `context.client_id`
- `context.session_id`
- `context.origin`
- `context.workspace_id`
- `context.device_hint`
- `context.capabilities`
- `context.metadata`

## Capability model

Each endpoint can declare required capabilities.

Examples:

- read endpoints: no capability required or read capability
- write endpoints: capability requirement such as `workspace.write`

Capability checks happen in `IntegrationService` before handler execution.

## Validation model

Validation occurs at two layers:

1. Envelope parsing (`from_payload`) rejects malformed payloads.
2. Endpoint handler validation rejects unsupported semantic inputs.

Errors are returned as structured `IntegrationResponse(ok=false, error=...)` payloads.

## Transport strategy

Transport is adapter-only:

- integration contracts/service do not depend on transport internals
- adapters only translate transport payloads into service dispatch calls

Current adapters:

- in-process: recommended for tests, local automation, desktop co-usage
- local HTTP: lightweight, local-only ingress for future web/mobile bridge tools
  - `POST /v1/command`
  - `POST /v1/query`
  - `POST /v1/snapshot`
  - `GET /v1/contracts`
  - `GET /v1/events`
  - `GET /v1/events/stream` (single SSE frame scaffold)

Future adapters (prepared, not implemented):

- websocket adapter scaffold
- IPC adapter

## Desktop coexistence

Desktop UI remains direct and local.

The integration boundary is additive:

- desktop can keep using runtime/template directly
- external clients can call integration contracts
- both paths share underlying runtime/application logic via bridge/service

## How a future lightweight web client connects

Recommended path:

1. app composes runtime/template as today
2. app creates `IntegrationService`
3. app attaches `GlassRuntimeIntegrationBridge(runtime, service, ...)`
4. app exposes one adapter (in-process for internal bridge tools, or local HTTP)
5. web client sends command/query/snapshot envelopes
6. client polls events or uses future live event adapter

This avoids direct widget coupling and keeps contracts versionable.

## Stability notes

Stable:

- envelope and response models
- service registration/dispatch contracts
- in-process adapter behavior
- runtime bridge public command/query/snapshot naming pattern
- local contracts/event polling routes

Evolving:

- advanced transport adapters (persistent websocket/SSE session model)
- richer policy/permission hooks
- live outbound channel adapters
