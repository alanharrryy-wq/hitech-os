# PRISMA HTML · Full Surface Sweep

## Resultado

`PASS_BROWSER_HARNESS_USER_VISUAL_REVIEW_PENDING`

No representa certificación visual final. El barrido cerró validación estática y navegador Chromium; la revisión directa en Safari/iPhone sigue abierta.

## Alcance

- Índice maestro.
- Página 1: Qué es PRISMA.
- Página 2: Investor Deck.
- Página 3: Por qué PRISMA.
- Página 4: Ecosistema del producto.
- Catálogo del sistema UI.
- Sistema narrativo compartido.
- Identidad y atmósferas gobernadas.

## Contrato aplicado

- Tres escenas por página narrativa.
- Máximo `3.0` alturas de viewport en móvil, equivalente a pantalla inicial más dos desplazamientos.
- Cero overflow horizontal.
- Controles móviles de al menos 44 CSS px.
- Selector nativo más botones anterior/siguiente para tabs y steppers móviles.
- Logo único: `assets/images/prisma-logo.png`.
- Navegación de transición consistente.
- Sin `!important`, `document.write()` ni imágenes Base64 activas.

## Evidencia

- Validación estática: `PASS`.
- Checks: `382`.
- Errores: `0`.
- Browser harness: `PASS`.
- Viewports: `320×568`, `375×667`, `1440×900`.
- Consola: 0 errores.
- Page errors: 0.
- Target-size issues: 0.
- Interacciones probadas: tabs, steppers, deck, superficies, catálogo y transparencia alpha 0.

## Scroll móvil 320×568

| Superficie | Alturas de viewport |
|---|---:|
| index | 1.930 |
| page1 | 2.817 |
| page2 | 1.000 |
| page3 | 2.817 |
| page4 | 2.817 |
| catalog | 2.423 |

## Assets gobernados

- `aurora-slate-veil.svg` desde Background Catalog.
- `liquid-operations-smoke.svg` desde Background Catalog.

## Rollback

Rama remota previa al barrido:

`stash/prisma-html-before-narrative-sweep-20260715`

## Pendiente

- Revisión directa en Safari/iPhone.
- Aprobación visual del usuario.
- Decisión explícita de merge.
