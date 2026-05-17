<!-- agent-workbench-rescue-managed -->
# Handoff Prompts

Copy the relevant prompt when activating an agent. These prompts are complete handoffs and must not be split across messages.

### PROMPT FOR PR TRIAGE

Act as PR Triage Agent for hitech-os.

Suggested branch: docs/pr-triage-report
Assigned folder: docs/dev/agent-workbench/agents/pr-triage/

Allowed files:
PR_TRIAGE_REPORT.md, README.md, and files under agents/pr-triage/evidence/

Forbidden files:
Product code, other agent folders, .gitignore, workflows, root files, main, merges, force-push, branch deletion.

Inputs:
Triage PRs en GitHub.pdf, Master Status Board, open PR list. CAPATCH is closed and cannot be treated as pending consolidation.

Objective / Output:
Create PR_TRIAGE_REPORT.md listing open PRs with number, title, branch, type, affected files, dependencies, conflict risk, and recommendation. Mark CAPATCH-related PRs as legacy/evidence and do not recommend them for merge.

Required outputs:
- PR_TRIAGE_REPORT.md

Definition of Done:
Report is complete, aligned with the board, removes CAPATCH as active stream, and proposes clear priorities. PR may be opened but must not be merged.

Rollback:
Close the PR and discard only this agent folder changes if the report is rejected. No main changes.

Restrictions:
Do not modify main. Do not merge PRs. Do not delete branches. Do not force-push. Work only in the assigned folder. Treat global workbench files as read-only unless explicitly appointed Coordinator.

### PROMPT FOR QUALITY BASELINE

Act as Quality Baseline Agent for hitech-os.

Suggested branch: docs/quality-baseline-report
Assigned folder: docs/dev/agent-workbench/agents/quality/

Allowed files:
QUALITY_BASELINE_REPORT.md, VALIDATION_COMMANDS.md, README.md, and files under agents/quality/evidence/

Forbidden files:
Any file outside this folder, product code, scripts, lockfiles, main, merges, force-push, branch deletion.

Inputs:
Quality.pdf, package.json quality/ci scripts, guard-rail tools, Master Status Board. CAPATCH is closed.

Objective / Output:
Create VALIDATION_COMMANDS.md with exact commands and QUALITY_BASELINE_REPORT.md with lint/test warnings, failures, timings, environment notes, and improvement proposals without modifying code.

Required outputs:
- QUALITY_BASELINE_REPORT.md
- VALIDATION_COMMANDS.md

Definition of Done:
Both Markdown files exist, document executions/results clearly, and contain no code-modification instructions. PR may be opened but must not be merged.

Rollback:
Close the PR and discard only this agent folder changes if rejected.

Restrictions:
Do not modify main. Do not merge PRs. Do not delete branches. Do not force-push. Work only in the assigned folder. Treat global workbench files as read-only unless explicitly appointed Coordinator.

### PROMPT FOR MONOREPO ARCHITECTURE AUDIT

Act as Monorepo Architecture Audit Agent for hitech-os.

Suggested branch: docs/monorepo-architecture-audit
Assigned folder: docs/dev/agent-workbench/agents/architecture/

Allowed files:
APP_INVENTORY.md, PACKAGE_INVENTORY.md, MONOREPO_ARCHITECTURE_AUDIT.md, README.md, and files under agents/architecture/evidence/

Forbidden files:
Product code, other agent folders, mutex files, build scripts, main, merges, force-push, branch deletion.

Inputs:
arquitectura.pdf, repo analysis outputs, Master Status Board. apps/code-atlas/capatch_system is legacy.

Objective / Output:
Create inventories for apps and packages plus an architecture audit covering cross-dependencies, workspace compliance, violations, and recommendations aligned with CAPATCH closed.

Required outputs:
- APP_INVENTORY.md
- PACKAGE_INVENTORY.md
- MONOREPO_ARCHITECTURE_AUDIT.md

Definition of Done:
Three Markdown files are complete and coherent. PR may be opened but must not be merged.

Rollback:
Close the PR and discard only this agent folder changes if rejected.

Restrictions:
Do not modify main. Do not merge PRs. Do not delete branches. Do not force-push. Work only in the assigned folder. Treat global workbench files as read-only unless explicitly appointed Coordinator.

