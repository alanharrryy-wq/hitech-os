# PRISMA Black Visual Governance Pass 01D

## Objetivo

Este pass gobierna la estética PRISMA Black con una regla sencilla: un fondo vivo manda, los paneles interpretan y las cards no reinventan el clima.

## Qué instala

- Tokens para fondo cinematográfico, glass, blur, bordes, glows y motion.
- Capa de fondo global con haze/motion sutil y `prefers-reduced-motion`.
- Paneles grandes con glass fuerte.
- Cards con glass ligero.
- Product stage como vitrina local.
- Flags CSS para apagar haze, noise, motion, card blur y product glow.
- Perfil `perf` para reducir blur/textura/motion sin romper legibilidad.

## Reglas de QA

- Máximo 3 glows importantes por pantalla.
- Máximo 1 motion hero global.
- No haze por card.
- No noise por card.
- No fondo duplicado en body + shell + panel.
- CTA, precio, búsqueda y total deben leerse rápido.

## Flags útiles

```text
html[data-layer-stage-haze="off"]
html[data-layer-stage-noise="off"]
html[data-layer-motion-enabled="off"]
html[data-layer-card-blur="off"]
html[data-layer-product-glow="off"]
html[data-prisma-profile="perf"]
```

## Archivos tocados

```text
products/shared-ui/prisma/tokens/prisma-theme.css
products/shared-ui/prisma/components/prisma-components.css
products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css
products/tablet/app/components/pos/pos.module.css
products/pc/app/app/globals.css
products/tablet/app/app/globals.css
```
