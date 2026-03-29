# Guia de integracion Operator / Codex

## Instalar y activar plugin
1. Descomprime el lote respetando rutas relativas desde `F:\repos\hitech-os\`.
2. Verifica que exista el package:
   - `tools/graphviz/repo_analizer/app/gui_qt/plugins/orchestrator_bridge`
3. Abre el host `repo_analizer`.
4. En el plugin manager confirma que `orchestrator_bridge` este habilitado.
5. Si el host cachea manifests, reinicia el host una vez.

## Ejecutar una sesion desde la GUI
1. Abre el dock desde toolbar o menu `Tools > Orchestrator Bridge`.
2. Verifica que el estado diga `Ready`.
3. Configura:
   - `mode`: `existing` o `new`
   - `policy`
   - `project_id`
   - `intent`
   - `dry-run`
   - `non-interactive`
4. Presiona `Run`.
5. Observa logs en vivo y el panel de resultado.
6. Si se produce ZIP valido, usa:
   - `Copy ZIP Path`
   - `Open ZIP`
   - `Open Folder`
7. Para repetir la misma solicitud, usa `Rerun Last`.

## Que entregar a Codex despues
Entrega el ZIP generado por el motor externo, idealmente el path canonico reportado por `OB_ZIP|...`.
Acompanalo con:
- `mode`
- `policy`
- `project_id`
- `intent`
- estado final visible en UI
- extracto corto de warnings o errores si existieron

## Troubleshooting breve
- **Estado Blocked al abrir**: revisa `bridge_config.json` y que `one_button_path` siga bajo `tools\orchestrator_factory`.
- **Run deshabilitado**: corrige config, runtime root o el script faltante.
- **Sin ZIP publicable**: revisa si el motor emitio `OB_ZIP|...` con ruta permitida y si el archivo existe.
- **Malformed contract**: usa el detalle en logs para corregir la salida del motor, no el plugin.
- **Host sin dock visible**: valida que el plugin manager haya cargado `plugin.json`, `module = "plugin"`, y `class_name = "PluginImplementation"`.
