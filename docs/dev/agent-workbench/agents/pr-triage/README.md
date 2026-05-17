<!-- agent-workbench-rescue-managed -->
# PR Triage Agent Workspace

## Assignment

- Agent: PR Triage
- Task ID: TRIAGE-001
- Suggested branch: docs/pr-triage-report
- Current state: NEEDS_UPDATE
- Risk level: MEDIUM
- Coordinator decision: UPDATE_REQUIRED

## Scope

Allowed files:

    docs/dev/agent-workbench/agents/pr-triage/**

Forbidden files:

    Product code, other agent folders, .gitignore, workflows, root files, main, merges, force-push, branch deletion.

## Inputs

Triage PRs en GitHub.pdf, Master Status Board, open PR list. CAPATCH is closed and cannot be treated as pending consolidation.

## Required Outputs

- PR_TRIAGE_REPORT.md

## Goal

Create PR_TRIAGE_REPORT.md listing open PRs with number, title, branch, type, affected files, dependencies, conflict risk, and recommendation. Mark CAPATCH-related PRs as legacy/evidence and do not recommend them for merge.

## Definition of Done

Report is complete, aligned with the board, removes CAPATCH as active stream, and proposes clear priorities. PR may be opened but must not be merged.

## Rollback

Close the PR and discard only this agent folder changes if the report is rejected. No main changes.
