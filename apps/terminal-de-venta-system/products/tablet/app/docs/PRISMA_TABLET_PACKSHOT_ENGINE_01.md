# PRISMA Tablet Packshot Engine 01

## Propósito

Este paquete instala el motor visual para packshots duales de PRISMA Tablet.

No instala imágenes finales por defecto. Deja preparado el sistema para que, cuando existan las carpetas de staging:

```text
F:\dark packshots
F:\light packshots
```

el instalador pueda copiarlas hacia el `public/` real de Tablet:

```text
products/tablet/app/public/products/packshots/dark
products/tablet/app/public/products/packshots/light
```

## Contrato de nombres

Cada producto debe usar el mismo nombre base en dark y light:

```text
light/aurevia-pan-de-caja-multigrano-620g.png
dark/aurevia-pan-de-caja-multigrano-620g.png
```

Los nombres deben ser slugs ASCII en minúsculas, con guiones y extensión `.png`.

## Cómo resuelve la UI

`components/pos/pos-packshots.ts` resuelve el packshot con este orden:

1. packshot específico del skin activo;
2. packshot específico del skin opuesto;
3. fallback de categoría del skin activo;
4. fallback de categoría del skin opuesto;
5. packshot específico legacy si existía;
6. fallback genérico legacy de `/pos-packshots`;
7. fallback final `cereal_box_512.png`.

## Cómo detecta skin

`components/pos/use-prisma-packshot-skin.ts` observa:

```text
html[data-prisma-skin="light"]
html[data-prisma-skin="dark"]
```

La UI actual ya usa `data-prisma-skin` para PRISMA Light/Dark. El motor solo lo lee, no gobierna el selector.

## Superficies tocadas

- `components/pos/pos-packshots.ts`
- `components/pos/use-prisma-packshot-skin.ts`
- `components/pos/pos-product-list.tsx`
- `components/pos/pos-ticket-panel.tsx`
- `tools/verify_prisma_tablet_packshot_engine_01.mjs`
- carpetas `public/products/packshots/light` y `public/products/packshots/dark`

## Zonas no tocadas

- `src/server/*`
- `app/api/*`
- `prisma/*`
- `data/*`
- `sync/*`
- `pos-engine/*`
- `pos-api/*`
- `shared-kernel/*`
- PC app

## Validación

Después de instalar:

```text
node F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\tools\verify_prisma_tablet_packshot_engine_01.mjs
```

Si todavía no hay PNGs en ambas carpetas, el verificador reporta `READY_WITH_CAVEATS`, no `BLOCKED`.
