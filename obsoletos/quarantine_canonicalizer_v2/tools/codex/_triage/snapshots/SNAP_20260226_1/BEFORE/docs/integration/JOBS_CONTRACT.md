# JOBS CONTRACT

Version: 1.1.0  
Last Updated: 2026-02-18

## Contract Source

- Canonical schemas: `packages/contracts/src/*.ts`
- Generated schemas: `packages/contracts/schemas/generated/*.json`
- Python model mirror: `services/ai-agent/app/models.py`

## Core API Routes

1. `GET /health`
2. `GET /flags`
3. `GET /capabilities`
4. `POST /jobs`
5. `GET /jobs/:id`
6. `POST /jobs/:id/run`

Determinism note:

- `CORE_API_FIXED_NOW_UTC` may be set for deterministic smoke/runtime timestamping.
- When unset, production runtime uses system UTC clock.

## Types

### FeatureFlags

```json
{
  "enableAiExecution": false,
  "enableCapabilitiesProxy": false,
  "enableExperimentalUi": false,
  "enableHealthDashboard": false
}
```

### JobRequest

```json
{
  "jobId": "job-123",
  "kind": "summarize_text",
  "input": { "text": "hello world" },
  "requestedAtUtc": "2026-01-01T00:00:00.000Z",
  "flags": {
    "enableAiExecution": true,
    "enableCapabilitiesProxy": false,
    "enableExperimentalUi": false,
    "enableHealthDashboard": false
  }
}
```

Fields:

1. `jobId`: stable caller-provided ID.
2. `kind`: `echo | summarize_text | extract_keywords`.
3. `input`: JSON-compatible object.
4. `requestedAtUtc`: ISO date-time string.
5. `flags`: feature flag object.

### JobResult

```json
{
  "jobId": "job-123",
  "kind": "summarize_text",
  "status": "completed",
  "output": { "summary": "hello world" },
  "logs": [
    {
      "seq": 0,
      "level": "info",
      "event": "job.received",
      "message": "job request accepted",
      "atUtc": "2026-01-01T00:00:00.000Z",
      "details": {}
    }
  ],
  "finishedAtUtc": "2026-01-01T00:00:00.000Z"
}
```

Fields:

1. `status`: `queued | running | completed | failed`.
2. `output`: deterministic handler output object.
3. `logs`: ordered structured logs.
4. `finishedAtUtc`: deterministic completion timestamp or `null`.

### AgentCapabilities

```json
{
  "serviceName": "ai-agent",
  "version": "0.2.0",
  "protocolVersion": "1.1.0",
  "deterministic": true,
  "supportedJobKinds": ["echo", "extract_keywords", "summarize_text"],
  "maxInputChars": 12000,
  "defaults": {
    "enableAiExecution": false,
    "enableCapabilitiesProxy": false,
    "enableExperimentalUi": false,
    "enableHealthDashboard": false
  },
  "notes": ["Deterministic local handlers only"]
}
```

### HealthReport

```json
{
  "service": "core-api",
  "version": "0.2.0",
  "contractVersion": "1.1.0",
  "status": "ok",
  "timestampUtc": "2026-01-01T00:00:00.000Z",
  "checks": [{ "name": "contracts", "status": "ok", "message": "contract version 1.1.0" }]
}
```

## Versioning

1. Schema version file: `packages/contracts/schemas/generated/schema-version.json`.
2. Compatibility policy: `packages/contracts/docs/SCHEMA_VERSIONING.md`.
3. Generator check mode enforces deterministic output and expected file set.

## Contract Update Flow

1. Update Zod schemas.
2. Run `node packages/contracts/tools/gen_schemas.mjs`.
3. Run `node packages/contracts/tools/gen_schemas.mjs --check`.
4. Update Python model mirror and tests.
