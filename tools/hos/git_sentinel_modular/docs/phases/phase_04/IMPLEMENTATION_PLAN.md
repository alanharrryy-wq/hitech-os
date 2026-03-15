    # Implementation plan for phase_04

    ## Secuencia sugerida

    1. Crear contratos o adapters que bajen el acoplamiento.
    2. Mover primero funciones puras y luego wrappers con side effects.
    3. Agregar shim legacy si todavía existe consumo desde el paquete viejo.
    4. Cerrar con pruebas y smoke checks de esta fase.

    ## Archivos objetivo
    - `reporting/alerting.py`
- `reporting/generator.py`
- `app/visualization.py`

    ## Definición de terminado
    - Reportes salen con schema estable.
- Alerting se puede probar sin red real.
- Visualization no orquesta lógica de negocio.

    ## Riesgos a vigilar
    - Mezclar HTML/UI con lógica del reporte.
- Meter dependencias de red en pruebas unitarias.
