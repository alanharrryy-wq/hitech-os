# Tooling Guide

This guide maps the major tooling areas in the repository and explains the role of each one.

## Tooling zones

### `tools/health`
Repository hygiene checks. This is where repo-level health scanning lives.

Primary use:
- detect suspicious artifacts
- keep `src/**` areas free from obvious junk or oversized baggage
- support deterministic hygiene reporting

### `tools/scripts`
General utility scripts for validation, smoke checks, dependency policy, documentation indexing, reporting, and repo maintenance.

Primary use:
- workspace validation
- docs index generation
- dependency hygiene
- release discipline reports
- engineering health collection

### `tools/codex`
Codex / factory-oriented runtime helpers, validation utilities, dispatch logic, guards, schemas, and tracking artifacts.

Primary use:
- factory dispatch
- codex runtime / validation helpers
- repo-specific codex automation
- task-bank / tracking / state support

### `tools/meta`
Metadata, pathing, hashing, registries, and report generation support.

Primary use:
- structured reporting
- registry support
- path and IO helper logic

### `tools/snapshot`
Snapshot creation and validation tooling for repository state.

Primary use:
- deterministic snapshot creation
- snapshot validation in quality / CI flows

## Useful existing commands from the repo root

```powershell
pnpm run docs
pnpm run health
pnpm run deps:check
pnpm run workspace:validate
pnpm run guardrails:all
pnpm run engineering-health:collect
pnpm run snapshot:hos
pnpm run snapshot:hos:validate
```

## How to choose the right tool area

### You need a repo health check
Start with `tools/health`.

### You need a general validation or report
Start with `tools/scripts`.

### You need Codex / Factory runtime support
Start with `tools/codex`.

### You need structured report writing or registry / path helpers
Start with `tools/meta`.

### You need repository state capture / validation
Start with `tools/snapshot`.

## Operational cautions

- Do not assume all tools are interchangeable.
- Avoid moving tools between top-level directories without a design decision.
- Prefer adding README/navigation coverage before doing structural surgery.
- If a new tool changes repo law or guardrails, document that in `docs/NOTEBOOK.md` and the relevant local README.

## New support introduced by this remediation

This patch set adds:
- README files for previously under-documented tool directories
- a navigation guard script for critical README and doc presence
- a contract/Python parity check script for `packages/contracts` and `services/ai-agent`
- workflow catalog documentation for `.github/workflows`

The goal is to reduce ambiguity, not to flatten the repository into one giant toolbox.
