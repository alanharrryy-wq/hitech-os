    # phase_03: Learning and analysis

    ## Objetivo
    - Mover memoria histórica y scoring sin contaminar el core.
- Encapsular SQLite y rutas de estado bajo límites claros.
- Separar heurísticas/predicción de scheduler y dashboard.

    ## Dependencias
    - phase_01
- phase_02

    ## Targets directos
    - `learning/engine.py`
- `analysis/prediction.py`

    ## Dominios tocados
    - `learning`
- `analysis`
- `tests/learning`
- `tests/analysis`
- `docs/phases/phase_03`

    ## Regla de seguridad
    - No tocar el package vivo `tools/hos/git_sentinel` como parte del primer pase.
    - No cambiar imports de producción hasta que esta fase pase sus criterios.
    - Todo cambio debe ser reversible y quedar documentado.

    ## Nota
    Esta fase te dice si Sentinel piensa con cabeza propia o si solo es una libreta glorificada.
