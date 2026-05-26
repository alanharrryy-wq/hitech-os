# PRISMA Tablet · Pearl Grey Mist v2 Crystal

Este paquete convierte el primer concepto visual en código standalone e instalable.

## Qué incluye

- Fondo gris perla más evidente.
- Paneles de cristal G3/G4 con blur, rim, sombra y reflejo.
- Motion ambiental: mist drift, sheen sweep, crystal glint.
- Microinteracción: tilt fino en cards.
- `prefers-reduced-motion` para congelar el motion sin perder estética.
- Preview standalone en `preview/index.html`.
- Instalador para colocarlo dentro del paquete visual de Tablet.

## Preset

```txt
pearl-grey-mist-v2-crystal
```

## Archivos instalados

```txt
docs/design/tablet-light-visual-preset-engine/prisma-tablet-pearl-grey-mist-v2.css
docs/design/tablet-light-visual-preset-engine/prisma-tablet-pearl-grey-mist-v2.js
docs/design/tablet-light-visual-preset-engine/pearl-grey-mist-v2-smoke-test.html
```

## Uso futuro en runtime

El siguiente inyector runtime puede importar la hoja CSS y aplicar una clase root:

```tsx
<main className="prisma-pgm-stage" data-pgm-root>
  ...
</main>
```

Este paquete no toca runtime productivo todavía. Es contrato visual + código de preset + smoke test.
