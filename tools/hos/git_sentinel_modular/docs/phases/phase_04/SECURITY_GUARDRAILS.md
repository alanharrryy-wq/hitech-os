    # Security guardrails for phase_04

    ## No negociables
    - Ningún cambio de esta fase debe borrar el package legacy.
    - No se habilita apply destructivo durante la fase.
    - Cualquier side effect debe documentar ruta, tipo de escritura y rollback.
    - Las pruebas deben señalar ruta exacta y archivo exacto cuando fallen.

    ## Riesgos propios
    - Mezclar HTML/UI con lógica del reporte.
- Meter dependencias de red en pruebas unitarias.

    ## Gate de salida
    - Reportes salen con schema estable.
- Alerting se puede probar sin red real.
- Visualization no orquesta lógica de negocio.
