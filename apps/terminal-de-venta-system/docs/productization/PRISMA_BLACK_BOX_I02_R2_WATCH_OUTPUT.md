# PRISMA black-box i02 R2 - Watch output discipline

## Objetivo

Mover black-box a `F:\Black-box` como salida principal y evitar que `watch` genere reportes completos cada ciclo.

## Cambios

- Default output root: `F:\Black-box`.
- `watch` escribe heartbeat compacto en `black_box_heartbeat.jsonl`.
- `watch` solo genera reporte completo si cambia la firma del estado, aparece `BLOCKED`, hay fallas activas, se usa `--emit-report`, o se cumple `--report-every`.
- Corrige el `SyntaxWarning` de Python 3.13 por `F:\descargasf` en help text.
- Agrega `cleanup reports` para limpiar reportes viejos de black-box.

## Seguridad

- No toca Tablet, PC, Mobile, DB, schema, shared-kernel ni contratos.
- Solo modifica `tools/black-box/black_box.py`, README de black-box y este documento.
- Backup automático antes de sobreescribir.
