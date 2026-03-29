    # phase_05: Remediation and operations

    ## Objetivo
    - Mover colmillos a un corral con doble cerca.
- Mantener cleanup/repair siempre opt-in y con quarantine primero.
- Separar runtime operations de lógica de dominio.

    ## Dependencias
    - phase_01
- phase_02
- phase_03
- phase_04

    ## Targets directos
    - `remediation/cleanup.py`
- `remediation/repair.py`
- `operations/execution_lock.py`
- `operations/ci_gate.py`
- `operations/scheduler.py`

    ## Dominios tocados
    - `remediation`
- `operations`
- `tests/remediation`
- `tests/operations`
- `docs/phases/phase_05`

    ## Regla de seguridad
    - No tocar el package vivo `tools/hos/git_sentinel` como parte del primer pase.
    - No cambiar imports de producción hasta que esta fase pase sus criterios.
    - Todo cambio debe ser reversible y quedar documentado.

    ## Nota
    Aquí es donde un sistema serio se separa de una ruleta rusa con dashboard bonito.
