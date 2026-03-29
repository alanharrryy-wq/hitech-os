# Policies

Monorepo hardening policies are executable inputs for guardrail scripts.

## Files
- `F:\repos\hitech-os\policies\dependencies.json`
  - workspace patterns + roots
  - allowed workspace cycles baseline
  - boundary model (single source for workspace boundary enforcement)
  - retired workspace entries (explicitly tracked to avoid silent drift)
- `F:\repos\hitech-os\policies\release.json`
  - lockstep vs independent versioning mode
  - lockstep scope posture
  - release-critical and public API paths
  - change-note and release-intent expectations
  - blocking-check IDs for strict mode
- `F:\repos\hitech-os\policies\security.json`
  - sensitive path prefixes
  - high-confidence secret scan patterns
  - review policy posture

## Enforcement posture
- Default mode is report-first.
- Strict mode is enabled where signal is stable (`check_no_new_cycles`, dependency-policy validation).
- `F:\repos\hitech-os\tools\scripts\validate_dependencies_policy.mjs` is the policy structural/sync gate.
