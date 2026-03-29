    # phase_01: Shared foundation and contracts

    ## Objetivo
    - Estabilizar el idioma interno del sistema antes de mover lógica pesada.
- Definir contratos tipados para findings, reportes y planes de acción.
- Extraer helpers compartidos sin rewirear todavía imports del runtime vivo.

    ## Dependencias
    - none

    ## Targets directos
    - `shared/config.py`
- `shared/git.py`
- `shared/utils.py`
- `shared/telemetry.py`
- `shared/false_positives.py`
- `shared/ignore_rules.py`
- `shared/retention.py`
- `shared/contracts.py`
- `shared/types.py`
- `shared/errors.py`
- `shared/interfaces.py`

    ## Dominios tocados
    - `shared`
- `tests/contracts`
- `docs/phases/phase_01`

    ## Regla de seguridad
    - No tocar el package vivo `tools/hos/git_sentinel` como parte del primer pase.
    - No cambiar imports de producción hasta que esta fase pase sus criterios.
    - Todo cambio debe ser reversible y quedar documentado.

    ## Nota
    Esta fase es la bisagra de seguridad. Si aquí queda flojo, todo lo demás se vuelve espagueti con esteroides.
