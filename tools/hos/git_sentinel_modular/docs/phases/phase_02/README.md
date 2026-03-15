    # phase_02: Scanning and security

    ## Objetivo
    - Separar observación del repo y detección de artefactos.
- Aislar seguridad y quality eval de la orquestación.
- Forzar outputs determinísticos amarrados a contratos de la fase 1.

    ## Dependencias
    - phase_01

    ## Targets directos
    - `scanning/repository.py`
- `scanning/artifacts.py`
- `security/scanner.py`
- `security/quality.py`

    ## Dominios tocados
    - `scanning`
- `security`
- `tests/scanning`
- `tests/security`
- `docs/phases/phase_02`

    ## Regla de seguridad
    - No tocar el package vivo `tools/hos/git_sentinel` como parte del primer pase.
    - No cambiar imports de producción hasta que esta fase pase sus criterios.
    - Todo cambio debe ser reversible y quedar documentado.

    ## Nota
    Aquí nace el observability layer real de Sentinel. Debe quedar bien seco y predecible.
