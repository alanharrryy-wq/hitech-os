# PRISMA HTML · Sistema narrativo

Sitio HTML modular de PRISMA dentro del Draft PR `feature/prisma-html-investor-site`.

## Enlace maestro

La entrada completa es:

`index.html`

Desde ahí se abren:

- Página 1 · Qué es PRISMA.
- Página 2 · Investor Deck.
- Página 3 · Por qué PRISMA.
- Página 4 · Ecosistema del producto.
- Catálogo · Sistema visual.

## Contrato narrativo

Las páginas públicas comparten:

- identidad oficial desde `assets/images/prisma-logo.png`;
- atmósferas gobernadas;
- máximo tres escenas;
- transición anterior/siguiente;
- progreso visible;
- controles móviles de 44 CSS px;
- selector nativo y flechas en móvil;
- tabs y steppers con ARIA y teclado en escritorio;
- cero overflow horizontal;
- fallback sin `backdrop-filter`;
- soporte para movimiento reducido.

La autoridad compartida vive en:

- `sistema-ui/css/patrones/narrative-page.css`
- `sistema-ui/js/componentes/prisma-narrative.js`

## Atmósferas gobernadas

- `assets/atmosphere/aurora-slate-veil.svg`
- `assets/atmosphere/liquid-operations-smoke.svg`

Ambas provienen del Background Catalog del repositorio.

## Validación

```powershell
python -m pip install -r requirements-dev.txt
python tools\validate_project.py --root . --report validation.json
```

Estado actual:

- Validación estática: PASS, 382 checks, 0 errores.
- Browser harness Chromium: PASS.
- Viewports: 320×568, 375×667 y 1440×900.
- Revisión Safari/iPhone: pendiente.
- Certificación visual final: pendiente.
- Merge: bloqueado hasta aprobación explícita.

Reportes:

- `reports/FULL_SURFACE_SWEEP.md`
- `reports/full-surface-sweep.json`
- `governance/PRISMA_HTML_NARRATIVE_SWEEP_MANIFEST.json`

## Rollback

Estado remoto anterior al barrido:

`stash/prisma-html-before-narrative-sweep-20260715`

## Límites

Este proyecto no modifica Tablet POS, PC Admin, Mobile Companion, Chart Lab, Control Center, bases de datos, Prisma schema, procesos, puertos ni despliegues.
