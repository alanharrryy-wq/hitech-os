# Release Governance

## Current decision
Versioning mode for this repository remains **lockstep** at repo level.

Reason:
- all workspace packages are private
- release automation is currently repository-centric
- insufficient evidence for safe independent publishing lanes
- current versions show grouped lockstep behavior (`0.1.x` runtime/tooling, `0.2.x` services)

Current lockstep scope:
- `grouped-provisional` (not strict full-workspace lockstep yet)

## Release-critical surfaces
- `F:\repos\hitech-os\packages\contracts\**`
- `F:\repos\hitech-os\services\core-api\src\contracts\**`
- `F:\repos\hitech-os\services\core-api\src\routes\**`
- `F:\repos\hitech-os\apps\keystone\app\api\**`
- release automation/config:
  - `F:\repos\hitech-os\release-please-config.json`
  - `F:\repos\hitech-os\.releaserc.json`
  - `F:\repos\hitech-os\.github\workflows\release.yml`

## Discipline rules (current final-pass baseline)
When any release-critical or public-API path changes, include release evidence in one of:
- `F:\repos\hitech-os\CHANGELOG.md`
- `F:\repos\hitech-os\docs\releases\**`

Additional report-first rules:
- workspace `package.json` changes should include release evidence
- workspace version changes should include explicit release intent/evidence

## CI hook status
- `tools/scripts/check_release_discipline.mjs` validates:
  - release-critical change evidence
  - public API change evidence
  - manifest/version intent evidence
  - release/dependency policy consistency inputs
- Script remains report-first by default.
- `release.yml` (Release Governance workflow) supports optional strict mode via `workflow_dispatch` input.
- Blocking check IDs are policy-driven in `F:\repos\hitech-os\policies\release.json`.

## Future tightening path
1. Keep manifest/version intent checks in warn mode until noise is stable.
2. Enforce strict mode for blocking check IDs on release-critical PR lanes.
3. Add API diff checks for `packages/contracts` once stable baselines are defined.
