# PRISMA PC UIUX V03 · Playwright Visual Gate

Este paquete agrega el gate visual con Playwright para PC UIUX.

## Qué valida

- Capturas 1920x1080 de rutas PC principales.
- Navegación/copy humano visible.
- Ausencia de términos técnicos prohibidos en navegación/acciones visibles.
- Overflow horizontal básico.
- Existencia de shell principal, navegación o acciones.
- Errores de página y consola.
- Evidencia exportada en PNG, HTML, CSV, JSON y Markdown.

## No cambia diseño

Este paquete no rediseña pantallas. Sólo instala el verificador visual y scripts asociados.

## Resultado

El runner deja un ZIP de resultados en `F:\descargasf` con:

- `VISUAL_GATE_SUMMARY.md`
- `VISUAL_ROUTE_MATRIX.csv`
- `VISUAL_GATE_RESULT.json`
- `screenshots/*.png`
- `html/*.html`
- logs del servidor si se arrancó desde el wrapper
