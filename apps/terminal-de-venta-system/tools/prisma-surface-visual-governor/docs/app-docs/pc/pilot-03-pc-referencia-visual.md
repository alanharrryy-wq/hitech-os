# PRISMA Surface Visual Governor · Pilot 03 · PC Referencia Visual

## Estado esperado

Pilot 03 conecta la ruta PC `/referencia-visual` con el Materiality Catalog y las recetas exportadas por Chart Lab en Pilot 02.

No aplica el look a rutas operativas. No toca POS. No toca DB. No instala dependencias. No hace deploy.

## Qué instala

- `products/pc/app/app/referencia-visual/page.tsx`
- `products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/prisma-pc-reference-visual.css`
- `products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/index.json`
- `products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/route.visual-reference.pilot-03.json`
- `products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/surface-twin.pc-reference.json`
- mirror del Materiality Catalog desde Tablet Visual OS
- mirror de recetas Pilot 02 desde Chart Lab
- mirror de assets reales de Atmosphere Engine
- `products/pc/app/scripts/verify-surface-visual-governor-pilot03.mjs`

## Gates

- PC: permitido como sala aislada de referencia visual.
- Tablet: light-first preservado, no se modifica.
- POS: bloqueado hasta gate final.
- DB: no touch.
- Deploy/Cloudflare: no touch.
- Dependencies: no touch.

## Mantra

La galería es laboratorio. El Materiality Catalog es contrato. El Governor es policía. Chart Lab es taller. PC ahora es sala. POS se toca al final.
