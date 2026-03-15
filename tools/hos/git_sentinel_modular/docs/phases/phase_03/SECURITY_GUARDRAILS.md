    # Security guardrails for phase_03

    ## No negociables
    - Ningún cambio de esta fase debe borrar el package legacy.
    - No se habilita apply destructivo durante la fase.
    - Cualquier side effect debe documentar ruta, tipo de escritura y rollback.
    - Las pruebas deben señalar ruta exacta y archivo exacto cuando fallen.

    ## Riesgos propios
    - Anclar lógica de aprendizaje a paths absolutos del entorno viejo.
- Hacer predicción no determinística y romper pruebas.

    ## Gate de salida
    - Learning engine corre con DB temporal controlada.
- Prediction consume contracts y no payloads informales.
- No se escribe fuera de rutas de runtime o temp definidas.
