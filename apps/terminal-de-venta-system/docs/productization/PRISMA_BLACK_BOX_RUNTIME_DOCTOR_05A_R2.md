# PRISMA BLACK-BOX Runtime Doctor 05A R2

## Objetivo
Diagnosticar runtime local de Tablet, PC y Mobile con reportes legibles, timeline JSONL, evidencia ZIP y reparaciones seguras.

## Cambio clave de R2
- No escanea sus propios eventos/reports como errores activos.
- Separa `active_error_hits` de `resolved_error_hits`.
- Si un `prisma_*_dev_preflight_last.log` termina en `PRISMA DEV PREFLIGHT 00G OK`, los errores intermedios no bloquean.
- Agrega probes HTTP de endpoints.
- El patron de bridge faltante ahora exige texto real de `not found`, no solo una ruta en stack trace.

## Comandos
- `status`
- `doctor`
- `last-error`
- `collect`
- `repair plan`
- `repair apply --safe`
- `repair rollback`
- `self-test`
