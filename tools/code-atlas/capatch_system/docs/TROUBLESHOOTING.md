# CAPATCH Troubleshooting

Guía rápida para interpretar señales operativas del workspace con calma y criterio. La idea es distinguir estados esperados, señales informativas y pasos útiles para seguir operando con fluidez.

## 1. `capatch.py` avisa que opera como shim
**Qué significa**
- Es esperado.
- `capatch.py` sigue siendo la entrada estable.
- El CLI real vive en `capatch_cli.main`.

**Qué hacer**
- Continúa usando `capatch.py` como punto de entrada diario.

## 2. `--rollback-last` devuelve `no_checkpoints`
**Qué significa**
- El workspace o el target todavía no tienen checkpoints previos para restaurar.
- Es una señal válida y limpia en workspaces nuevos o en targets recién intervenidos.

**Qué hacer**
- Ejecuta una corrida que genere checkpoint.
- Luego vuelve a consultar preview o apply de rollback.

## 3. `run_windows_smoke.py` regresa `degraded`
**Qué significa**
- El contrato de Windows smoke admite `degraded` cuando el contexto real no justifica `passed` pleno pero el sistema sigue operando de forma útil y controlada.

**Qué revisar**
- `reports/telemetry/windows_smoke.json`
- `tooling/run_windows_smoke.py`
- `tests/test_windows_smoke_contract.py`

## 4. `plugin-health` marca plugins rechazados
**Qué significa**
- El runtime está siendo estricto con contracts, capabilities o versión mínima requerida.
- El plugin puede estar presente como archivo y, aun así, no ser aceptado operativamente.

**Qué revisar**
- runtime activo
- `PLUGIN_MIN_RUNTIME`
- `capatch_plugins/_plugin_registry.json`
- `capatch_contracts/plugin_runtime.py`

## 5. `plugin-health` y `run_plugin_contract_smoke.py` muestran señales distintas
**Qué significa**
- Estás viendo dos lentes diferentes del sistema:
  - salud operativa del runtime
  - validación contractual del ecosistema de plugins

**Qué revisar**
- entorno cargado durante cada corrida
- capabilities presentes
- registry efectivo y reportes asociados

## 6. El readiness gate marca `degraded` o `blocked`
**Qué significa**
- El readiness gate está consolidando señales reales del workspace para ayudarte a decidir promoción.

**Qué revisar**
- `reports/telemetry/`
- `reports/patch_runs/`
- `reports/verification/`
- `reports/rollback/`
- `tooling/run_readiness_gate.py`

**Qué hacer**
- refresca reports
- corre smokes clave
- valida plugin health
- confirma que baseline y evidence estén al día

## 7. `manage_baselines.py` no encuentra la baseline esperada
**Qué significa**
- La baseline aún no ha sido promovida, o se está buscando con otra etiqueta.

**Qué hacer**
```powershell
py -3 "$root\tooling\manage_baselines.py" --list
```
- confirma el nombre correcto
- promueve una baseline nueva si el estado actual ya es oficial

## 8. `refresh_workspace_reports.py` genera artifacts nuevos
**Qué significa**
- Es el comportamiento esperado.
- El objetivo del refresh es dejar evidencia vigente, ordenada y fácil de consultar.

**Qué revisar**
- `reports/telemetry/`
- `reports/patch_runs/`
- timestamps y metadata de los artifacts regenerados

## 9. El consolidado resume-aware salta rondas anteriores
**Qué significa**
- Buen síntoma.
- El consolidador está reconociendo trabajo ya integrado y evita reinyectar rondas cerradas.

**Qué hacer**
- usa `capatch_master_consolidation_v2.py` como camino recomendado para revalidación

## 10. Validación mínima para recuperar visibilidad rápida
```powershell
$root = "F:\repos\hitech-os\apps\code-atlas\capatch_system"
py -3 "$root\capatch.py" --plugin-health
py -3 "$root\capatch.py" --smoke-test
py -3 "$root\tooling\run_phase0_ac_smoke.py"
py -3 "$root\tooling\run_capatch_diagnostics_smoke.py"
py -3 "$root\tooling\run_readiness_gate.py"
```

## 11. Señales bonitas que vale la pena buscar

Una corrida sana normalmente deja varias de estas señales:

- `plugin-health` claro
- `smoke-test` verde o `degraded` justificado
- readiness gate promocionable o legible
- patch runs con metadata completa
- telemetry reciente
- baselines visibles y comparables
- rollback disponible cuando aplica

## 12. Regla práctica

Si necesitas un resumen rápido del estado del workspace, piensa así:

1. **health** con `--plugin-health`
2. **smoke** con `--smoke-test`
3. **readiness** con `run_readiness_gate.py`
4. **evidence** en `reports/`
5. **baseline** con `manage_baselines.py`

Con esa secuencia, casi siempre recuperas contexto útil en minutos.
