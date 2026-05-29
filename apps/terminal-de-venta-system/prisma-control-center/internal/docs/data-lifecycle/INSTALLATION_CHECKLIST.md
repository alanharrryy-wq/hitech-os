# INSTALLATION CHECKLIST V5

## Antes

- ZIP en `<OUTPUT_DIR>`.
- Control Center cerrado si está corriendo.
- Repo en `<REPO_ROOT>\apps\terminal-de-venta-system`.
- No ejecutar en cliente live sin respaldo externo.
- Revisar README.

## Durante

- Detecta Control Center.
- Valida payload completo.
- Compila API antes de copiar.
- Hace backup de archivos tocados.
- Copia payload.
- Parchea panel e index de forma idempotente.
- Verifica instalación.
- Genera ZIP de resultado.

## Después

- Abrir Control Center.
- Ir a `PRISMA Data Lifecycle`.
- Probar `/api/lifecycle/health`.
- Probar `/api/lifecycle/release/evidence`.
- Probar dry-run antes de inyectar.
- No usar Clear hasta revisar PIN y backup.

## Rollback

Si algo falla, el instalador restaura automáticamente archivos respaldados y deja ZIP `_FAILED`.
