# Runbook rápido

## Arranque GUI
```powershell
python tools/graphviz/repo_analizer/main.py
```

## Arranque CLI
```powershell
python tools/graphviz/repo_analizer/main.py --cli
```

## Recomendación
Mantén `main.py` como fachada estable y mueve cambios internos únicamente dentro de `app/`.

## Self-test dev rápido
```powershell
python tools/graphviz/repo_analizer/dev_self_test.py --repo tools/graphviz/repo_analizer --query plugin --failure-mode off
```

En `failure-mode off`, el self-test ahora valida explícitamente:
- carga de plugins
- attach de plugin docks
- attach de acciones plugin en toolbar
- attach de acciones plugin en menú

Guía extendida:
- `tools/graphviz/repo_analizer/docs/03_operations/DEVELOPER_FAST_PATH.md`

## Failure injection (diagnóstico determinístico)
```powershell
python tools/graphviz/repo_analizer/dev_self_test.py --repo tools/graphviz/repo_analizer --query plugin --failure-mode load
python tools/graphviz/repo_analizer/dev_self_test.py --repo tools/graphviz/repo_analizer --query plugin --failure-mode init
python tools/graphviz/repo_analizer/dev_self_test.py --repo tools/graphviz/repo_analizer --query plugin --failure-mode integration
```

## CI headless PR
- Workflow: `.github/workflows/repo-analyzer-self-test.yml`
- Ejecuta:
  - self-test normal (`off`)
  - matriz determinística (`load`, `init`, `integration`)
