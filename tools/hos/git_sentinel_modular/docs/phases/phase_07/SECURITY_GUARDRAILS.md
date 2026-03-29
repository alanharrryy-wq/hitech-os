# Security guardrails for phase_07

- No instalar nada fuera del scaffold root detectado.
- No ejecutar código de los zips, solo extraer/copiar/validar.
- No sobrescribir fuera del conjunto de rutas del manifest.
- Reportar todo overwrite como archivo instalado en reporte.
- No silenciar checksum mismatch.
