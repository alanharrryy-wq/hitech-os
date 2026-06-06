# CAPATCH Operating Guide

Guía operativa del workspace `capatch_system` para correr patches seguros, diagnóstico, baselines y readiness con una rutina clara y repetible.

## Ruta base del workspace

```powershell
$root = "F:\repos\hitech-os\apps\code-atlas\capatch_system"
```

## Rutina diaria recomendada

### 1. Verifica salud del runtime
```powershell
py -3 "$root\capatch.py" --plugin-health
py -3 "$root\capatch.py" --smoke-test
py -3 "$root\tooling\run_readiness_gate.py"
```

### 2. Ejecuta patch seguro por stdin
```powershell
$target = "C:\ruta\objetivo"
Get-Content .\ops.json -Raw | py -3 "$root\capatch.py" --root-dir $target --ops-stdin --dry-run
Get-Content .\ops.json -Raw | py -3 "$root\capatch.py" --root-dir $target --ops-stdin
```

### 3. Corre diagnóstico cuando el caso requiere contexto
```powershell
$target = "C:\ruta\objetivo"
py -3 "$root\capatch.py" --diagnose --target-path $target
```

### 4. Genera support bundle
```powershell
$target = "C:\ruta\objetivo"
py -3 "$root\capatch.py" --support-bundle --target-path $target --bundle-format md
```

### 5. Genera fix-plan y aplica fixes
```powershell
$target = "C:\ruta\objetivo"
py -3 "$root\capatch.py" --fix-plan --target-path $target
py -3 "$root\capatch.py" --apply-fixes --target-path $target
```

### 6. Revisa checkpoints y rollback
```powershell
py -3 "$root\capatch.py" --list-checkpoints
py -3 "$root\capatch.py" --rollback-last --dry-run
py -3 "$root\capatch.py" --rollback-last
```

## Estrategias de patch y guardrails nuevos

### Selector automático
`capatch` ya decide una estrategia sugerida por corrida y la deja anotada en salida, riesgo y journal.

Estrategias principales:
- `exact`: cambios literales, chicos y estables
- `guarded`: cambios con riesgo medio o anchors frágiles
- `transactional`: batches que necesitan coordinación por lote
- `structural`: superficie TS/JS/JSX con intención más semántica
- `probe-only`: inspección sin escritura

### Forzar o sugerir estrategia
```powershell
Get-Content .\ops.json -Raw | py -3 "$root\capatch.py" --root-dir $target --ops-stdin --strategy exact --dry-run
Get-Content .\ops.json -Raw | py -3 "$root\capatch.py" --root-dir $target --ops-stdin --strategy guarded --dry-run
Get-Content .\ops.json -Raw | py -3 "$root\capatch.py" --root-dir $target --ops-stdin --strategy transactional --dry-run
```

### Probe-only
Úsalo cuando quieras solo clasificar, ver preview y revisar guardrails.

```powershell
Get-Content .\ops.json -Raw | py -3 "$root\capatch.py" --root-dir $target --ops-stdin --probe-only --dry-run
```

### Estrategias advisory / superficies estructurales
Si el selector marca una estrategia advisory o una superficie estructural todavía sensible, deja primero preview y luego decide si autorizas ejecución explícita.

```powershell
Get-Content .\ops.json -Raw | py -3 "$root\capatch.py" --root-dir $target --ops-stdin --allow-advisory-strategy --dry-run
```

### Guardrail de riesgo alto
Si el cambio queda `high` o `critical`, la corrida debe pasar por `--dry-run` primero.

```powershell
Get-Content .\ops.json -Raw | py -3 "$root\capatch.py" --root-dir $target --ops-stdin --dry-run
```

Señales prácticas:
- si toca varios archivos y anchors cortitos, normalmente caerá en `guarded`
- si el target es TS/TSX/JS/JSX y el cambio huele a imports/JSX/objetos, el selector empuja hacia `structural`
- si el cambio es puro replace literal y limpio, normalmente caerá en `exact`

## Operación con baselines

