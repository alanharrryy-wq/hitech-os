# PRISMA_TRI_SURFACE_VISUAL_GUARDIAN_00C_REBASE

Guardian de contrato para el rebase de PRISMA App a `products/mobile/app`.

## Qué corrige

- Conserva los Surface IDs de 00A.
- Declara `products/mobile/app` como raíz canónica de Mobile.
- Separa `reviewedFiles` de `touchedFiles`.
- Bloquea `OMITTED`.
- Exige evidencia por superficie.
- Exige razón fuerte para `EXCLUDED`.
- Mantiene la autonomía de Tablet como invariante.

## Regla clave

`reviewedFiles` no significa cambio. Sólo evidencia validación.

`changedFiles` y `touchedFiles` sí significan impacto real.

No mezclar ambas cosas, porque revisar el changarro no es mover la caja registradora.
