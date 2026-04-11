# .github/workflows

This directory contains repository automation workflows.

## Purpose

Workflows here are the executable automation layer for CI, docs governance, quality gates, release flows, security scans, and maintenance jobs.

## How to navigate

1. Start with `docs/WORKFLOW_CATALOG.md` for a filename-to-intent overview.
2. Open the workflow YAML that matches the concern you care about.
3. Trace any called scripts back into `tools/`, `packages/`, `services/`, or `docs/`.

## New narrow workflows added by this remediation

- `contract-python-parity.yml`
- `repo-navigation-guard.yml`

These are intentionally focused and should be read as additive guardrails, not as replacements for the broader existing workflows already present in the repo.
