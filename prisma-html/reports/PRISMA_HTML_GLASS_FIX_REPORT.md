# PRISMA HTML / Atlas · Glass Fix Report

## Estado

`PASS_SOURCE_AND_INLINE_CHROMIUM_HARNESS`

## Reparaciones aplicadas

- Transparencia honesta al 0% para chrome y contenido gobernado.
- Owners canónicos para contenido estructural, overlays, cards y controles.
- 11 grupos de selectores duplicados consolidados en `index.css`.
- Dropdown accesible: Enter abre una sola vez y conserva `aria-expanded=true`.
- Contención responsive con `minmax(0, 1fr)` y swatches móviles sin overflow.
- Muestras deliberadas de opacidad separadas de los owners de material.
- Evidencia, árbol, continuación y manifiestos regenerados.

## Validación

- Source validator: **PASS**, 379 checks, 0 warnings, 0 errors.
- Atlas validator: **PASS**, 27 páginas, 26 secciones, 418 elementos, 0 issues.
- Chromium inline harness: **PASS**, 27 páginas.
- Owners inspeccionados en 0%: **1353**, fallas: **0**.
- Overflow desktop/móvil: **0 fallas**.
- Errores de consola/página: **0**.
- Dropdown por teclado: **PASS**.

## Límite honesto

La evidencia certifica el snapshot standalone suministrado dentro de Chromium con assets locales inyectados. La navegación directa por URL fue bloqueada por política del sandbox. No se certifica deploy, servidor local ni runtime de `hitech-os`.
