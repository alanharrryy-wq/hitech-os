# @hitech/contracts

Shared contract package for TypeScript services/apps and Python model mirror.

## Contents

- Zod schemas for:
  - `FeatureFlags`
  - `JobRequest`
  - `JobResult`
  - `AgentCapabilities`
  - `HealthReport`
- TypeScript type exports
- Deterministic JSON Schema generated artifacts in `schemas/generated`
- Python sync map file (`schemas/generated/python-sync-map.json`)
- Contract version metadata (`schemas/generated/schema-version.json`)

## Commands

- `node tools/gen_schemas.mjs` regenerate schema artifacts
- `node tools/gen_schemas.mjs --check` verify deterministic output

## Docs

- `docs/SCHEMA_VERSIONING.md` explains schema versioning and compatibility guarantees.
