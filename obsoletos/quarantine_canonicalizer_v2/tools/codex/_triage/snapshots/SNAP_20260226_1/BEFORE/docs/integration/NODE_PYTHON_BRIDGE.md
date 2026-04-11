# NODE PYTHON BRIDGE

Version: 1.0.0  
Last Updated: 2026-02-18

## Purpose

Define deterministic integration between:

- `services/core-api` (Node)
- `services/ai-agent` (Python)
- shared contracts in `packages/contracts`

Bridge rule: communication only via local HTTP (`127.0.0.1`). No direct runtime imports across service boundaries.

## Runtime Topology

1. Client sends job payload to `core-api` `POST /jobs`.
2. Core API validates and enqueues deterministic job state.
3. Client triggers execution with `POST /jobs/:id/run`.
4. Core API calls `ai-agent` `POST /jobs/run`.
5. AI agent returns deterministic `JobResult`.
6. Core API stores result and exposes `GET /jobs/:id`.

## Endpoints

### core-api

- `POST /jobs`
- `GET /jobs/:id`
- `POST /jobs/:id/run`
- `GET /capabilities`
- `GET /health`
- `GET /flags`

### ai-agent

- `GET /capabilities`
- `POST /jobs/run`
- `GET /health`

## Determinism Rules

1. Job ordering in queue is deterministic: `requestedAtUtc`, then `jobId`, then insertion sequence.
2. AI handler output depends only on request payload.
3. Logs use ordered `seq` values.
4. No randomness, no external network, no wall-clock output in job results.
5. Feature flags are off by default in request normalization.

## Feature Flags

Default flags from contracts:

- `enableAiExecution: false`
- `enableCapabilitiesProxy: false`
- `enableExperimentalUi: false`
- `enableHealthDashboard: false`

Execution flow requires `enableAiExecution: true` per job request.

## Failure Behavior

- If ai-agent is down, core-api returns deterministic failure payload and marks job as failed.
- If feature flag is off, core-api returns `FEATURE_FLAG_DISABLED` and keeps queue state deterministic.

## Offline-first Notes

- No dependency installation is required to inspect code.
- Runtime scripts use built-in Node and Python stdlib facilities.
- All smoke flows run on localhost only.
