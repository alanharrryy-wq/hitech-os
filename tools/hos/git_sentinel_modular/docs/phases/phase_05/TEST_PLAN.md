    # Test plan for phase_05

    ## Pruebas mínimas
    - Dry-run cleanup no mueve ni borra nada.
- Quarantine path confinement.
- Repair plan bloquea riskyActions.
- Locking evita doble ejecución concurrente.

    ## Smoke check de fase
    - Verificar que existen todos los targets documentados.
    - Verificar que no se introducen rutas fuera de `tools/hos/git_sentinel_modular`.
    - Verificar que los docs referencian únicamente módulos existentes o explícitamente planificados.
    - Verificar que los markdown links internos no están rotos.
