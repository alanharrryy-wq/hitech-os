# MANIFIESTO DE LOTE OLA 6

## Objetivo
Acabado premium del plugin `orchestrator_bridge` para Qt/Windows manteniendo el plugin como bridge-only async runner hacia `one_button.ps1`.

## Archivos nuevos/modificados
### Modificados
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/plugin.py`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/plugin.json`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/README.md`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/tests/test_plugin_package_integration.py`

### Nuevos
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/PREMIUM_UI_DESIGN_NOTES_OLA6.md`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/CHECKLIST_VISUAL_MANUAL_OLA6.md`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/MANIFIESTO_DE_LOTE_OLA6.md`

## Archivos incluidos
- `tools/_local/orchestrator_bridge/.gitkeep`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/CHECKLIST_FINAL_OLA5.md`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/CHECKLIST_VISUAL_MANUAL_OLA6.md`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/OPERATOR_CODEX_INTEGRATION_GUIDE.md`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/PREMIUM_UI_DESIGN_NOTES_OLA6.md`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/README.md`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/__init__.py`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/bridge_config.json`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/plugin.json`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/plugin.py`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/tests/__init__.py`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/tests/fixtures/blocked_lock_stderr.txt`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/tests/fixtures/contracts_fail_stdout.txt`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/tests/fixtures/reused_stdout.txt`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/tests/fixtures/runtime_error_stderr.txt`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/tests/fixtures/success_stdout.txt`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/tests/test_exit_mapping.py`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/tests/test_output_parser.py`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/tests/test_plugin_package_integration.py`
- `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge/tests/test_validation_and_config.py`

## Comandos de validación
```powershell
$zip = 'F:\OneDrive\Descargas\lote_plugin_ola6_premium_ui_motion.zip'
$dest = 'F:\OneDrive\Descargas\lote_plugin_ola6_premium_ui_motion_unpacked'
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Expand-Archive -Path $zip -DestinationPath $dest -Force
Get-ChildItem -Recurse $dest
python -m py_compile "$dest\tools\graphviz\repo_analizer\app\gui_qt\plugins\orchestrator_bridge\plugin.py"
python -m unittest discover -s "$dest\tools\graphviz\repo_analizer\app\gui_qt\plugins\orchestrator_bridge\tests" -p "test_*.py" -v
Select-String -Path "$dest\tools\graphviz\repo_analizer\app\gui_qt\plugins\orchestrator_bridge\plugin.py" -Pattern 'THEME_TOKENS|STATE_VISUALS|QProgressBar|Execution Timeline|Run Bridge|_on_pulse_tick|_flash_feedback|bridgeStatusChip'
```

## Resultado esperado
- El ZIP conserva rutas relativas desde `F:\repos\hitech-os\`.
- El plugin sigue cargando como package estándar del host con `module = "plugin"` y `class_name = "PluginImplementation"`.
- `plugin.py` mantiene runner async con `QProcess`, parseo existente, persistencia mínima y guardrails.
- El dock ahora muestra sistema visual premium, status chip semántico, timeline de ejecución, panel de resultado refinado y feedback visual corto.
- No hay dependencias nuevas ni lógica de motor reimplementada en el plugin.
- La suite de pruebas sigue pasando.

## Checklist visual manual
- Dock abre desde menú y toolbar.
- Status chip cambia entre idle/ready/running/success/reused/blocked/failed con contraste alto.
- Barra de progreso visible sólo durante ejecución.
- El formulario se deshabilita durante run para evitar double-run.
- Timeline y raw logs reciben información durante el proceso.
- El panel de resultado habilita acciones rápidas según disponibilidad real del ZIP.
- El dock conserva legibilidad al redimensionar.
- Los mensajes de feedback son breves, claros y no intrusivos.
