# Runbook rápido

## Arranque GUI
```powershell
python F:\repos\hitech-os\tools\graphviz\repo_analizer\main.py
```

## Arranque CLI
```powershell
python F:\repos\hitech-os\tools\graphviz\repo_analizer\main.py --cli
```

## Recomendación
Mantén `main.py` como fachada estable y mueve cambios internos únicamente dentro de `app/`.
