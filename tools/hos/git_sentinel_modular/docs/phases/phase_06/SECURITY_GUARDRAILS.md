    # Security guardrails for phase_06

    ## No negociables
    - Ningún cambio de esta fase debe borrar el package legacy.
    - No se habilita apply destructivo durante la fase.
    - Cualquier side effect debe documentar ruta, tipo de escritura y rollback.
    - Las pruebas deben señalar ruta exacta y archivo exacto cuando fallen.

    ## Riesgos propios
    - Rewirear imports demasiado pronto.
- Mover dashboard antes de congelar contratos.

    ## Gate de salida
    - Scan-only parity funcionando.
- CLI modular y dashboard modular pasan smoke tests.
- Compat shims documentados y reversibles.
