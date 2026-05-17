<!-- agent-workbench-rescue-managed -->
# Master Status Board

| Agent | Current State | Evidence Source | Main Deliverable | Workbench Path | Depends On | Blocks | Risk Level | Coordinator Decision | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAPATCH Consolidation | CLOSED | capatch-consolidated.full.bundle legacy | N/A | N/A | None | None | LOW | DO_NOT_MERGE | No action. CAPATCH remains discarded, legacy-only, and unavailable as an active dependency. |
| PR Triage | NEEDS_UPDATE | Triage PRs en GitHub.pdf | PR_TRIAGE_REPORT.md | agents/pr-triage/ | Board Setup | Branch Cleanup, Integration Captain | MEDIUM | UPDATE_REQUIRED | Convert PDF to Markdown, update CAPATCH references as legacy/evidence, classify current PRs, and document merge/close/postpone recommendations. |
| Quality Baseline | NEEDS_UPDATE | Quality.pdf | QUALITY_BASELINE_REPORT.md and VALIDATION_COMMANDS.md | agents/quality/ | Board Setup | CI Hardening, Security/Hygiene, UI Smoke, Integration Captain | MEDIUM | UPDATE_REQUIRED | Convert PDF to Markdown, run quality/CI commands only as validation, document results, and propose fixes without modifying product code. |
| Monorepo Architecture Audit | NEEDS_UPDATE | arquitectura.pdf | MONOREPO_ARCHITECTURE_AUDIT.md, APP_INVENTORY.md, PACKAGE_INVENTORY.md | agents/architecture/ | Board Setup | PRISMA Plan, Branch Cleanup, Quality Baseline, Documentation/Onboarding, Integration Captain | HIGH | UPDATE_REQUIRED | Generate inventories from the PDF, produce architecture audit, and align all notes with CAPATCH closed. |
| Branch Cleanup Plan | NEEDS_UPDATE | Branch cleanup.pdf | BRANCH_CLEANUP_PLAN.md | agents/branch-cleanup/ | PR Triage, Architecture Audit | PRISMA Plan, Integration Captain | MEDIUM | UPDATE_REQUIRED | Convert PDF to Markdown and classify CAPATCH branches as evidence/legacy. Do not delete branches. |
| PRISMA Consolidation Plan | NEEDS_UPDATE | Prisma.pdf | PRISMA_CONSOLIDATION_PLAN.md | agents/prisma/ | Architecture Audit, Quality Baseline, PR Triage | Real Execution, Integration Captain | MEDIUM | UPDATE_REQUIRED | Convert PDF to Markdown and design a strategy that does not treat CAPATCH as dependency. |
| CI Hardening | NOT_STARTED | N/A | CI_HARDENING_REPORT.md | agents/ci-hardening/ | Quality Baseline | Security/Hygiene, Integration Captain | MEDIUM | WAIT | Wait for Quality Baseline, then document workflow/dependabot hardening proposals without editing workflows. |
| Security / Repo Hygiene | NOT_STARTED | N/A | SECURITY_HYGIENE_REPORT.md, LOCAL_ARTIFACT_POLICY.md | agents/security-hygiene/ | Quality Baseline | Integration Captain | MEDIUM | WAIT | Wait for Quality Baseline, then document secrets/artifacts/.gitignore recommendations without modifying repo configs. |
| UI Smoke Baseline | NOT_STARTED | N/A | UI_SMOKE_BASELINE.md, VISUAL_TESTING_GUIDE.md | agents/ui-smoke/ | Quality Baseline | Integration Captain | LOW | WAIT | Wait for Quality Baseline, then document visual smoke methodology. Do not edit UI code. |
| Documentation / Onboarding | BLOCKED | N/A | GETTING_STARTED_PLAN.md, ARCHITECTURE_OVERVIEW_PLAN.md, RELEASE_PROCESS_PLAN.md | agents/documentation-onboarding/ | Architecture Audit, Quality Baseline, PR Triage | Final Integration | MEDIUM | WAIT | Do not start until architecture, quality, and triage reports exist. |
| Integration Captain | IN_PROGRESS | Board and reconciliation docs | INTEGRATION_SEQUENCE_REPORT.md, FINAL_MERGE_PLAN.md | agents/integration-captain/ | All agents | Real Execution | HIGH | UPDATE_REQUIRED | Continue updating integration sequence and checklist as reports arrive. Do not merge. |

## Notes

- Delivered PDFs are evidence already received, but their actionable Markdown reports are still NEEDS_UPDATE until converted and reconciled.
- CAPATCH stays visible in this board because it is a critical safety constraint: CLOSED, legacy-only, and DO_NOT_MERGE.
- Only the Coordinator may edit this global board. Agents must treat it as read-only.
