# PRISMA Tablet Packshot Engine 02

## Purpose

Engine 01 installed the skin-aware folders and copied the new PNGs. Engine 02 fixes the resolver layer so real catalog product names like `Aceite Capullo 1 L`, `Atún Dolores en Agua 140 g`, `Avena Quaker 400 g`, and `Azúcar Estándar 1 kg` resolve to the new generic generated packshots instead of falling back to old legacy images.

## Scope

Touches only visual packshot resolution:

- `components/pos/pos-packshots.ts`
- `tools/verify_prisma_tablet_packshot_engine_02.mjs`
- this documentation file

No POS sale, stock, sync, DB, API, checkout, PC, or shared-kernel behavior is modified.

## Runtime rule

Tablet canonical URL is:

```text
http://127.0.0.1:3120/
```

`/prisma-dark-pos-reference` is not the operational Tablet URL.

## What changed

- Adds `GENERATED_PRODUCT_RULES`, a deterministic synonym map from real catalog names to generic generated image slugs.
- Moves high-risk false-positive cases like `Atún ... en Agua` before generic `agua` matching.
- Adds real skin fallback slugs per category, instead of trying missing `_fallback-*` images first.
- Keeps legacy `/pos-packshots/*.png` as final safety fallback.

## Expected visual result

The first POS grid should stop showing the old `FRASCO`/cola placeholders for common products and should resolve approximately as:

- Aceite Capullo / Patrona -> `aceite-vegetal.png`
- Arroz Verde Valle -> `arroz-1kg.png`
- Atún Dolores -> `atun-en-agua-140g.png`
- Avena Quaker -> `avena-hojuelas-500g.png`
- Azúcar Estándar -> `azucar-refinada-1kg.png`
- Café Nescafé Clásico -> `cafe-soluble-200g.png`
