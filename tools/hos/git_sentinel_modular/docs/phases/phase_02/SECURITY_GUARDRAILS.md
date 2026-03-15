    # Security guardrails for phase_02

    ## No negociables
    - Ningún cambio de esta fase debe borrar el package legacy.
    - No se habilita apply destructivo durante la fase.
    - Cualquier side effect debe documentar ruta, tipo de escritura y rollback.
    - Las pruebas deben señalar ruta exacta y archivo exacto cuando fallen.

    ## Riesgos propios
    - Meter side effects de cleanup por accidente en scanner.
- Acoplar security a dashboard o report generator demasiado pronto.

    ## Gate de salida
    - Scanner y security ya no dependen del paquete flat legacy excepto vía shims claros.
- Los findings salen con contratos tipados.
- Las pruebas de scan no escriben en el repo.
