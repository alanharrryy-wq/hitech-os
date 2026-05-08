<!-- agent-workbench-rescue-managed -->
# CI Hardening Agent Workspace

## Assignment

- Agent: CI Hardening
- Task ID: CIHARD-001
- Suggested branch: chore/ci-actions-hardening
- Current state: NOT_STARTED
- Risk level: MEDIUM
- Coordinator decision: WAIT

## Scope

Allowed files:

    docs/dev/agent-workbench/agents/ci-hardening/**

Forbidden files:

    .github/workflows/**, .github/dependabot.yml, product code, any file outside this folder, main, merges, force-push, branch deletion.

## Inputs

Read-only workflows, dependabot.yml, quality baseline, security recommendations.

## Required Outputs

- CI_HARDENING_REPORT.md

## Goal

Document CI risks and proposed hardening. Do not implement workflow changes.

## Definition of Done

Report has clear recommendations and waits for Integration Captain approval before real changes.

## Rollback

Close the PR and discard only this agent folder changes if rejected.
