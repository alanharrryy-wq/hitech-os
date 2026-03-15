    # Security guardrails for phase_05

    ## No negociables
    - Ningún cambio de esta fase debe borrar el package legacy.
    - No se habilita apply destructivo durante la fase.
    - Cualquier side effect debe documentar ruta, tipo de escritura y rollback.
    - Las pruebas deben señalar ruta exacta y archivo exacto cuando fallen.

    ## Riesgos propios
    - Romper seguridad con defaults agresivos.
- Confundir dry-run con apply real.

    ## Gate de salida
    - Todos los paths destructivos tienen constraints documentados y probados.
- Scheduler nunca aplica cleanup/repair por default.
- Riesky actions bloqueadas y reportadas con exactitud.
