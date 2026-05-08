# Master Status Board

| Agent | Current State | Evidence Source | Main Deliverable | Workbench Path | Depends On | Blocks | Risk | Coordinator Decision | Next Action |
|---|---|---|---|---|---|---|---|---|---|
| CAPATCH Consolidation | CLOSED | capatch-consolidated.full.bundle legacy | N/A | N/A | N/A | N/A | LOW | DO_NOT_MERGE | No action. CAPATCH remains discarded. |
| PR Triage | NEEDS_UPDATE | Triage PRs en GitHub.pdf | PR_TRIAGE_REPORT.md | agents/pr-triage/ | Board Setup | Branch Cleanup | MEDIUM | UPDATE_REQUIRED | Convert PDF to MD, mark CAPATCH as legacy, classify current PRs. |
| Quality Baseline | NEEDS_UPDATE | Quality.pdf | QUALITY_BASELINE_REPORT.md and VALIDATION_COMMANDS.md | agents/quality/ | Board Setup | CI Hardening, Security/Hygiene, UI Smoke | MEDIUM | UPDATE_REQUIRED | Convert PDF to MD, run quality and CI scripts, document results. |
| Monorepo Architecture Audit | NEEDS_UPDATE | arquitectura.pdf | APP_INVENTORY.md, PACKAGE_INVENTORY.md, MONOREPO_ARCHITECTURE_AUDIT.md | agents/architecture/ | Board Setup | PRISMA Plan, Branch Cleanup | HIGH | UPDATE_REQUIRED | Generate inventories and align with CAPATCH closed. |
| Branch Cleanup Plan | NEEDS_UPDATE | Branch cleanup.pdf | BRANCH_CLEANUP_PLAN.md | agents/branch-cleanup/ | PR Triage, Architecture Audit | PRISMA Plan | MEDIUM | UPDATE_REQUIRED | Convert PDF to MD and classify CAPATCH branches as evidence/legacy. |
| PRISMA Consolidation Plan | NEEDS_UPDATE | Prisma.pdf | PRISMA_CONSOLIDATION_PLAN.md | agents/prisma/ | Architecture Audit, Quality Baseline, PR Triage | Real Execution | MEDIUM | UPDATE_REQUIRED | Convert PDF to MD and design strategy without CAPATCH as dependency. |
| CI Hardening | NOT_STARTED | N/A | CI_HARDENING_REPORT.md | agents/ci-hardening/ | Quality Baseline | Security/Hygiene | MEDIUM | WAIT | Wait for Quality Baseline. |
| Security / Repo Hygiene | NOT_STARTED | N/A | SECURITY_HYGIENE_REPORT.md and LOCAL_ARTIFACT_POLICY.md | agents/security-hygiene/ | Quality Baseline | N/A | MEDIUM | WAIT | Wait for Quality Baseline. |
| UI Smoke Baseline | NOT_STARTED | N/A | UI_SMOKE_BASELINE.md and VISUAL_TESTING_GUIDE.md | agents/ui-smoke/ | Quality Baseline | N/A | LOW | WAIT | Wait for Quality Baseline. |
| Documentation / Onboarding | BLOCKED | N/A | GETTING_STARTED_PLAN.md, ARCHITECTURE_OVERVIEW_PLAN.md, RELEASE_PROCESS_PLAN.md | agents/documentation-onboarding/ | Architecture Audit, Quality Baseline, PR Triage | Final Integration | MEDIUM | WAIT | Do not start until architecture, quality, and triage reports exist. |
| Integration Captain | IN_PROGRESS | Board and reconciliation docs | INTEGRATION_SEQUENCE_REPORT.md and FINAL_MERGE_PLAN.md | agents/integration-captain/ | All agents | Real Execution | HIGH | UPDATE_REQUIRED | Continue updating sequence as reports arrive. |

## Note

Delivered PDFs are DELIVERED_NOT_PUSHED. Convert them to Markdown and align them with this board before review.
