    # phase_06: Core and app integration

    ## Objetivo
    - Rearmar la columna vertebral usando módulos ya extraídos.
- Partir dashboard monolítico por responsabilidades.
- Crear compatibilidad gradual con shims legacy antes del cutover.

    ## Dependencias
    - phase_01
- phase_02
- phase_03
- phase_04
- phase_05

    ## Targets directos
    - `core/orchestrator.py`
- `app/cli.py`
- `app/dashboard.py`
- `legacy/`

    ## Dominios tocados
    - `core`
- `app`
- `legacy`
- `tests/integration`
- `docs/phases/phase_06`

    ## Regla de seguridad
    - No tocar el package vivo `tools/hos/git_sentinel` como parte del primer pase.
    - No cambiar imports de producción hasta que esta fase pase sus criterios.
    - Todo cambio debe ser reversible y quedar documentado.

    ## Nota
    Esta fase es cirugía de tórax abierto. Se hace al final porque aquí ya todo depende de todo.
