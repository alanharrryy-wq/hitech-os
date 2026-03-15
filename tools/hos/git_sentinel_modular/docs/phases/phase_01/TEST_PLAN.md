    # Test plan for phase_01

    ## Pruebas mínimas
    - Parsing de config en fixtures válidos e inválidos.
- Roundtrip de payloads compartidos a JSON estable.
- Git helpers en modo dry-run y lectura solamente.
- False positives con persistencia y lectura determinística.

    ## Smoke check de fase
    - Verificar que existen todos los targets documentados.
    - Verificar que no se introducen rutas fuera de `tools/hos/git_sentinel_modular`.
    - Verificar que los docs referencian únicamente módulos existentes o explícitamente planificados.
    - Verificar que los markdown links internos no están rotos.
