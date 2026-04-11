# tools/health

Repository health and hygiene checks live here.

## Purpose

This area exists to catch repository problems that should fail loudly instead of drifting quietly into source paths.

Typical examples:
- suspicious dumps or archives in source-oriented areas
- oversized artifacts that should not live in committed source paths
- hygiene violations that damage deterministic review

## Current contents

- `src/check_repo_health.mjs`

## Typical usage

From repo root:

```powershell
node tools/health/src/check_repo_health.mjs
```

Or via the existing root script:

```powershell
pnpm run health
```

## Why this README was added

The repository already had functioning health logic, but this directory had no local README. The missing navigation layer made it harder to discover the purpose of the directory quickly.

## Boundaries

- keep this directory focused on repo health checks
- avoid mixing unrelated project-specific business logic here
- prefer deterministic text or JSON output for machine review