### Listar baselines
```powershell
py -3 "$root\tooling\manage_baselines.py" --list
```

### Promover el estado más reciente a baseline
```powershell
py -3 "$root\tooling\manage_baselines.py" --promote-latest --label "baseline-operativa"
```

### Comparar contra una baseline
```powershell
py -3 "$root\tooling\manage_baselines.py" --compare --baseline "baseline-operativa"
```

### Restaurar baseline
```powershell
py -3 "$root\tooling\manage_baselines.py" --restore --baseline "baseline-operativa" --dry-run
py -3 "$root\tooling\manage_baselines.py" --restore --baseline "baseline-operativa"
```

## Revalidación consolidada del workspace

### Revalidación resume-aware
Usa este comando cuando quieras confirmar que el workspace ya quedó alineado y quieres una pasada limpia de revalidación.

```powershell
$py = "F:\descargasf\capatch_master_consolidation_v2.py"
py -3 $py --root-dir "$root" --patch-dir "F:\descargasf" --out-dir "F:\descargasf"
```

### Solo dry-run de consolidación
```powershell
$py = "F:\descargasf\capatch_master_consolidation_v2.py"
py -3 $py --root-dir "$root" --patch-dir "F:\descargasf" --out-dir "F:\descargasf" --dry-run-only
```

## Refresh de reports y telemetry

Cuando quieras dejar reports y telemetry perfectamente actualizados:

```powershell
py -3 "$root\tooling\refresh_workspace_reports.py"
```

## Operación de cierre / promoción

Para declarar un estado listo para promover:

```powershell
py -3 -m compileall "$root"
py -3 "$root\capatch.py" --smoke-test
py -3 "$root\capatch.py" --plugin-health
py -3 "$root\tooling\run_phase0_ac_smoke.py"
py -3 "$root\tooling\run_capatch_diagnostics_smoke.py"
py -3 "$root\tooling\run_plugin_contract_smoke.py"
py -3 "$root\tooling\run_rollback_drill.py"
py -3 "$root\tooling\run_qa_benchmark_suite.py"
py -3 "$root\tooling\run_windows_smoke.py"
py -3 "$root\tooling\run_readiness_gate.py"
pytest tests/test_patch_pipeline.py tests/test_commands_patch_hardening.py tests/test_phase2_transaction_journal.py tests/test_phase1_python_verifiers.py tests/test_engine_golden.py
```

## Qué revisar después de cada corrida

### Evidencia operativa
- `reports/patch_runs/`
- `reports/checkpoints/`
- `reports/rollback/`
- `reports/diagnostics/`
- `reports/bundles/`
- `reports/telemetry/`
- `reports/verification/`

### Estado del runtime de plugins
- `capatch_plugins/_plugin_registry.json`
- `capatch_plugins/_plugin_disabled.json`
- `capatch_plugins/_logs/`

### Respaldo y huella operativa
- `.capatch/backups/patches/`

## Comandos útiles de observabilidad

### Mostrar plugins registrados
```powershell
py -3 "$root\capatch.py" --plugin-list
```

### Ver log de un plugin
```powershell
py -3 "$root\capatch.py" --plugin-show-log recommender.safe-fix-plan
```

### Recuperar una transacción de patch
```powershell
py -3 "$root\tooling\recover_patch_transaction.py"
```

## Buenas prácticas

1. usa `--dry-run` como primer movimiento en cambios mutantes
2. revisa la línea `[STRATEGY]` antes de aplicar en serio
3. si el selector cae en `probe-only`, no lo forces a ciegas
4. corre `--plugin-health` después de tocar runtime, policy, verify o tooling
5. usa baselines para marcar estados oficiales y no depender solo del último checkpoint
6. refresca reports cuando quieras evidencia actual y ordenada
7. usa el readiness gate como semáforo final antes de promover o compartir un estado

## Resultado esperado de una rutina sana

Una rutina operativa bien ejecutada deja:

- patch runs legibles
- telemetry fresca
- readiness claro
- baselines comparables
- rollback disponible
- reports útiles para diagnóstico, soporte y auditoría
