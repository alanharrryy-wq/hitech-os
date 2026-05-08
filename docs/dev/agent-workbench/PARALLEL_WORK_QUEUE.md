<!-- agent-workbench-rescue-managed -->
# Parallel Work Queue

## WAVE 0 - Coordination

### TASK ID: WB-SETUP

Agent: Coordinator
State: DELIVERED_NOT_PUSHED
Goal: Maintain the Agent Workbench structure, board, queue, checklist, prompts, and reconciliation documents.
Allowed Files: docs/dev/agent-workbench/**
Forbidden Files: Product code, lockfiles, CI configs, main, merges, force-push, branch deletion.
Inputs: Existing workbench docs, orchestrator_factory atlas, delivered PDFs, user instructions.
Output Required: Stable workbench coordination docs.
Dependencies: None
Blocking Conditions: Any requested product-code change or out-of-scope edit.
Definition of Done: Workbench reflects current truth and all agents have isolated scopes.
Rollback: Restore from backup zip in F:\descargasf if validation fails.
Coordinator Notes: This task is fulfilled by v3 reconciler for the current iteration.

## WAVE 1 - Analysis

### TASK ID: TRIAGE-001

Agent: PR Triage
State: NEEDS_UPDATE
Goal: Create PR_TRIAGE_REPORT.md listing open PRs with number, title, branch, type, affected files, dependencies, conflict risk, and recommendation. Mark CAPATCH-related PRs as legacy/evidence and do not recommend them for merge.
Allowed Files: docs/dev/agent-workbench/agents/pr-triage/**
Forbidden Files: Product code, files outside assigned folder, other agent folders, main, merges, force-push, branch deletion. Global workbench files are read-only unless the user explicitly appoints the agent as Coordinator.
Inputs: Triage PRs en GitHub.pdf, Master Status Board, open PR list. CAPATCH is closed and cannot be treated as pending consolidation.
Output Required: PR_TRIAGE_REPORT.md
Dependencies: Board Setup
Blocking Conditions: Need product-code changes, missing required evidence, conflict with another agent scope, CAPATCH active dependency, merge request, branch deletion request, or force-push request.
Definition of Done: Required outputs updated inside assigned folder, evidence listed, risks stated, dependencies stated, CAPATCH handled as legacy where relevant, no out-of-scope files touched.
Rollback: Close the PR and discard only this agent folder changes if the report is rejected. No main changes.
Coordinator Notes: Suggested branch is docs/pr-triage-report. Agent may open a PR but must not merge it.

### TASK ID: QUAL-001

Agent: Quality Baseline
State: NEEDS_UPDATE
Goal: Create VALIDATION_COMMANDS.md with exact commands and QUALITY_BASELINE_REPORT.md with lint/test warnings, failures, timings, environment notes, and improvement proposals without modifying code.
Allowed Files: docs/dev/agent-workbench/agents/quality/**
Forbidden Files: Product code, files outside assigned folder, other agent folders, main, merges, force-push, branch deletion. Global workbench files are read-only unless the user explicitly appoints the agent as Coordinator.
Inputs: Quality.pdf, package.json quality/ci scripts, guard-rail tools, Master Status Board. CAPATCH is closed.
Output Required: QUALITY_BASELINE_REPORT.md, VALIDATION_COMMANDS.md
Dependencies: Board Setup
Blocking Conditions: Need product-code changes, missing required evidence, conflict with another agent scope, CAPATCH active dependency, merge request, branch deletion request, or force-push request.
Definition of Done: Required outputs updated inside assigned folder, evidence listed, risks stated, dependencies stated, CAPATCH handled as legacy where relevant, no out-of-scope files touched.
Rollback: Close the PR and discard only this agent folder changes if rejected.
Coordinator Notes: Suggested branch is docs/quality-baseline-report. Agent may open a PR but must not merge it.

### TASK ID: ARCH-001

Agent: Monorepo Architecture Audit
State: NEEDS_UPDATE
Goal: Create inventories for apps and packages plus an architecture audit covering cross-dependencies, workspace compliance, violations, and recommendations aligned with CAPATCH closed.
Allowed Files: docs/dev/agent-workbench/agents/architecture/**
Forbidden Files: Product code, files outside assigned folder, other agent folders, main, merges, force-push, branch deletion. Global workbench files are read-only unless the user explicitly appoints the agent as Coordinator.
Inputs: arquitectura.pdf, repo analysis outputs, Master Status Board. apps/code-atlas/capatch_system is legacy.
Output Required: APP_INVENTORY.md, PACKAGE_INVENTORY.md, MONOREPO_ARCHITECTURE_AUDIT.md
Dependencies: Board Setup
Blocking Conditions: Need product-code changes, missing required evidence, conflict with another agent scope, CAPATCH active dependency, merge request, branch deletion request, or force-push request.
Definition of Done: Required outputs updated inside assigned folder, evidence listed, risks stated, dependencies stated, CAPATCH handled as legacy where relevant, no out-of-scope files touched.
Rollback: Close the PR and discard only this agent folder changes if rejected.
Coordinator Notes: Suggested branch is docs/monorepo-architecture-audit. Agent may open a PR but must not merge it.

### TASK ID: BCLEAN-001

Agent: Branch Cleanup Plan
State: NEEDS_UPDATE
Goal: Create branch cleanup plan with categories: active, legacy, evidence, superseded, needs-inspection. Include deletion criteria, backup protocol, author notification, and explicit CAPATCH no-delete rule.
Allowed Files: docs/dev/agent-workbench/agents/branch-cleanup/**
Forbidden Files: Product code, files outside assigned folder, other agent folders, main, merges, force-push, branch deletion. Global workbench files are read-only unless the user explicitly appoints the agent as Coordinator.
Inputs: Branch cleanup.pdf, PR triage report when available, app/package inventories, Master Status Board. CAPATCH branches are evidence/legacy until classified.
Output Required: BRANCH_CLEANUP_PLAN.md
Dependencies: PR Triage and Architecture Audit
Blocking Conditions: Need product-code changes, missing required evidence, conflict with another agent scope, CAPATCH active dependency, merge request, branch deletion request, or force-push request.
Definition of Done: Required outputs updated inside assigned folder, evidence listed, risks stated, dependencies stated, CAPATCH handled as legacy where relevant, no out-of-scope files touched.
Rollback: Close the PR and discard only this agent folder changes if rejected.
Coordinator Notes: Suggested branch is docs/branch-cleanup-plan. Agent may open a PR but must not merge it.

### TASK ID: PRISMA-001

Agent: PRISMA Consolidation Planning
State: NEEDS_UPDATE
Goal: Create PRISMA_CONSOLIDATION_PLAN.md with related branches/PRs, dependencies, preconditions, ordered consolidation steps, risks, owners, and Wave 4 approval boundary.
Allowed Files: docs/dev/agent-workbench/agents/prisma/**
Forbidden Files: Product code, files outside assigned folder, other agent folders, main, merges, force-push, branch deletion. Global workbench files are read-only unless the user explicitly appoints the agent as Coordinator.
Inputs: Prisma.pdf, app/package inventories, quality baseline, PR triage, Master Status Board. CAPATCH must not appear as dependency.
Output Required: PRISMA_CONSOLIDATION_PLAN.md
Dependencies: Architecture Audit, Quality Baseline, PR Triage
Blocking Conditions: Need product-code changes, missing required evidence, conflict with another agent scope, CAPATCH active dependency, merge request, branch deletion request, or force-push request.
Definition of Done: Required outputs updated inside assigned folder, evidence listed, risks stated, dependencies stated, CAPATCH handled as legacy where relevant, no out-of-scope files touched.
Rollback: Close the PR and discard only this agent folder changes if rejected.
Coordinator Notes: Suggested branch is docs/prisma-consolidation-plan. Agent may open a PR but must not merge it.

## WAVE 2 - Risk and Validation

### TASK ID: CIHARD-001

Agent: CI Hardening
State: NOT_STARTED
Goal: Document CI risks and proposed hardening. Do not implement workflow changes.
Allowed Files: docs/dev/agent-workbench/agents/ci-hardening/**
Forbidden Files: Product code, files outside assigned folder, other agent folders, main, merges, force-push, branch deletion. Global workbench files are read-only unless the user explicitly appoints the agent as Coordinator.
Inputs: Read-only workflows, dependabot.yml, quality baseline, security recommendations.
Output Required: CI_HARDENING_REPORT.md
Dependencies: Quality Baseline
Blocking Conditions: Need product-code changes, missing required evidence, conflict with another agent scope, CAPATCH active dependency, merge request, branch deletion request, or force-push request.
Definition of Done: Required outputs updated inside assigned folder, evidence listed, risks stated, dependencies stated, CAPATCH handled as legacy where relevant, no out-of-scope files touched.
Rollback: Close the PR and discard only this agent folder changes if rejected.
Coordinator Notes: Suggested branch is chore/ci-actions-hardening. Agent may open a PR but must not merge it.

### TASK ID: SEC-001

Agent: Security / Repo Hygiene
State: NOT_STARTED
Goal: Document secrets/artifact findings and local artifact policy. Suggest .gitignore entries without editing .gitignore.
Allowed Files: docs/dev/agent-workbench/agents/security-hygiene/**
Forbidden Files: Product code, files outside assigned folder, other agent folders, main, merges, force-push, branch deletion. Global workbench files are read-only unless the user explicitly appoints the agent as Coordinator.
Inputs: Repo hygiene tools, quality baseline, Master Status Board.
Output Required: SECURITY_HYGIENE_REPORT.md, LOCAL_ARTIFACT_POLICY.md
Dependencies: Quality Baseline
Blocking Conditions: Need product-code changes, missing required evidence, conflict with another agent scope, CAPATCH active dependency, merge request, branch deletion request, or force-push request.
Definition of Done: Required outputs updated inside assigned folder, evidence listed, risks stated, dependencies stated, CAPATCH handled as legacy where relevant, no out-of-scope files touched.
Rollback: Close the PR and discard only this agent folder changes if rejected.
Coordinator Notes: Suggested branch is chore/security-hygiene-audit. Agent may open a PR but must not merge it.

### TASK ID: UI-001

Agent: UI Smoke Baseline
State: NOT_STARTED
Goal: Document critical UI smoke scenarios and visual testing methodology. Do not execute real automation in this phase.
Allowed Files: docs/dev/agent-workbench/agents/ui-smoke/**
Forbidden Files: Product code, files outside assigned folder, other agent folders, main, merges, force-push, branch deletion. Global workbench files are read-only unless the user explicitly appoints the agent as Coordinator.
Inputs: Quality baseline, available UI tools, Master Status Board.
Output Required: UI_SMOKE_BASELINE.md, VISUAL_TESTING_GUIDE.md
Dependencies: Quality Baseline
Blocking Conditions: Need product-code changes, missing required evidence, conflict with another agent scope, CAPATCH active dependency, merge request, branch deletion request, or force-push request.
Definition of Done: Required outputs updated inside assigned folder, evidence listed, risks stated, dependencies stated, CAPATCH handled as legacy where relevant, no out-of-scope files touched.
Rollback: Close the PR and discard only this agent folder changes if rejected.
Coordinator Notes: Suggested branch is docs/ui-smoke-baseline. Agent may open a PR but must not merge it.

## WAVE 3 - Documentation and Integration

### TASK ID: DOC-001

Agent: Documentation / Onboarding
State: BLOCKED
Goal: Prepare plans to update onboarding docs without modifying final docs yet.
Allowed Files: docs/dev/agent-workbench/agents/documentation-onboarding/**
Forbidden Files: Product code, files outside assigned folder, other agent folders, main, merges, force-push, branch deletion. Global workbench files are read-only unless the user explicitly appoints the agent as Coordinator.
Inputs: Architecture inventories, quality baseline, PR triage, Master Status Board.
Output Required: GETTING_STARTED_PLAN.md, ARCHITECTURE_OVERVIEW_PLAN.md, RELEASE_PROCESS_PLAN.md
Dependencies: Architecture Audit, Quality Baseline, PR Triage
Blocking Conditions: Need product-code changes, missing required evidence, conflict with another agent scope, CAPATCH active dependency, merge request, branch deletion request, or force-push request.
Definition of Done: Required outputs updated inside assigned folder, evidence listed, risks stated, dependencies stated, CAPATCH handled as legacy where relevant, no out-of-scope files touched.
Rollback: Close the PR and discard only this agent folder changes if rejected.
Coordinator Notes: Suggested branch is docs/onboarding-refresh. Agent may open a PR but must not merge it.

### TASK ID: ICAP-001

Agent: Integration Captain
State: IN_PROGRESS
Goal: Consolidate reports, update integration sequence, and prepare final merge plan with risks, validations, and rollback protocols. Do not merge.
Allowed Files: docs/dev/agent-workbench/agents/integration-captain/**
Forbidden Files: Product code, files outside assigned folder, other agent folders, main, merges, force-push, branch deletion. Global workbench files are read-only unless the user explicitly appoints the agent as Coordinator.
Inputs: All agent reports, Master Status Board, Work Queue, Merge Readiness Checklist.
Output Required: INTEGRATION_SEQUENCE_REPORT.md, FINAL_MERGE_PLAN.md
Dependencies: All agents
Blocking Conditions: Need product-code changes, missing required evidence, conflict with another agent scope, CAPATCH active dependency, merge request, branch deletion request, or force-push request.
Definition of Done: Required outputs updated inside assigned folder, evidence listed, risks stated, dependencies stated, CAPATCH handled as legacy where relevant, no out-of-scope files touched.
Rollback: Close the PR and discard only this agent folder changes if rejected.
Coordinator Notes: Suggested branch is chore/integration-captain-report. Agent may open a PR but must not merge it.


## WAVE 4 - Real Execution

### TASK ID: EXEC-PRISMA

State: NOT_STARTED
Rule: Real PRISMA implementation is blocked until the PRISMA plan is approved by the user and Integration Captain.

### TASK ID: EXEC-CLEANUP

State: NOT_STARTED
Rule: Real branch cleanup is blocked until the Branch Cleanup Plan is approved by the user. No branches may be deleted from the workbench phase.

### TASK ID: EXEC-QUALITY-FIXES

State: NOT_STARTED
Rule: Real quality fixes are blocked until the Quality Baseline is reviewed and a fix plan is approved.

### TASK ID: EXEC-UI-AUTOMATION

State: NOT_STARTED
Rule: Real UI automation is blocked until UI Smoke Baseline and Visual Testing Guide are reviewed.
