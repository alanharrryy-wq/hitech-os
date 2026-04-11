# @hitech/core-api

Deterministic Node HTTP service bridging job execution to `ai-agent` over localhost HTTP.

## Endpoints

- `GET /health`
- `GET /flags`
- `GET /capabilities`
- `GET /governance/stage/S1`
- `GET /governance/runs`
- `GET /governance/runs/:runId/artifacts`
- `POST /jobs`
- `GET /jobs/:id`
- `POST /jobs/:id/run`

## Notes

- Feature flags are OFF by default.
- Queue ordering is deterministic by `requestedAtUtc`, then `jobId`, then insertion sequence.
- `POST /jobs/:id/run` only executes when the job `flags.enableAiExecution` is `true`.
- Runtime has zero external dependencies; execute with `node --experimental-strip-types src/index.ts`.
- Governance run listing and artifact manifest routes are read-only and deterministic.
