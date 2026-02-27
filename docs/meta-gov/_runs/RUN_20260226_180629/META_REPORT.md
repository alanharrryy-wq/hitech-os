# META_REPORT

## Run Info

- run_id: `RUN_20260226_180629`
- timestamp_iso: `2026-02-26T18:06:29-06:00`
- timezone: `America/Mexico_City`

## Federation Status

- status: `DEGRADED`
- generated_at: `2026-02-27T00:06:29+00:00`

## Repos

| repo            | online | status          | docs_doctor     | report_path                                                                                                                                           |
| --------------- | -----: | --------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| hitech-frontend |   true | MISSING_TOOLING | MISSING_TOOLING | F:/OneDrive/Hitech/3.Proyectos/CHAT GPT AI Estudio/HITECH_AISTUDIO_SYSTEM/0.Origins/app/frontend/hitech-frontend/docs/govos/\_reports/FINAL_REPORT.md |
| hitech-os       |   true | OK              | OK              | F:/repos/hitech-os/docs/govos/\_reports/FINAL_REPORT.md                                                                                               |
| inversion-next  |   true | MISSING_TOOLING | MISSING_TOOLING | F:/repos/inversion-next/docs/govos/\_reports/FINAL_REPORT.md                                                                                          |

## Blockers

### Constitutional

- none

### Policy

- none

### Tooling

- hitech-frontend: Docs-Doctor missing
- hitech-frontend: FINAL_REPORT missing
- inversion-next: Docs-Doctor missing
- inversion-next: FINAL_REPORT missing

## Debt Summary

- global_total: 1
- hitech-os: 1

## Immediate Next Actions

1. Restore missing tooling (Docs-Doctor / reports) for degraded repositories.
2. Re-run `python -m tools.meta.meta_orchestrator --registry docs/meta-gov/REPO_REGISTRY.yaml --write`.

## Appendix: Repo Excerpts

### hitech-frontend

- No report excerpt available.

### hitech-os

```md
# FINAL REPORT

RESULT: OK
REPO_ROOT: F:/repos/hitech-os
CANONICAL_DOCS_ROOT: docs/govos

## Mandatory First Read

- KERNEL_CONTEXT.md: present
- docs/factory/FACTORY_RUNTIME_EXPLAINED.md: present
- additive_only_trigger: false
- resolution: pointer stub linked to docs/factory/CONTRACT.md
```

### inversion-next

- No report excerpt available.
