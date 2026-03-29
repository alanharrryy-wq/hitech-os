    # phase_04: Reporting and visualization

    ## Objetivo
    - Formalizar outputs serializados y alertas.
- Separar generación de reportes de dashboard y core.
- Dejar snapshots y schemas listos para regression testing.

    ## Dependencias
    - phase_01
- phase_02
- phase_03

    ## Targets directos
    - `reporting/alerting.py`
- `reporting/generator.py`
- `app/visualization.py`

    ## Dominios tocados
    - `reporting`
- `app`
- `tests/reporting`
- `docs/phases/phase_04`

    ## Regla de seguridad
    - No tocar el package vivo `tools/hos/git_sentinel` como parte del primer pase.
    - No cambiar imports de producción hasta que esta fase pase sus criterios.
    - Todo cambio debe ser reversible y quedar documentado.

    ## Nota
    Aquí conviertes datos en narrativa operativa. Si esto queda bien, el dashboard ya no tiene que improvisar.
