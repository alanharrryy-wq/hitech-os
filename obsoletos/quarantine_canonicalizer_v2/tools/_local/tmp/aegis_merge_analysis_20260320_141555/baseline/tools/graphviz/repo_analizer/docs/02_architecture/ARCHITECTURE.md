# Arquitectura

## Diseño de carpetas
- `main.py`: único archivo ejecutable en la raíz.
- `app/config.py`: constantes y parámetros.
- `app/models.py`: dataclasses compartidas.
- `app/helpers.py`: funciones reutilizables.
- `app/gui/app_gui.py`: GUI principal heredada del monolito.
- `app/cli/cli_mode.py`: fallback CLI.
- `docs/`: documentación ordenada por tema.
- `_source_backup/`: copia del archivo original.

## Decisión clave
Esta fase no reescribe toda la lógica. Solo redistribuye piezas para:
- reducir ruido en la raíz
- dejar punto de entrada claro
- preparar refactors futuros por paneles y servicios

## Fase siguiente sugerida
Partir `app/gui/app_gui.py` en:
- `tree_panel.py`
- `preview_panel.py`
- `results_panel.py`
- `imports_panel.py`
- `services/settings_service.py`
- `services/bookmarks_service.py`
- `services/export_service.py`
