# Live Scene Composer tooling hub

Este directorio concentra el tooling operativo de Live Scene Composer dentro de `tools/live-scene-composer`.

## Layout
- `architecture/` -> generación de artefactos de arquitectura
- `policy/` -> guards y validadores de arquitectura/documentación
- `docs/` -> tooling y fuentes legacy para bootstrap documental
- `_local/` -> evidencia, staging y backups locales

## Entry points
- `generate_architecture_artifacts.py`
- `validate_docs_architecture_guard.py`
- `generate_architecture_artifacts.bat`
- `run_docs_architecture_guard.bat`

## Notas
- Los `.py` en la raíz son shims de compatibilidad que delegan a `architecture/` y `policy/`.
- Los `.sh` se preservan como compatibilidad / referencia legacy, pero la operación recomendada es Python.
