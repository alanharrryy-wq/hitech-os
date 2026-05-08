<!-- agent-workbench-rescue-managed -->
# PRISMA Consolidation Planning Agent Workspace

## Assignment

- Agent: PRISMA Consolidation Planning
- Task ID: PRISMA-001
- Suggested branch: docs/prisma-consolidation-plan
- Current state: NEEDS_UPDATE
- Risk level: MEDIUM
- Coordinator decision: UPDATE_REQUIRED

## Scope

Allowed files:

    docs/dev/agent-workbench/agents/prisma/**

Forbidden files:

    PRISMA product code, other agent folders, mutex files, main, merges, force-push, branch deletion.

## Inputs

Prisma.pdf, app/package inventories, quality baseline, PR triage, Master Status Board. CAPATCH must not appear as dependency.

## Required Outputs

- PRISMA_CONSOLIDATION_PLAN.md

## Goal

Create PRISMA_CONSOLIDATION_PLAN.md with related branches/PRs, dependencies, preconditions, ordered consolidation steps, risks, owners, and Wave 4 approval boundary.

## Definition of Done

Plan is complete, aligned with inventories and baseline, and excludes CAPATCH as dependency. PR may be opened but must not be merged.

## Rollback

Close the PR and discard only this agent folder changes if rejected.
