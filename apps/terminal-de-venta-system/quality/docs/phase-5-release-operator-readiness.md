# Phase 5: Release & Operator Readiness

Phase 5 is the final local-first release gate for PRISMA operator readiness.

It does not start services, mutate databases, require Cloudflare, or claim runtime health without evidence.

## Gates

| Gate | Purpose |
| --- | --- |
| Q26 | Launcher OS release readiness |
| Q27 | Evidence bundle readiness |
| Q28 | Cleanup and artifact hygiene |
| Q29 | Operator docs readiness |
| Q30 | Release profile readiness |
| Q31 | Automation improvement catalog readiness |

## Required evidence

- `latest_DIAGNOSE.zip` mechanism or documentation
- `latest_KILL_EVERYTHING.zip` mechanism or documentation
- `transcript.log` and `summary.json` evidence model
- `F:\descargasf` as operator handoff location
- `PRISMA_QUALITY_OS_<runId>` machine-readable reports
- 100 implemented automation improvements under `quality/automation/automation-improvements.json`

## No-fake-green rule

A gate cannot be READY without evidence. A blocked gate cannot be BLOCKED without findings. Phase 5 blockers must become S1 findings and warnings must become S3 findings.

## Rollback operativo y reparación de warnings Phase 5

Phase 5 distingue entre **blockers** que impiden declarar readiness y **warnings** que son limpieza operacional.
El paquete incluye `scripts/repair_phase5_warnings.py` para reparar, con backup y rollback, drift externo común en launchers y wrappers:

- `05_LEVANTAR_WEB_CONTROL_LOCAL.cmd` debe llamar claramente a `web_control_local.ps1`.
- `07_ABRIR_PANEL_CONTROL_3150.cmd` debe llamar claramente a `panel_3150.ps1`.
- Los wrappers no deben conservar referencias activas a `PRISMA_LAUNCHER_RUNS`; la evidencia debe apuntar a `F:\descargasf`.
- El operador debe tener una ruta de rollback documentada para deshacer reparaciones externas.

Uso recomendado desde la raíz `apps/terminal-de-venta-system`:

```powershell
py -3 quality\scripts\repair_phase5_warnings.py --dry-run --repo-root . --backup-root "F:\descargasf"
py -3 quality\scripts\repair_phase5_warnings.py --apply --repo-root . --backup-root "F:\descargasf"
py -3 quality\scripts\repair_phase5_warnings.py --verify --repo-root . --backup-root "F:\descargasf"
```

Rollback:

```powershell
$State = Get-Content "F:\descargasf\LATEST_PRISMA_PHASE5_WARNING_REPAIR.json" | ConvertFrom-Json
py -3 quality\scripts\repair_phase5_warnings.py --rollback --repo-root . --backup "$($State.backup)" --backup-root "F:\descargasf"
```

