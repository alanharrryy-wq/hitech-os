# MASTER_MAP

Version: 1.0.0
Last Updated: 2026-02-18

This file maps ownership, boundaries, and runtime entry points.

## Top-level map

| Path | Type | Purpose |
| --- | --- | --- |
| `apps/web` | app | User-facing React frontend |
| `apps/demo-engine` | app | Placeholder scaffold for future demo orchestration |
| `services/core-api` | service | Node Fastify API, contract gateway |
| `services/ai-agent` | service | Python FastAPI deterministic AI stub |
| `packages/contracts` | package | Shared Zod contracts + JSON schema artifacts |
| `packages/ui-kit` | package | Shared lightweight React components |
| `packages/tooling` | package | Shared lint/format/type presets |
| `tools/health` | tool | Repository guardrail and anti-artifact checks |
| `tools/scripts` | tool | Utility scripts (docs index generation) |
| `docs` | docs | Law, notebook, and map |

## Ownership model

| Area | Primary Owner | Secondary Owner |
| --- | --- | --- |
| Contracts | Platform | Core API |
| Core API | Backend | Platform |
| AI Agent | Applied AI | Backend |
| Web | Frontend | Product |
| UI Kit | Frontend | Platform |
| Health Tooling | Platform | DevEx |
| Documentation | Platform | All teams |

## Runtime entry points

### apps/web

- Dev: `pnpm --filter @hitech/web dev`
- Build: `pnpm --filter @hitech/web build`
- Typecheck: `pnpm --filter @hitech/web typecheck`

### services/core-api

- Dev: `pnpm --filter @hitech/core-api dev`
- Build: `pnpm --filter @hitech/core-api build`
- Smoke: `node services/core-api/scripts/smoke-core-api.mjs`

### services/ai-agent

- Run: `uvicorn app.main:app --host 127.0.0.1 --port 8001`

### contracts

- Generate schemas: `node packages/contracts/tools/gen_schemas.mjs`
- Check mode: `node packages/contracts/tools/gen_schemas.mjs --check`

### health

- Repo gate: `node tools/health/src/check_repo_health.mjs`

## Dependency graph (high level)

1. `apps/web` -> `packages/ui-kit`, `packages/contracts`
2. `services/core-api` -> `packages/contracts`
3. `services/ai-agent` -> mirrored schema shapes (no runtime TS import)
4. `packages/ui-kit` -> React only
5. `tools/health` -> Node built-ins only

Constraint: `packages/*` cannot import from `apps/*` or `services/*`.

## Directory details

### `apps/web`

- `src/main.tsx`: bootstraps React.
- `src/App.tsx`: top-level page shell.
- `src/pages/HomePage.tsx`: base overview page.
- `src/pages/HealthPage.tsx`: health dashboard calling core API.
- `src/lib/api.ts`: typed fetch helpers.
- `src/styles.css`: app-level theme and layout.

### `apps/demo-engine`

- `README.md`: placeholder scope.
- `package.json`: minimal scripts for future task integration.

### `services/core-api`

- `src/server.ts`: Fastify server factory and route registration.
- `src/routes/*.ts`: endpoint handlers.
- `src/lib/*.ts`: pure utilities and deterministic helpers.
- `src/index.ts`: runtime startup entry point.
- `src/__tests__/*.test.ts`: deterministic unit tests.
- `scripts/smoke-core-api.mjs`: local smoke flow.

### `services/ai-agent`

- `app/main.py`: FastAPI app and routes.
- `app/models.py`: pydantic models aligned to contract shapes.
- `app/engine.py`: deterministic stub execution.
- `tests/test_engine.py`: simple deterministic tests.
- `pyproject.toml`: Python package and lint config.

### `packages/contracts`

- `src/*.ts`: Zod schema definitions and exports.
- `src/index.ts`: public entry.
- `schemas/generated/*.json`: committed generated JSON Schema files.
- `tools/gen_schemas.ts`: TypeScript generator entry.
- `tools/gen_schemas.mjs`: Node executable generator.

### `packages/ui-kit`

- `src/components/*.tsx`: primitive UI components.
- `src/index.ts`: strict export surface.
- `src/styles.css`: minimal reusable styles.

### `packages/tooling`

- `eslint/base.cjs`: shared lint rules.
- `prettier/prettier.config.cjs`: shared formatting rules.
- `tsconfig/base.json`: shared TS compiler baseline.

### `tools/health`

- `src/check_repo_health.mjs`: anti-artifact deterministic checker.
- `package.json`: runnable scripts and metadata.

### `tools/scripts`

- `generate_docs_index.mjs`: deterministic docs index generator.

## Task graph expectations

All Node packages should expose scripts:

- `build`
- `lint`
- `test`
- `typecheck`
- optional `dev`

Turbo task behavior:

1. `build` depends on upstream `build`.
2. `test` depends on upstream `build` and `test`.
3. `health` is uncached and local.
4. `docs` outputs `docs/DOCS_INDEX.md`.

## Guardrail map

| Guardrail | Enforced by | Scope |
| --- | --- | --- |
| Feature flags default OFF | contracts + API + web fallback | runtime behavior |
| No dumps under src | health script + gitignore | repository hygiene |
| Deterministic generated schema | generator check mode | contract artifacts |
| No hidden service coupling | module boundaries | architecture |

## Change impact map

When touching `packages/contracts`:

1. Re-run schema generation.
2. Check core-api compile and tests.
3. Check ai-agent models for drift.
4. Check web flag and API type usage.

When touching `services/core-api`:

1. Re-run core-api unit tests.
2. Run local smoke script.
3. Verify `/flags` returns all known defaults.

When touching `services/ai-agent`:

1. Validate models match schema field names.
2. Run local FastAPI startup.
3. Verify deterministic `jobs/run` response.

When touching `tools/health`:

1. Run against repo root.
2. Validate both success and failure path determinism.

## Backlog placeholders

- `apps/demo-engine`: wire future demo orchestration UI.
- `packages/tooling`: extend shared TS/ESLint presets across all packages.
- `.github/workflows`: add full CI when online package install policy is defined.

## Non-goals at bootstrap

1. No production deployment manifests.
2. No database integration.
3. No external queue broker.
4. No secret manager integration.
5. No binary asset pipelines.
