# SMOKE RUN

Last Updated: 2026-02-18

## Scope

Smoke verifies Node↔Python bridge over localhost with deterministic contracts.

## Preconditions

1. `node -v` works.
2. `python --version` works.
3. No dependency install is required for provided smoke scripts.

## Command Matrix

### Contracts

1. Generate schemas:
   - `node packages/contracts/tools/gen_schemas.mjs`
2. Check deterministic output:
   - `node packages/contracts/tools/gen_schemas.mjs --check`

### Unit tests

1. Core API tests:
   - `node --experimental-strip-types --test services/core-api/src/__tests__/*.test.ts`
2. AI agent tests:
   - `python -m unittest discover -s services/ai-agent/tests -p "test_*.py"`

### End-to-end smoke

1. Bridge smoke (starts both services, runs one job):
   - `node tools/scripts/smoke_node_python_bridge.mjs`
2. Core API local smoke:
   - `node services/core-api/scripts/smoke-core-api.mjs`
3. AI agent local smoke:
   - `python services/ai-agent/scripts/smoke_ai_agent.py`

### Health

1. Repository health gate:
   - `node tools/health/src/check_repo_health.mjs`

## Expected Smoke Flow

1. Start `ai-agent` (`127.0.0.1:8001`).
2. Start `core-api` (`127.0.0.1:3001`).
3. `POST /jobs` to core-api with `enableAiExecution=true`.
4. `POST /jobs/:id/run` from core-api to ai-agent.
5. `GET /jobs/:id` returns `status=completed`.
6. `GET /capabilities` returns deterministic capability payload.

## Troubleshooting

1. If `/health` never becomes ready, verify no port conflicts on `3001` and `8001`.
2. If `run` returns `FEATURE_FLAG_DISABLED`, ensure `flags.enableAiExecution` is true in the request.
3. If health reports schema violations, rerun contract generator and inspect `packages/contracts/schemas/generated`.
4. If Python tests fail on import path, run from repo root.
