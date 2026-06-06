# Workspace Changelog

## 2026-04-10

### Workspace status
- consolidación integral del workspace de `capatch` dentro de `code-atlas`
- `capatch.py` confirmado como entrada estable del workspace
- `capatch_cli.main` establecido como entrypoint operativo del CLI

### Engine y verify
- patch pipeline con preflight, preview, apply y verify integrados
- incorporación de verificación por superficie y por riesgo
- smokes Python separados para compile, import y boot
- verification floor formal para distintos niveles de evidencia

### Lifecycle transaccional
- journal de transacción para patch runs
- lifecycle explícito para apply, verify y rollback
- mejor legibilidad del estado final de cada corrida

### Runtime y plugins
- alineación del runtime/plugins al contrato `6.0.0`
- activación limpia de plugins esenciales:
  - `fixer.safe-runtime-actions`
  - `recommender.safe-fix-plan`
  - `verifier.post-fix-verifier`
- runtime de plugins consolidado en `capatch_plugins/runtime_core.py`
- environment guard y required plugins por default

### Auditoría y evidence
- patch runs con metadata más rica
- telemetry fresca, versionada y trazable
- refresh de reports operativos
- reports reforzados para smoke, rollback, benchmark y readiness

### Baselines y promoción
- baselines de primera clase para promoción y restore
- compare y restore integrados al tooling
- readiness gate formal para decidir estados promocionables

### Workspace hygiene
- cleaner de workspace integrado en startup y shutdown
- backups operativos bajo `.capatch/backups/patches`
- mejor separación entre source, evidence y artefactos operativos

### Tooling destacado
- `capatch_master_consolidation_v2.py` como revalidador resume-aware recomendado
- `tooling/refresh_workspace_reports.py`
- `tooling/recover_patch_transaction.py`
- `tooling/manage_baselines.py`
- `tooling/run_readiness_gate.py`

### Documentación actualizada
- `ADR-001-boundaries.md`
- `WORKSPACE_README.md`
- `OPERATING_GUIDE.md`
- `TROUBLESHOOTING.md`
- `CAPATCH_CLOSURE_REPORT.md`
