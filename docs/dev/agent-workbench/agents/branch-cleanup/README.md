<!-- agent-workbench-rescue-managed -->
# Branch Cleanup Plan Agent Workspace

## Assignment

- Agent: Branch Cleanup Plan
- Task ID: BCLEAN-001
- Suggested branch: docs/branch-cleanup-plan
- Current state: NEEDS_UPDATE
- Risk level: MEDIUM
- Coordinator decision: UPDATE_REQUIRED

## Scope

Allowed files:

    docs/dev/agent-workbench/agents/branch-cleanup/**

Forbidden files:

    Any file outside this folder. Do not modify, delete, or rename branches. No main, merges, force-push, branch deletion.

## Inputs

Branch cleanup.pdf, PR triage report when available, app/package inventories, Master Status Board. CAPATCH branches are evidence/legacy until classified.

## Required Outputs

- BRANCH_CLEANUP_PLAN.md

## Goal

Create branch cleanup plan with categories: active, legacy, evidence, superseded, needs-inspection. Include deletion criteria, backup protocol, author notification, and explicit CAPATCH no-delete rule.

## Definition of Done

Plan is complete and aligned with board. PR may be opened but must not be merged.

## Rollback

Close the PR and discard only this agent folder changes if rejected.
