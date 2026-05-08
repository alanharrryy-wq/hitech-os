<!-- agent-workbench-rescue-managed -->
# Agent Report Reconciliation

| Agent | Evidence | Reconciliation State | Notes | Active Dependency? |
| --- | --- | --- | --- | --- |
| CAPATCH Consolidation | capatch-consolidated.full.bundle legacy | CLOSED / DISCARDED_FOR_SAFETY / NO_PUSH / NO_PR / DO_NOT_MERGE | Historical evidence only. Must not appear as active dependency. | NO |
| PR Triage | Triage PRs en GitHub.pdf | NEEDS_UPDATE | PDF delivered outside main. Convert to scoped Markdown and reconcile before review. | YES |
| Quality Baseline | Quality.pdf | NEEDS_UPDATE | PDF delivered outside main. Convert to scoped Markdown and reconcile before review. | YES |
| Monorepo Architecture Audit | arquitectura.pdf | NEEDS_UPDATE | PDF delivered outside main. Convert to scoped Markdown and reconcile before review. | YES |
| Branch Cleanup Plan | Branch cleanup.pdf | NEEDS_UPDATE | PDF delivered outside main. Convert to scoped Markdown and reconcile before review. | YES |
| PRISMA Consolidation Plan | Prisma.pdf | NEEDS_UPDATE | PDF delivered outside main. Convert to scoped Markdown and reconcile before review. | YES |
| CI Hardening | N/A | NOT_STARTED | Wait for Quality Baseline, then document workflow/dependabot hardening proposals without editing workflows. | YES |
| Security / Repo Hygiene | N/A | NOT_STARTED | Wait for Quality Baseline, then document secrets/artifacts/.gitignore recommendations without modifying repo configs. | YES |
| UI Smoke Baseline | N/A | NOT_STARTED | Wait for Quality Baseline, then document visual smoke methodology. Do not edit UI code. | YES |
| Documentation / Onboarding | N/A | BLOCKED | Do not start until architecture, quality, and triage reports exist. | YES |
| Integration Captain | Board and reconciliation docs | IN_PROGRESS | Coordinator/integration stream already active. Continue consolidating agent reports into integration sequence and final merge plan. Do not merge. | YES |

## Contradiction Register

- v2 scaffold marked some delivered-PDF work as DELIVERED_NOT_PUSHED only. v3 restores the sharper operating distinction: PDF evidence exists, but Markdown conversion remains NEEDS_UPDATE.
- v2 removed CAPATCH from the main board. v3 restores CAPATCH as a first-class safety row with DO_NOT_MERGE.
- v2 marked Integration Captain as NOT_STARTED. v3 restores it to IN_PROGRESS because the board/reconciliation system is already being actively coordinated.

## Dependency Register

- PR Triage feeds Branch Cleanup and Integration Captain.
- Architecture Audit and Quality Baseline feed PRISMA and Documentation / Onboarding.
- Quality Baseline feeds CI Hardening, Security / Repo Hygiene, and UI Smoke.
- CAPATCH must not be resurrected as an active stream, dependency, merge candidate, or cleanup target without explicit human approval.
