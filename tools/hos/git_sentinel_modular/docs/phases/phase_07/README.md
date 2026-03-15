# phase_07: Installer, validation and exact error reporting

## Objetivo
- Instalar todos los zips de fases en su lugar correcto dentro del scaffold.
- Verificar integridad por manifest y checksum.
- Reportar puntualmente ruta, fase y mensaje cuando exista un error.

## Entregable especial
- `apply_sentinel_phase_docs.py`

## Uso esperado
```powershell
python F:\OneDrive\Descargas\apply_sentinel_phase_docs.py F:\OneDrive\Descargas\sentinel_phase_01_shared_foundation.zip F:\OneDrive\Descargas\sentinel_phase_02_scanning_security.zip
```

## Qué valida
- manifest por fase
- checksums de archivos
- rutas seguras dentro del scaffold
- markdown links internos
- carpetas objetivo esperadas
