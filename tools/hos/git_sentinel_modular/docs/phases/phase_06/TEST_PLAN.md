    # Test plan for phase_06

    ## Pruebas mínimas
    - CLI smoke en scan-only.
- Dashboard smoke con markers base.
- Integration tests con mocks de remediation disabled.
- Import graph sin ciclos nuevos de alto riesgo.

    ## Smoke check de fase
    - Verificar que existen todos los targets documentados.
    - Verificar que no se introducen rutas fuera de `tools/hos/git_sentinel_modular`.
    - Verificar que los docs referencian únicamente módulos existentes o explícitamente planificados.
    - Verificar que los markdown links internos no están rotos.
