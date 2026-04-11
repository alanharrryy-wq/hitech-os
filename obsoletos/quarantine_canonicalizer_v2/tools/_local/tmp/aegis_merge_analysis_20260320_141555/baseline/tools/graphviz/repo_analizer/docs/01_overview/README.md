# Repo Analyzer Modularizado

Esta salida fue generada por `modularize_repo_analyzer_root_clean.py`.

## Objetivo
Dejar la carpeta principal limpia y que solo viva ahí el **launcher** (`main.py`).

## Fuente original
- Archivo origen: `tools/graphviz/repo_analyzer.py`
- Respaldo conservado en: `_source_backup/repo_analyzer.original.py`

## Regla de acomodo
- **Raíz**: solo `main.py`
- **Código interno**: `app/`
- **Documentación**: `docs/`
- **Respaldo**: `_source_backup/`

## Cómo arrancar
```powershell
python tools/graphviz/repo_analizer/main.py
```

## Modo CLI
```powershell
python tools/graphviz/repo_analizer/main.py --cli
```
