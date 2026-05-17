<!-- agent-workbench-rescue-managed -->
# Quality Baseline Agent Workspace

## Assignment

- Agent: Quality Baseline
- Task ID: QUAL-001
- Suggested branch: docs/quality-baseline-report
- Current state: NEEDS_UPDATE
- Risk level: MEDIUM
- Coordinator decision: UPDATE_REQUIRED

## Scope

Allowed files:

    docs/dev/agent-workbench/agents/quality/**

Forbidden files:

    Any file outside this folder, product code, scripts, lockfiles, main, merges, force-push, branch deletion.

## Inputs

Quality.pdf, package.json quality/ci scripts, guard-rail tools, Master Status Board. CAPATCH is closed.

## Required Outputs

- QUALITY_BASELINE_REPORT.md
- VALIDATION_COMMANDS.md

## Goal

Create VALIDATION_COMMANDS.md with exact commands and QUALITY_BASELINE_REPORT.md with lint/test warnings, failures, timings, environment notes, and improvement proposals without modifying code.

## Definition of Done

Both Markdown files exist, document executions/results clearly, and contain no code-modification instructions. PR may be opened but must not be merged.

## Rollback

Close the PR and discard only this agent folder changes if rejected.