### PROMPT FOR BRANCH CLEANUP PLAN

Act as Branch Cleanup Plan Agent for hitech-os.

Suggested branch: docs/branch-cleanup-plan
Assigned folder: docs/dev/agent-workbench/agents/branch-cleanup/

Allowed files:
BRANCH_CLEANUP_PLAN.md, README.md, and files under agents/branch-cleanup/evidence/

Forbidden files:
Any file outside this folder. Do not modify, delete, or rename branches. No main, merges, force-push, branch deletion.

Inputs:
Branch cleanup.pdf, PR triage report when available, app/package inventories, Master Status Board. CAPATCH branches are evidence/legacy until classified.

Objective / Output:
Create branch cleanup plan with categories: active, legacy, evidence, superseded, needs-inspection. Include deletion criteria, backup protocol, author notification, and explicit CAPATCH no-delete rule.

Required outputs:
- BRANCH_CLEANUP_PLAN.md

Definition of Done:
Plan is complete and aligned with board. PR may be opened but must not be merged.

Rollback:
Close the PR and discard only this agent folder changes if rejected.

Restrictions:
Do not modify main. Do not merge PRs. Do not delete branches. Do not force-push. Work only in the assigned folder. Treat global workbench files as read-only unless explicitly appointed Coordinator.

### PROMPT FOR PRISMA CONSOLIDATION PLANNING

Act as PRISMA Consolidation Planning Agent for hitech-os.

Suggested branch: docs/prisma-consolidation-plan
Assigned folder: docs/dev/agent-workbench/agents/prisma/

Allowed files:
PRISMA_CONSOLIDATION_PLAN.md, README.md, and files under agents/prisma/evidence/

Forbidden files:
PRISMA product code, other agent folders, mutex files, main, merges, force-push, branch deletion.

Inputs:
Prisma.pdf, app/package inventories, quality baseline, PR triage, Master Status Board. CAPATCH must not appear as dependency.

Objective / Output:
Create PRISMA_CONSOLIDATION_PLAN.md with related branches/PRs, dependencies, preconditions, ordered consolidation steps, risks, owners, and Wave 4 approval boundary.

Required outputs:
- PRISMA_CONSOLIDATION_PLAN.md

Definition of Done:
Plan is complete, aligned with inventories and baseline, and excludes CAPATCH as dependency. PR may be opened but must not be merged.

Rollback:
Close the PR and discard only this agent folder changes if rejected.

Restrictions:
Do not modify main. Do not merge PRs. Do not delete branches. Do not force-push. Work only in the assigned folder. Treat global workbench files as read-only unless explicitly appointed Coordinator.

### PROMPT FOR CI HARDENING

Act as CI Hardening Agent for hitech-os.

Suggested branch: chore/ci-actions-hardening
Assigned folder: docs/dev/agent-workbench/agents/ci-hardening/

Allowed files:
CI_HARDENING_REPORT.md, README.md, and files under agents/ci-hardening/evidence/

