# Agent Handoff Prompts

## PR Triage

Branch: docs/pr-triage-report

Folder: docs/dev/agent-workbench/agents/pr-triage/

Allowed files: PR_TRIAGE_REPORT.md, README.md, evidence/**

Goal: convert Triage PRs en GitHub.pdf into PR_TRIAGE_REPORT.md. Classify open PRs by number, title, branch, type, affected files, dependencies, conflict risk, and recommendation. Mark CAPATCH as legacy/evidence.

## Quality Baseline

Branch: docs/quality-baseline-report

Folder: docs/dev/agent-workbench/agents/quality/

Allowed files: QUALITY_BASELINE_REPORT.md, VALIDATION_COMMANDS.md, README.md, evidence/**

Goal: convert Quality.pdf into Markdown, run validation commands, and record results without changing product code.

## Monorepo Architecture Audit

Branch: docs/monorepo-architecture-audit

Folder: docs/dev/agent-workbench/agents/architecture/

Allowed files: APP_INVENTORY.md, PACKAGE_INVENTORY.md, MONOREPO_ARCHITECTURE_AUDIT.md, README.md, evidence/**

Goal: convert arquitectura.pdf into app/package inventories and architecture audit. Treat CAPATCH as legacy.

## Branch Cleanup Plan

Branch: docs/branch-cleanup-plan

Folder: docs/dev/agent-workbench/agents/branch-cleanup/

Allowed files: BRANCH_CLEANUP_PLAN.md, README.md, evidence/**

Goal: convert Branch cleanup.pdf into a non-destructive branch cleanup plan. Do not delete branches.

## PRISMA Consolidation Planning

Branch: docs/prisma-consolidation-plan

Folder: docs/dev/agent-workbench/agents/prisma/

Allowed files: PRISMA_CONSOLIDATION_PLAN.md, README.md, evidence/**

Goal: convert Prisma.pdf into a planning report. Do not implement PRISMA consolidation. CAPATCH is not a dependency.

## CI Hardening

Branch: chore/ci-actions-hardening

Folder: docs/dev/agent-workbench/agents/ci-hardening/

Allowed files: CI_HARDENING_REPORT.md, README.md, evidence/**

Goal: document workflow and dependabot hardening recommendations after Quality Baseline exists. Do not edit workflows.

## Security / Repo Hygiene

Branch: chore/security-hygiene-audit

Folder: docs/dev/agent-workbench/agents/security-hygiene/

Allowed files: SECURITY_HYGIENE_REPORT.md, LOCAL_ARTIFACT_POLICY.md, README.md, evidence/**

Goal: audit for secrets, local artifacts, temporary files, and propose policy. Do not edit .gitignore directly.

## UI Smoke Baseline

Branch: docs/ui-smoke-baseline

Folder: docs/dev/agent-workbench/agents/ui-smoke/

Allowed files: UI_SMOKE_BASELINE.md, VISUAL_TESTING_GUIDE.md, README.md, evidence/**

Goal: document UI smoke methodology after Quality Baseline exists. Do not edit UI code.

## Documentation / Onboarding

Branch: docs/onboarding-refresh

Folder: docs/dev/agent-workbench/agents/documentation-onboarding/

Allowed files: GETTING_STARTED_PLAN.md, ARCHITECTURE_OVERVIEW_PLAN.md, RELEASE_PROCESS_PLAN.md, README.md, evidence/**

Goal: plan onboarding documentation refresh. Do not edit final root docs yet.

## Integration Captain

Branch: chore/integration-captain-report

Folder: docs/dev/agent-workbench/agents/integration-captain/

Allowed files: INTEGRATION_SEQUENCE_REPORT.md, FINAL_MERGE_PLAN.md, README.md, evidence/**

Goal: consolidate reports and produce final merge plan. Do not merge code.
