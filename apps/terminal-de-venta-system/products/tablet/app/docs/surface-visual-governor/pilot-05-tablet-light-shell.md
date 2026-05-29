# Pilot 05 · Tablet Light Shell

## Objetivo

Trasladar tokens/variants seguros a Tablet productiva light-first, sin tocar POS todavía.

## Reglas

- Tablet debe ser clara, táctil, luminosa y de alto contraste suave.
- Atmosphere Engine usa assets reales, pero con scrim claro y baja intensidad.
- No dark storm como fondo activo.
- No Pixi vapor.
- No WebGL.
- No blur pesado.
- No POS ni checkout.
- No DB, deploy ni dependencias nuevas.

## Instalado

- `products/tablet/app/app/page.tsx`
- `products/tablet/app/app/prisma-tablet-light-shell.module.css`
- `products/tablet/app/public/surface-visual-governor/tablet-light-shell/pilot-05/*`
- `products/tablet/app/public/surface-visual-governor/tablet-light-shell/latest/*`
- `products/tablet/app/scripts/verify-surface-visual-governor-pilot05.mjs`

## Siguiente paso natural

POS final queda bloqueado hasta que se apruebe el gate `light-only / touch-first / no WebGL / no Pixi vapor / no dark storm / no blur pesado`.
