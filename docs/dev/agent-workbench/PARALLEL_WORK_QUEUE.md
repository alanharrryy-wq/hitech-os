# Parallel Work Queue

## Wave 0 - Coordination

### WB-SETUP

State: DELIVERED_NOT_PUSHED

Goal: create this Agent Workbench and open a documentation-only PR.

Allowed files: docs/dev/agent-workbench/**

Forbidden files: everything else.

## Wave 1 - Analysis

### TRIAGE-001 - PR Triage

State: NEEDS_UPDATE

Output: agents/pr-triage/PR_TRIAGE_REPORT.md

Inputs: Triage PRs en GitHub.pdf, Master Status Board, open PR list.

Rules: CAPATCH is legacy/evidence and must not be recommended for merge.

### QUAL-001 - Quality Baseline

State: NEEDS_UPDATE

Output: agents/quality/QUALITY_BASELINE_REPORT.md and VALIDATION_COMMANDS.md

Inputs: Quality.pdf and package scripts.

Rules: document commands and results without modifying product code.

### ARCH-001 - Monorepo Architecture Audit

State: NEEDS_UPDATE

Output: agents/architecture/APP_INVENTORY.md, PACKAGE_INVENTORY.md, MONOREPO_ARCHITECTURE_AUDIT.md

Inputs: arquitectura.pdf and repo analysis tools.

Rules: treat apps/code-atlas/capatch_system as legacy.

### BCLEAN-001 - Branch Cleanup Plan

State: NEEDS_UPDATE

Depends on: PR Triage and Architecture Audit.

Output: agents/branch-cleanup/BRANCH_CLEANUP_PLAN.md

Rules: no real branch deletion.

### PRISMA-001 - PRISMA Consolidation Plan

State: NEEDS_UPDATE

Depends on: Architecture Audit, Quality Baseline, PR Triage.

Output: agents/prisma/PRISMA_CONSOLIDATION_PLAN.md

Rules: planning only, no implementation.

## Wave 2 - Risk and Validation

CI Hardening, Security Hygiene, and UI Smoke wait for Quality Baseline.

## Wave 3 - Documentation and Integration

Documentation/Onboarding waits for PR Triage, Architecture Audit, and Quality Baseline.

Integration Captain consolidates all reports into FINAL_MERGE_PLAN.md.

## Wave 4 - Real Execution

Real code execution requires approved plans and human review.
