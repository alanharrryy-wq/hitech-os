# NOTEBOOK

Version: 1.0.0
Status: Active operational notebook
Last Updated: 2026-02-18

## Mission

Build and evolve HITECH-OS as a deterministic, modular, mixed-language monorepo.

This notebook records operating assumptions, decision logs, and runbook snippets needed to keep execution disciplined.

## Baseline Operating Rules

1. Respect `docs/CONTRACT.md` at all times.
2. Keep feature flags OFF by default.
3. Keep generated artifacts deterministic and reviewable.
4. Keep source trees free from dump artifacts.
5. Favor explicit boundaries and typed contracts.

## Runtime Matrix

| Surface         | Runtime      | Required for baseline checks | Notes                              |
| --------------- | ------------ | ---------------------------- | ---------------------------------- |
| Node tooling    | Node 20+     | Yes                          | Needed for health and docs scripts |
| Package manager | PNPM 9+      | Recommended                  | Workspace orchestration            |
| Python service  | Python 3.11+ | Optional for full stack      | AI agent local service             |

## Local Workflow

### 1) Bootstrap

1. Clone or open repo root.
2. Verify runtimes:
   - `node -v`
   - `pnpm -v` (if installed)
   - `python --version`
3. If pnpm exists:
   - `pnpm install`

### 2) Deterministic generators

1. Regenerate docs index:
   - `node tools/scripts/generate_docs_index.mjs`
2. Regenerate contracts schema:
   - `node packages/contracts/tools/gen_schemas.mjs`

### 3) Guardrails

1. Run health check:
   - `node tools/health/src/check_repo_health.mjs`
2. Run optional monorepo tasks:
   - `pnpm turbo:lint`
   - `pnpm turbo:typecheck`
   - `pnpm turbo:test`

## Decision Log

### 2026-02-18 - Monorepo baseline selection

- Decision: Use PNPM workspace + Turborepo.
- Why: deterministic workspace orchestration and explicit task graph.
- Impact: all JS/TS packages expose normalized script names (`build/lint/test/typecheck/dev`).

### 2026-02-18 - Core API framework

- Decision: Fastify.
- Why: low overhead, good TypeScript support, straightforward JSON APIs.
- Impact: endpoint contracts stay simple and typed through `packages/contracts`.

### 2026-02-18 - Python AI agent framework

- Decision: FastAPI + pydantic.
- Why: strict request/response models and easy local server.
- Impact: schema mirror must stay aligned to TypeScript contracts.

### 2026-02-18 - Shared contracts source of truth

- Decision: Zod schemas + committed JSON Schema generation.
- Why: strong TS ergonomics and language-agnostic artifact output.
- Impact: schema generation step is mandatory after contract edits.

### 2026-02-18 - Guardrails strategy

- Decision: repository-local health script in Node.
- Why: avoid CI-only enforcement and keep offline checks possible.
- Impact: src artifact policy enforced consistently.

## Feature Flag Registry

| Flag                    | Default | Owner    | Scope        | Notes                             |
| ----------------------- | ------- | -------- | ------------ | --------------------------------- |
| `enableHealthDashboard` | `false` | Platform | web          | Controls health panel visibility  |
| `enableAiExecution`     | `false` | Platform | core-api/web | Controls direct AI execution path |
| `enableExperimentalUi`  | `false` | Product  | web/ui-kit   | Controls non-stable UI patterns   |

Rule: every new flag must be added here and in `packages/contracts/src/featureFlags.ts`.

## Contract Change Runbook

When changing `JobRequest`, `JobResult`, `HealthReport`, or `FeatureFlags`:

1. Update Zod schema files in `packages/contracts/src`.
2. Run `node packages/contracts/tools/gen_schemas.mjs`.
3. Inspect JSON schema diff for unintended changes.
4. Update `services/ai-agent/app/models.py` to mirror shape.
5. Update tests in affected package/service.
6. Record migration note in this notebook.

## Service-to-Service Integration Notes

### Core API to AI agent

- Core API endpoint: `POST /jobs`.
- Optional integration target: `http://127.0.0.1:8001/jobs/run`.
- Failure mode: return deterministic queued response without raising unstable exceptions.

### AI agent behavior

- Must produce deterministic stub output for equal input.
- Must never require outbound network to satisfy baseline response.

## Data Handling Rules

1. This repository is source code and documentation only.
2. Raw datasets, exports, images, and archives do not belong under `src/**`.
3. If sample data is needed, keep it tiny and textual under dedicated `fixtures/` directories.
4. Any generated contract artifact must be JSON with stable formatting.

## Known Risks and Mitigations

1. Risk: Contract drift between TS and Python models.
   - Mitigation: generated JSON schema + mirrored pydantic models + smoke tests.
