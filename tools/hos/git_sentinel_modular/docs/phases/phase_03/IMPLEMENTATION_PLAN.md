    # Implementation plan for phase_03

    ## Secuencia sugerida

    1. Crear contratos o adapters que bajen el acoplamiento.
    2. Mover primero funciones puras y luego wrappers con side effects.
    3. Agregar shim legacy si todavía existe consumo desde el paquete viejo.
    4. Cerrar con pruebas y smoke checks de esta fase.

    ## Archivos objetivo
    - `learning/engine.py`
- `analysis/prediction.py`

    ## Definición de terminado
    - Learning engine corre con DB temporal controlada.
- Prediction consume contracts y no payloads informales.
- No se escribe fuera de rutas de runtime o temp definidas.

    ## Riesgos a vigilar
    - Anclar lógica de aprendizaje a paths absolutos del entorno viejo.
- Hacer predicción no determinística y romper pruebas.