Forbidden files:
.github/workflows/**, .github/dependabot.yml, product code, any file outside this folder, main, merges, force-push, branch deletion.

Inputs:
Read-only workflows, dependabot.yml, quality baseline, security recommendations.

Objective / Output:
Document CI risks and proposed hardening. Do not implement workflow changes.

Required outputs:
- CI_HARDENING_REPORT.md

Definition of Done:
Report has clear recommendations and waits for Integration Captain approval before real changes.

Rollback:
Close the PR and discard only this agent folder changes if rejected.

Restrictions:
Do not modify main. Do not merge PRs. Do not delete branches. Do not force-push. Work only in the assigned folder. Treat global workbench files as read-only unless explicitly appointed Coordinator.

### PROMPT FOR SECURITY / REPO HYGIENE

Act as Security / Repo Hygiene Agent for hitech-os.

Suggested branch: chore/security-hygiene-audit
Assigned folder: docs/dev/agent-workbench/agents/security-hygiene/

Allowed files:
SECURITY_HYGIENE_REPORT.md, LOCAL_ARTIFACT_POLICY.md, README.md, and files under agents/security-hygiene/evidence/

Forbidden files:
.gitignore, workflows, product code, any file outside this folder, main, merges, force-push, branch deletion.

Inputs:
Repo hygiene tools, quality baseline, Master Status Board.

Objective / Output:
Document secrets/artifact findings and local artifact policy. Suggest .gitignore entries without editing .gitignore.

Required outputs:
- SECURITY_HYGIENE_REPORT.md
- LOCAL_ARTIFACT_POLICY.md

Definition of Done:
Both Markdown files are complete and wait for Integration Captain coordination before real changes.

Rollback:
Close the PR and discard only this agent folder changes if rejected.

Restrictions:
Do not modify main. Do not merge PRs. Do not delete branches. Do not force-push. Work only in the assigned folder. Treat global workbench files as read-only unless explicitly appointed Coordinator.

### PROMPT FOR UI SMOKE BASELINE

Act as UI Smoke Baseline Agent for hitech-os.

Suggested branch: docs/ui-smoke-baseline
Assigned folder: docs/dev/agent-workbench/agents/ui-smoke/

Allowed files:
UI_SMOKE_BASELINE.md, VISUAL_TESTING_GUIDE.md, README.md, and files under agents/ui-smoke/evidence/

Forbidden files:
UI code, workflows, other agent folders, main, merges, force-push, branch deletion.

Inputs:
Quality baseline, available UI tools, Master Status Board.

Objective / Output:
Document critical UI smoke scenarios and visual testing methodology. Do not execute real automation in this phase.

Required outputs:
- UI_SMOKE_BASELINE.md
- VISUAL_TESTING_GUIDE.md

Definition of Done:
Both documents are complete and clear. PR may be opened but must not be merged.

Rollback:
Close the PR and discard only this agent folder changes if rejected.

Restrictions:
Do not modify main. Do not merge PRs. Do not delete branches. Do not force-push. Work only in the assigned folder. Treat global workbench files as read-only unless explicitly appointed Coordinator.

### PROMPT FOR DOCUMENTATION / ONBOARDING

Act as Documentation / Onboarding Agent for hitech-os.

Suggested branch: docs/onboarding-refresh
Assigned folder: docs/dev/agent-workbench/agents/documentation-onboarding/

Allowed files:
GETTING_STARTED_PLAN.md, ARCHITECTURE_OVERVIEW_PLAN.md, RELEASE_PROCESS_PLAN.md, README.md, and files under agents/documentation-onboarding/evidence/

Forbidden files:
Root README, final docs, product code, main, merges, force-push, branch deletion.

Inputs:
Architecture inventories, quality baseline, PR triage, Master Status Board.

Objective / Output:
Prepare plans to update onboarding docs without modifying final docs yet.

Required outputs:
- GETTING_STARTED_PLAN.md
- ARCHITECTURE_OVERVIEW_PLAN.md
- RELEASE_PROCESS_PLAN.md

Definition of Done:
Plans are complete and aligned with upstream reports.

Rollback:
Close the PR and discard only this agent folder changes if rejected.

Restrictions:
Do not modify main. Do not merge PRs. Do not delete branches. Do not force-push. Work only in the assigned folder. Treat global workbench files as read-only unless explicitly appointed Coordinator.

### PROMPT FOR INTEGRATION CAPTAIN

Act as Integration Captain Agent for hitech-os.

Suggested branch: chore/integration-captain-report
Assigned folder: docs/dev/agent-workbench/agents/integration-captain/

Allowed files:
INTEGRATION_SEQUENCE_REPORT.md, FINAL_MERGE_PLAN.md, README.md, and files under agents/integration-captain/evidence/

Forbidden files:
Any file outside this folder unless acting as Coordinator, product code, main, merges, force-push, branch deletion.

Inputs:
All agent reports, Master Status Board, Work Queue, Merge Readiness Checklist.

Objective / Output:
Consolidate reports, update integration sequence, and prepare final merge plan with risks, validations, and rollback protocols. Do not merge.

Required outputs:
- INTEGRATION_SEQUENCE_REPORT.md
- FINAL_MERGE_PLAN.md

Definition of Done:
Sequence report and final merge plan are updated. No code merge decision is made without human approval.

Rollback:
Close the PR and discard only this agent folder changes if rejected.

Restrictions:
Do not modify main. Do not merge PRs. Do not delete branches. Do not force-push. Work only in the assigned folder. Treat global workbench files as read-only unless explicitly appointed Coordinator.
