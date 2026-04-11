# Getting Started with HITECH OS

This document is a practical contributor entrypoint for the current repository layout.

## What HITECH OS looks like right now

The repository already contains:

- governed docs under `docs/`
- application code under `apps/`
- runtime services under `services/`
- reusable packages under `packages/`
- repo automation and guardrails under `tools/`
- multiple CI and release workflows under `.github/workflows/`

This means onboarding is less about inventing structure and more about learning how the existing structure fits together.

## Suggested first reading order

1. `README.md`
2. `README_START_HERE.md`
3. `docs/README.md`
4. `docs/MASTER_MAP.md`
5. `docs/CONTRACT.md`
6. `docs/CONSTITUTION.md`

If you are touching contracts or Python-side runtime code, also read:

7. `docs/CONTRACT_PYTHON_SYNC.md`
8. `packages/contracts/README.md`
9. `services/ai-agent/README.md`

## Environment expectations

Typical commands in this repo assume:

- Node / pnpm for workspace orchestration
- Python for a number of guardrail and service-side scripts
- a repo-root execution context for package scripts

Recommended shell examples:

```powershell
Set-Location F:epos\hitech-os
pnpm install --frozen-lockfile --ignore-scripts
pnpm run docs
pnpm run health
pnpm run quality
```

## High-signal directories

### Applications
- `apps/keystone`
- `apps/demo-engine`

### Services
- `services/core-api`
- `services/ai-agent`

### Contracts and shared packages
- `packages/contracts`
- `packages/ui-kit`
- `packages/tooling`

### Tooling and repo operations
- `tools/health`
- `tools/scripts`
- `tools/codex`
- `tools/meta`
- `tools/snapshot`

## Safe first tasks for a newcomer

- read the navigation docs and map files
- run read-only validations
- inspect the relevant local README before changing a sub-area
- keep changes narrow and evidence-based
- avoid reorganizing top-level structure without an explicit decision

## Checks worth running after changes

```powershell
pnpm run docs
pnpm run schema:gen
pnpm run health
pnpm run contract:python-sync
pnpm run guardrails:nav
```

If your change is UI-centric:

```powershell
pnpm --filter @hitech/ui-kit test
pnpm --filter @hitech/keystone test
```

If your change is service / contract centric:

```powershell
pnpm run schema:gen
py tools\scripts\check_contract_python_parity.py --repo-root .
```

## Things this doc deliberately does not do

This file avoids making product decisions for you. For example:
- it does not decide whether `apps/demo-engine` should be deleted
- it does not physically reorganize `tools/`
- it does not reinterpret Constitution or Contract law

Those decisions need explicit review, not broad automation.
