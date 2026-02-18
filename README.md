# HITECH-OS

HITECH-OS is a deterministic monorepo skeleton for a mixed TypeScript + Python stack.

## Stack

- Package manager: PNPM workspaces
- Task runner: Turborepo
- Web app: Vite + React + TypeScript
- Core API: Node + TypeScript + Fastify
- AI Agent: Python + FastAPI + pydantic
- Shared contracts: Zod + generated JSON Schemas
- Shared UI: lightweight React component package
- Repo health gate: offline Node script

## Principles

- Deterministic artifacts and ordering
- Feature flags default OFF in all surfaces
- No historical baggage in bootstrap
- No binary or dump artifacts under `src/**`
- Every service/package has clear boundary and contract

## Quick start (offline-safe)

1. Ensure runtimes are available:
   - `node -v`
   - `pnpm -v` (optional but recommended)
   - `python --version` (for AI agent)
2. Install dependencies (if pnpm is available):
   - `pnpm install`
3. Generate docs index + schemas:
   - `pnpm docs`
   - `pnpm schema:gen`
4. Run quality checks:
   - `pnpm health`
   - `pnpm turbo:typecheck`

## If PNPM Is Missing

Do not install package managers during restricted/offline bootstrap. You can still run baseline checks directly:

- `node tools/scripts/generate_docs_index.mjs`
- `node packages/contracts/tools/gen_schemas.mjs --check`
- `node tools/health/src/check_repo_health.mjs`
- `node services/core-api/scripts/smoke-core-api.mjs` (skips safely if deps are not installed)

## Monorepo layout

- `apps/web` React app
- `apps/demo-engine` minimal placeholder app
- `services/core-api` Node Fastify API
- `services/ai-agent` Python FastAPI service
- `packages/contracts` Zod schemas + generated JSON Schema
- `packages/ui-kit` shared UI components
- `packages/tooling` shared lint/type presets
- `tools/health` guardrail checker
- `tools/scripts` repo utilities
- `docs` project law and maps

## Deterministic smoke checks

- `node tools/health/src/check_repo_health.mjs`
- `node packages/contracts/tools/gen_schemas.mjs --check`

## Notes

- This repo is scaffold-only and intentionally avoids network-time generation.
- If `pnpm` is missing, the repository remains inspectable and scripts can be run directly with `node` where possible.
