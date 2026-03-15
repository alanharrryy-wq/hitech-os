    # Implementation plan for phase_05

    ## Secuencia sugerida

    1. Crear contratos o adapters que bajen el acoplamiento.
    2. Mover primero funciones puras y luego wrappers con side effects.
    3. Agregar shim legacy si todavía existe consumo desde el paquete viejo.
    4. Cerrar con pruebas y smoke checks de esta fase.

    ## Archivos objetivo
    - `remediation/cleanup.py`
- `remediation/repair.py`
- `operations/execution_lock.py`
- `operations/ci_gate.py`
- `operations/scheduler.py`

    ## Definición de terminado
    - Todos los paths destructivos tienen constraints documentados y probados.
- Scheduler nunca aplica cleanup/repair por default.
- Riesky actions bloqueadas y reportadas con exactitud.

    ## Riesgos a vigilar
    - Romper seguridad con defaults agresivos.
- Confundir dry-run con apply real.
