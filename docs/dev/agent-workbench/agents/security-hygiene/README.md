<!-- agent-workbench-rescue-managed -->
# Security / Repo Hygiene Agent Workspace

## Assignment

- Agent: Security / Repo Hygiene
- Task ID: SEC-001
- Suggested branch: chore/security-hygiene-audit
- Current state: NOT_STARTED
- Risk level: MEDIUM
- Coordinator decision: WAIT

## Scope

Allowed files:

    docs/dev/agent-workbench/agents/security-hygiene/**

Forbidden files:

    .gitignore, workflows, product code, any file outside this folder, main, merges, force-push, branch deletion.

## Inputs

Repo hygiene tools, quality baseline, Master Status Board.

## Required Outputs

- SECURITY_HYGIENE_REPORT.md
- LOCAL_ARTIFACT_POLICY.md

## Goal

Document secrets/artifact findings and local artifact policy. Suggest .gitignore entries without editing .gitignore.

## Definition of Done

Both Markdown files are complete and wait for Integration Captain coordination before real changes.

## Rollback

Close the PR and discard only this agent folder changes if rejected.
