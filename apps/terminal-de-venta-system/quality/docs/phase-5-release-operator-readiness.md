# PRISMA PQOS Phase 5: Release & Operator Readiness

## Objetivo

Phase 5 es la aduana final antes de PR/release. No agrega gates decorativos. Valida que PRISMA pueda operarse, diagnosticarse, auditarse, empacarse y entregarse con evidencia útil.

## Regla madre

- Tablet opera.
- PC gobierna.
- Mobile supervisa.
- Core registra.
- Control audita.

## Gates Phase 5

| Gate | Nombre | Bloquea cuando |
| --- | --- | --- |
| Q26 | Launcher OS release readiness | Faltan launchers 01-09, wrappers oficiales, ZIP directo a `F:\descargasf`, kill ports o aparece `PRISMA_LAUNCHER_RUNS`. |
| Q27 | Evidence bundle readiness | No hay mecanismo claro para `latest_DIAGNOSE.zip`, reportes, transcript, summary o quality outputs en `F:\descargasf`. |
| Q28 | Cleanup and artifact hygiene | Hay `.bak_*`, `legacy_launchers` activo, scripts temporales `prisma_*_fix.py` o basura permanente. |
| Q29 | Operator docs readiness | Faltan README operador, puertos, launchers, diagnóstico, rollback, ZIPs o flujos local/Cloudflare. |
| Q30 | Release profile readiness | `quality:phase5`, `quality:release`, profile `phase5.json` o manifest no reconocen Q26-Q30. |

## Matriz de puertos

| Puerto | Superficie | Obligación Phase 5 |
| --- | --- | --- |
| 3000 | Chart Lab | Validar por launcher local y ZIP de evidencia. |
| 3100 | Legacy cleanup-only | Solo kill everything si aparece. |
| 3110 | PRISMA Web / EIT / página | Validar operación local/Cloudflare según launcher. |
| 3120 | Tablet | Validar kill everything. |
| 3130 | PC Backoffice | Validar kill everything. |
| 3140 | Mobile | Validar kill everything. |
| 3150 | Control Center | Validar panel y diagnóstico. |
| 3200 | Legacy cleanup-only | Solo kill everything si aparece. |

## Matriz de launchers

| Launcher | Wrapper esperado | Propósito |
| --- | --- | --- |
| 01_LEVANTAR_TODO_LOCAL.cmd | local_up.ps1 | Levantar stack local. |
| 02_LEVANTAR_TODO_CLOUDFLARE.cmd | cloudflare_up.ps1 | Levantar túnel/capa Cloudflare sin tocar config a lo bruto. |
| 03_LEVANTAR_TODO_LOCAL_Y_CLOUDFLARE.cmd | all_up.ps1 | Levantar local y Cloudflare. |
| 04_DIAGNOSTICO_LOCAL_Y_CLOUDFLARE.cmd | health.ps1 | Diagnóstico y evidencia. |
| 05_LEVANTAR_WEB_CONTROL_LOCAL.cmd | web_control_local.ps1 | Web Control local. |
| 06_LEVANTAR_WEB_CONTROL_LOCAL_Y_CLOUDFLARE.cmd | web_control_cloudflare.ps1 | Web Control local y Cloudflare. |
| 07_ABRIR_PANEL_CONTROL_3150.cmd | panel_3150.ps1 | Abrir panel 3150. |
| 08_LEVANTAR_CHART_LAB_LOCAL.cmd | chart_lab_local.ps1 | Chart Lab local 3000. |
| 09_KILL_EVERYTHING_PRISMA.cmd | kill_everything.ps1 | Cierre total y limpieza de puertos. |

## Matriz de evidencia

| Evidencia | Ubicación esperada | Nota |
| --- | --- | --- |
| Diagnóstico | `F:\descargasf\latest_DIAGNOSE.zip` | Debe contener o documentar `transcript.log`, `summary.json` y reportes Control Center si existen. |
| Kill everything | `F:\descargasf\latest_KILL_EVERYTHING.zip` | Debe documentar puertos cerrados. |
| Quality outputs | `F:\descargasf\PRISMA_QUALITY_OS_*` | Deben quedar fuera del repo como evidencia final. |
| Phase 5 result | `F:\descargasf\PRISMA_PQOS_PHASE5_RELEASE_OPERATOR_READINESS_*_RESULT.zip` | Generado por `pnpm quality:phase5` o por este instalador. |

## No fake green

- No se inventan servicios corriendo.
- Servicios locales opcionales apagados son evidencia, no warning.
- Servicios required apagados sí bloquean.
- Un diagnóstico con health operativo `FAIL` puede ser evidencia válida si el wrapper lo empaca y no oculta fallas reales.

## Comandos finales

```powershell
pnpm quality:phase5
pnpm quality:release
pnpm quality:pr
```

## Rollback

Este paquete instala con backup en `.prisma_backups`. Si la verificación falla, el instalador revierte automáticamente los archivos modificados.
