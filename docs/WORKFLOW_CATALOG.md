# Workflow Catalog

This document gives a practical index of workflow intent for `.github/workflows`.

## Why this file exists

The repository already contains many workflow files. A list of filenames is not enough when someone needs to understand why a workflow exists and where to start reading.

This catalog is intentionally descriptive rather than normative. The workflow YAML files remain the executable source of truth.

## Current workflow directory

The bundle used for this remediation includes these workflow files:

- `ci-local.yml`
- `ci.yml`
- `cla-check.yml`
- `dependency-check.yml`
- `dev-console-architecture-guard.yml`
- `docs-governor.yml`
- `factory.yml`
- `forgeos-quality-gate.yml`
- `forgeos-release-candidate.yml`
- `forgeos-root-authority.yml`
- `labels.yml`
- `orchestrator-factory.yml`
- `promotion.yml`
- `release.yml`
- `repo-analyzer-self-test.yml`
- `security-scan.yml`
- `stale.yml`

Additional workflow files added by this remediation:
- `contract-python-parity.yml`
- `repo-navigation-guard.yml`

## Workflow families

### Core CI
- `ci.yml`
- `ci-local.yml`

These are the first places to inspect for broad validation behavior.

### Docs / governance
- `docs-governor.yml`
- `dev-console-architecture-guard.yml`
- `forgeos-root-authority.yml`

These are likely tied to governance and documentation enforcement.

### Release / promotion
- `release.yml`
- `promotion.yml`
- `forgeos-release-candidate.yml`

These are the likely release path entry points.

### Security / compliance / hygiene
- `security-scan.yml`
- `dependency-check.yml`
- `cla-check.yml`

### Factory / orchestrator / self-tests
- `factory.yml`
- `orchestrator-factory.yml`
- `repo-analyzer-self-test.yml`
- `forgeos-quality-gate.yml`

### Repo maintenance
- `labels.yml`
- `stale.yml`

## How to read workflows efficiently

1. Start with the filename and top-level `name`.
2. Identify the trigger (`on:`).
3. Identify the main jobs.
4. Identify the decisive steps that fail or gate the run.
5. Cross-reference any local scripts they call back into `tools/`, `packages/`, `services/`, or `docs/`.

## New workflow checks added here

### `contract-python-parity.yml`
Runs a narrow verification that the contract-side generated sync map and the Python service model layer remain aligned enough to catch obvious drift.

### `repo-navigation-guard.yml`
Checks for the presence of critical navigation files and local README coverage in high-value repo areas.

These checks are additive and intentionally focused. They do not replace the broader CI flows already present in the repository.
