<!-- agent-workbench-rescue-managed -->
# UI Smoke Baseline Agent Workspace

## Assignment

- Agent: UI Smoke Baseline
- Task ID: UI-001
- Suggested branch: docs/ui-smoke-baseline
- Current state: NOT_STARTED
- Risk level: LOW
- Coordinator decision: WAIT

## Scope

Allowed files:

    docs/dev/agent-workbench/agents/ui-smoke/**

Forbidden files:

    UI code, workflows, other agent folders, main, merges, force-push, branch deletion.

## Inputs

Quality baseline, available UI tools, Master Status Board.

## Required Outputs

- UI_SMOKE_BASELINE.md
- VISUAL_TESTING_GUIDE.md

## Goal

Document critical UI smoke scenarios and visual testing methodology. Do not execute real automation in this phase.

## Definition of Done

Both documents are complete and clear. PR may be opened but must not be merged.

## Rollback

Close the PR and discard only this agent folder changes if rejected.
