# Implementation plan for phase_07

1. Descubrir repo y scaffold automáticamente.
2. Cargar phase zips.
3. Validar `phase_manifest.json`.
4. Extraer a carpeta temporal.
5. Copiar docs al scaffold root preservando paths.
6. Correr validaciones y generar reportes JSON/Markdown.
7. Salir con error code distinto de cero si existe cualquier ERROR.

## Reportes
- `sentinel_phase_install_report_*.json`
- `sentinel_phase_install_report_*.md`
