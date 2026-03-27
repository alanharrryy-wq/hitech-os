# Run ID Standard

## Purpose
A strong ID system makes cross-chat coordination traceable from vague idea to accepted artifact.

## Required identifiers

### `project_id`
Format: `prj-<slug>`
Examples:
- `prj-billing-migration`
- `prj-customer-portal`
- `prj-api-hardening`

### `run_id`
Format: `run-<project_id>-<YYYYMMDD>-<NN>`
Examples:
- `run-prj-billing-migration-20260327-01`
- `run-prj-customer-portal-20260327-02`

Rules:
- one run ID per bounded execution campaign
- do not reuse a run ID for a different objective
- increment `NN` when more than one run starts on the same day for the same project

### `round_id`
Format: `rd-<NNN>`
Examples:
- `rd-001`
- `rd-002`

Rules:
- rounds are local to a run
- round IDs do not reset inside the same run

### `decision_id`
Format: `dec-<run_id>-<NNN>`

### `bundle_id`
Format: `<run_id>__<round_id>__<package_id>__v<NN>`
Example:
`run-prj-customer-portal-20260327-01__rd-001__03-service-contracts-and-orchestration__v01`

### `artifact_id`
Format: `art-<run_id>-<round_id>-<package_id>-<kind>-<NNN>`

## Path conventions
- run root: `ops/runs/<run_id>/`
- round root: `ops/runs/<run_id>/rounds/<round_id>/`
- decisions: `ops/runs/<run_id>/decisions/`
- incoming bundles: `ops/runs/<run_id>/rounds/<round_id>/incoming/`
- reports: `ops/runs/<run_id>/rounds/<round_id>/reports/`

## Why this matters
The ID chain makes it possible to answer:
- which project this artifact belongs to
- which run and round produced it
- which package owned it
- which decision authorized it
- which downstream consumers were affected
