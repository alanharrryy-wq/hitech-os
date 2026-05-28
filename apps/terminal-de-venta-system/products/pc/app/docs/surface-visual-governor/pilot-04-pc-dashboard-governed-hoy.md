# Pilot 04 · PC Dashboard Governed Hoy

## Objetivo

Aplicar Materiality Catalog + Atmosphere Engine de forma gobernada a `PC /dashboard`.

## Reglas

- PC Dashboard puede usar presupuesto visual alto.
- Claridad primero: texto y acciones quedan por encima del fondo.
- Atmosphere Engine usa assets reales, no downgrade a CSS plano.
- Glow semántico: 1 fuerte máximo por viewport.
- Motion lento y con `prefers-reduced-motion`.
- Sin POS, sin checkout, sin DB, sin deploy, sin dependencias nuevas.

## Instalado

- `app/dashboard/page.tsx`
- `app/dashboard/prisma-surface-dashboard.module.css`
- `public/surface-visual-governor/dashboard/pilot-04/*`
- `public/surface-visual-governor/dashboard/latest/*`
- `scripts/verify-surface-visual-governor-pilot04.mjs`

## Siguiente paso natural

Pilot 05 · Tablet Light Shell, sin tocar POS.
