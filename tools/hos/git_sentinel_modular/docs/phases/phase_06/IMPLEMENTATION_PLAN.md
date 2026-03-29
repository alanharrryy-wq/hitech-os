    # Implementation plan for phase_06

    ## Secuencia sugerida

    1. Crear contratos o adapters que bajen el acoplamiento.
    2. Mover primero funciones puras y luego wrappers con side effects.
    3. Agregar shim legacy si todavía existe consumo desde el paquete viejo.
    4. Cerrar con pruebas y smoke checks de esta fase.

    ## Archivos objetivo
    - `core/orchestrator.py`
- `app/cli.py`
- `app/dashboard.py`
- `legacy/`

    ## Definición de terminado
    - Scan-only parity funcionando.
- CLI modular y dashboard modular pasan smoke tests.
- Compat shims documentados y reversibles.

    ## Riesgos a vigilar
    - Rewirear imports demasiado pronto.
- Mover dashboard antes de congelar contratos.
