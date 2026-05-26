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

- `latest_ALL_LOCAL.zip`, `latest_ALL_LOCAL_CLOUDFLARE.zip`, `latest_MODULE_CLOUDFLARE.zip`, and `latest_DEPENDENCY_ATLAS_OPEN.zip` mechanism or documentation
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

- `00_KILL_ALL_LOCAL.cmd` debe llamar claramente a `kill_everything.ps1`.
- `01_LEVANTAR_TODO_LOCAL.cmd` debe llamar claramente a `local_up.ps1`.
- `02_LEVANTAR_TODO_LOCAL_CLOUDFLARE.cmd` debe llamar claramente a `all_up.ps1`.
- `03_LEVANTAR_SOLO_UN_MODULO.cmd` debe llamar claramente a `module_cloudflare.ps1`.
- `04_ABRIR_ATLAS_DEPENDENCIAS.cmd` debe llamar claramente a `open_dependency_atlas.ps1`.
- `09_KILL_EVERYTHING_PRISMA.cmd` debe llamar claramente a `kill_everything.ps1`.
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
