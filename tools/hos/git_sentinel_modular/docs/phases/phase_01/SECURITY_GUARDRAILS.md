    # Security guardrails for phase_01

    ## No negociables
    - Ningún cambio de esta fase debe borrar el package legacy.
    - No se habilita apply destructivo durante la fase.
    - Cualquier side effect debe documentar ruta, tipo de escritura y rollback.
    - Las pruebas deben señalar ruta exacta y archivo exacto cuando fallen.

    ## Riesgos propios
    - Convertir demasiado pronto helpers en side-effect code.
- Dejar contratos ambiguos y regresar a dict[str, Any].

    ## Gate de salida
    - Existe capa shared con contratos explícitos y naming estable.
- No hay cambio de imports en el package vivo.
- Los contratos cubren scan result, artifact finding, security finding, prediction, repair plan y cleanup plan.
- Hay tests de contrato y serialización base.
