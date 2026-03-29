    # Implementation plan for phase_01

    ## Secuencia sugerida

    1. Crear contratos o adapters que bajen el acoplamiento.
    2. Mover primero funciones puras y luego wrappers con side effects.
    3. Agregar shim legacy si todavía existe consumo desde el paquete viejo.
    4. Cerrar con pruebas y smoke checks de esta fase.

    ## Archivos objetivo
    - `shared/config.py`
- `shared/git.py`
- `shared/utils.py`
- `shared/telemetry.py`
- `shared/false_positives.py`
- `shared/ignore_rules.py`
- `shared/retention.py`
- `shared/contracts.py`
- `shared/types.py`
- `shared/errors.py`
- `shared/interfaces.py`

    ## Definición de terminado
    - Existe capa shared con contratos explícitos y naming estable.
- No hay cambio de imports en el package vivo.
- Los contratos cubren scan result, artifact finding, security finding, prediction, repair plan y cleanup plan.
- Hay tests de contrato y serialización base.

    ## Riesgos a vigilar
    - Convertir demasiado pronto helpers en side-effect code.
- Dejar contratos ambiguos y regresar a dict[str, Any].