2. Risk: Local dev machines with missing pnpm.
   - Mitigation: direct `node` script entry points for essential checks.
3. Risk: accidental source artifact commits.
   - Mitigation: `.gitignore` patterns + `tools/health` hard fail.
4. Risk: overgrowth of UI dependencies.
   - Mitigation: keep `ui-kit` dependency set minimal and framework-native.

## Local Environment Variables

### Core API

- `CORE_API_HOST` default: `127.0.0.1`
- `CORE_API_PORT` default: `3001`
- `AI_AGENT_URL` default: `http://127.0.0.1:8001`

### Web app

- `VITE_CORE_API_URL` default: `http://127.0.0.1:3001`

### Health script

- `MAX_SRC_FILE_BYTES` default: `10485760`
- `MAX_TEXT_ARTIFACT_BYTES` default: `1048576`

## Python Setup Notes (No Auto-Venv)

The bootstrap does not auto-create virtual environments.
Use local commands when needed:

1. `python -m venv .venv`
2. `.\.venv\Scripts\activate`
3. `pip install -e .`
4. `uvicorn app.main:app --host 127.0.0.1 --port 8001`

If Python is unavailable, keep AI agent code scaffolded and continue with Node-only checks.

## Execution Journal Template

Use this template for future entries:

Date:
Owner:
Scope:
Decision:
Reason:
Impact:
Follow-up:

## Quality Gate Checklist

Before merging changes:

1. Run `node tools/health/src/check_repo_health.mjs`.
2. Run `node packages/contracts/tools/gen_schemas.mjs --check`.
3. Run relevant unit tests for touched modules.
4. Confirm flags still default OFF unless intentionally changed.
5. Confirm docs (`NOTEBOOK`, `CONTRACT`, `MASTER_MAP`) are still consistent.

## Bootstrap Completion Note (2026-02-18)

Initial repo skeleton includes:

- workspace root config
- contract schemas and generator
- core-api service skeleton and tests
- ai-agent service skeleton and deterministic stub
- web app skeleton with health dashboard gate
- ui-kit package with strict exports
- health tooling and docs index script

No historical source migration was performed in bootstrap.
No external network calls are required for baseline local checks.

## 2026-03-03 - Keystone Scene Studio mission kickoff (UNICODEX)

Date: 2026-03-03  
Owner: UNICODEX  
Scope: `apps/keystone` + `docs/quality` + `visual validation tooling`

Decision:
- Build a dev-only Scene Studio at `/dev/scene-studio` with strict production 404 behavior.
- Treat `docs/dispatch/DISPATCHER_BRIEF.md` layer IDs as canonical and use `@hitech/ui-kit` as source of truth for layer query contracts.
- Keep backward compatibility for existing `layers`, `layerProfile`, and `motion` query semantics.
- Extend existing Playwright visual workflow instead of replacing it.

Assumptions:
- Node and pnpm are available locally and Chromium can be installed for Playwright.
- Scene Studio is an internal development capability and can persist state in browser localStorage.
- Deterministic rendering requires disabling animations, waiting for fonts, and waiting for a dedicated ready signal.
- Improvement evidence must be artifact-backed under `artifacts/keystone-scene-studio`.

Reason:
- Move from intuition-based visual changes to reproducible and measurable proof.

Impact:
- Introduces a versioned scene schema, scene diagnostics bridge, artifact scorecards, and claim-gated proof workflow.

Follow-up:
- Validate all new scripts/tests end-to-end and update docs index if required by repo process.

## 2026-03-03 - Keystone Scene Studio implementation complete

Date: 2026-03-03  
Owner: UNICODEX  
Scope: Scene contracts, Studio UI, diagnostics bridge, Playwright visual proof, claim gate

Delivered:
- `/dev/scene-studio` dev-only route with hard `404` behavior in production.
- Versioned scene schema + migration pipeline (`v1 -> v2`) with runtime validation.
- Local scene persistence, import/export, canonical URL builder, and URL roundtrip utilities.
- Scene Studio UI with search, tags, sorting, editor, compare preview, copy URL, diagnostics export, and keyboard shortcuts.
- Pitch runtime bridge with secure postMessage diagnostics and deterministic `data-scene-ready` signal.
- Manifest-driven visual run pipeline writing artifacts to `artifacts/keystone-scene-studio`.
- Report index generation and claim-based proof gate.

Tradeoffs:
- Scene Studio UI is intentionally dev-focused and uses localStorage for speed and zero backend coupling.
- Visual runner remains Playwright-first; the Studio triggers runner via dev API route for operator ergonomics.
- Report indexing is regenerated by script to keep CI behavior deterministic and avoid runtime scanning overhead in app code.

Verification:
- Keystone lint/typecheck/tests pass after implementation.
- Scene contract + migration + access + diagnostics payload tests added.
