# PRISMA black-box i02 R3 - Log scope and freshness filter

## Objetivo

Evitar falsos `BLOCKED` causados por logs viejos, externos o no pertenecientes a Terminal de Venta / PRISMA runtime.

## Problema corregido

black-box i02 R2 leía `F:\repos\hitech-os\tools\_local\logs` demasiado ancho. Eso levantó errores viejos de `eit-*`, puertos externos `3100/3200` y builds de abril como si fueran fallas activas del runtime actual. La tienda estaba abierta, pero el guardia estaba gritando por un pleito del vecino.

## Cambios

- `candidate_logs()` ahora filtra por alcance PRISMA/Terminal de Venta.
- Los logs parent del monorepo solo se aceptan si su nombre pertenece a Tablet, PC, Mobile, terminal runtime, Prisma runtime o black-box.
- Se excluyen por default logs `eit-*` y logs de áreas externas.
- Se ignoran logs antiguos por frescura, default 24 horas.
- `classify_log()` baja a `EXTERNAL_WARN` errores de puertos no canónicos si se cuelan.
- `summarize()` solo considera como activos los hits `FAIL` reales; `EXTERNAL_WARN` y `STALE_WARN` van a caveats.
- `build_report()` muestra external/stale hits separados.

## Puertos canónicos

- Tablet: 3120
- PC: 3130
- Mobile: 3140

## Seguridad

- No toca Tablet, PC, Mobile, DB, schema, shared-kernel ni contratos.
- Solo modifica `tools/black-box/black_box.py`, README y este documento.
- Backup automático antes de sobreescribir.
