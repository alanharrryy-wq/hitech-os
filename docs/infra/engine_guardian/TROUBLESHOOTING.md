# Troubleshooting de Engine Guardian v3

## Si `validate` falla con preflight degradado
Revisa:
- `state\resolved_tools.json`
- `reports\preflight_latest.json`
- presencia de `tools\infra\cloudflare\ensure_origin.py`
- presencia de `tools\infra\cloudflare\ensure_service.py`
- presencia de `tools\infra\cloudflare\validate_tunnel.py`
- presencia de `tools\graphviz\repo_analizer\main.py`
- presencia de `tools\graphviz\repo_analizer\dev_self_test.py`

## Si el público falla pero origin+túnel salen bien
Eso es drift de capa pública.
Engine Guardian marca escalación y deja snapshot explícito.

## Si el scheduler no se instala
- corre `python engine_guardian\cli.py install-scheduler --dry-run`
- revisa XML en `F:\OneDrive\Descargas\engine_guardian\install`
- confirma que la máquina tenga módulo `ScheduledTasks`
- para instalación real de tareas `SYSTEM`, ejecuta la terminal con elevación (Administrador)
- si `install-scheduler` devuelve código de salida distinto de `0`, revisa `reports\scheduler_install_latest.json` para el detalle exacto

## Si Repo Analyzer no abre
- ejecuta `validate_repo_analyzer.cmd`
- revisa `repo_analyzer_status.json`
- revisa `repo_analyzer_guardian.log`
