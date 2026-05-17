<!-- agent-workbench-rescue-managed -->
# Integration Captain Agent Workspace

## Assignment

- Agent: Integration Captain
- Task ID: ICAP-001
- Suggested branch: chore/integration-captain-report
- Current state: IN_PROGRESS
- Risk level: HIGH
- Coordinator decision: UPDATE_REQUIRED

## Scope

Allowed files:

    docs/dev/agent-workbench/agents/integration-captain/**

Forbidden files:

    Any file outside this folder unless acting as Coordinator, product code, main, merges, force-push, branch deletion.

## Inputs

All agent reports, Master Status Board, Work Queue, Merge Readiness Checklist.

## Required Outputs

- INTEGRATION_SEQUENCE_REPORT.md
- FINAL_MERGE_PLAN.md

## Goal

Consolidate reports, update integration sequence, and prepare final merge plan with risks, validations, and rollback protocols. Do not merge.

## Definition of Done

Sequence report and final merge plan are updated. No code merge decision is made without human approval.

## Rollback

Close the PR and discard only this agent folder changes if rejected.
