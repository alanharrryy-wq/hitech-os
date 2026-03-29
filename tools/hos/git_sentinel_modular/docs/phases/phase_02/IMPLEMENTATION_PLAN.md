    # Implementation plan for phase_02

    ## Secuencia sugerida

    1. Crear contratos o adapters que bajen el acoplamiento.
    2. Mover primero funciones puras y luego wrappers con side effects.
    3. Agregar shim legacy si todavía existe consumo desde el paquete viejo.
    4. Cerrar con pruebas y smoke checks de esta fase.

    ## Archivos objetivo
    - `scanning/repository.py`
- `scanning/artifacts.py`
- `security/scanner.py`
- `security/quality.py`

    ## Definición de terminado
    - Scanner y security ya no dependen del paquete flat legacy excepto vía shims claros.
- Los findings salen con contratos tipados.
- Las pruebas de scan no escriben en el repo.

    ## Riesgos a vigilar
    - Meter side effects de cleanup por accidente en scanner.
- Acoplar security a dashboard o report generator demasiado pronto.
