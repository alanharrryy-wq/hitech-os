# PRISMA Tablet Surface · Fuji Cloudglass

Package: `tablet surf1 0306 2327`

## Scope

This injection updates only the Tablet home/light shell surface.

Touched files:

- `products/tablet/app/app/page.tsx`
- `products/tablet/app/app/prisma-tablet-light-shell.module.css`
- `products/tablet/app/scripts/verify-surface-visual-governor-pilot05.mjs`
- `products/tablet/app/public/surface-visual-governor/tablet-light-shell/latest/**`
- `products/tablet/app/public/surface-visual-governor/tablet-light-shell/pilot-05/**`
- this document

Protected by design:

- `products/tablet/app/app/pos/**`
- `products/tablet/app/app/checkout/**`
- `products/tablet/app/components/pos/**`
- `products/pc/**`
- `products/mobile/**`
- DB, Prisma schema, launcher and sync wiring

## Visual direction

Fuji/cloud wallpaper plus light frosted glass panels. The interface remains light-first, tactile and legible. No WebGL, no Pixi, no dark storm.

## Asset

`tablet-fuji-cloudglass.jpg` SHA256:

```txt
957ca8b71ed3177da04ad5c2246693f5c504056d9ad3c5bb58c9d97b0d2978b1
```

The old `tablet-soft-gray-clouds.svg` is preserved as a compatibility alias so older checks do not fall into the barranca.
