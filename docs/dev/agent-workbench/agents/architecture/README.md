<!-- agent-workbench-rescue-managed -->
# Monorepo Architecture Audit Agent Workspace

## Assignment

- Agent: Monorepo Architecture Audit
- Task ID: ARCH-001
- Suggested branch: docs/monorepo-architecture-audit
- Current state: NEEDS_UPDATE
- Risk level: HIGH
- Coordinator decision: UPDATE_REQUIRED

## Scope

Allowed files:

    docs/dev/agent-workbench/agents/architecture/**

Forbidden files:

    Product code, other agent folders, mutex files, build scripts, main, merges, force-push, branch deletion.

## Inputs

arquitectura.pdf, repo analysis outputs, Master Status Board. apps/code-atlas/capatch_system is legacy.

## Required Outputs

- APP_INVENTORY.md
- PACKAGE_INVENTORY.md
- MONOREPO_ARCHITECTURE_AUDIT.md

## Goal

Create inventories for apps and packages plus an architecture audit covering cross-dependencies, workspace compliance, violations, and recommendations aligned with CAPATCH closed.

## Definition of Done

Three Markdown files are complete and coherent. PR may be opened but must not be merged.

## Rollback

Close the PR and discard only this agent folder changes if rejected.
