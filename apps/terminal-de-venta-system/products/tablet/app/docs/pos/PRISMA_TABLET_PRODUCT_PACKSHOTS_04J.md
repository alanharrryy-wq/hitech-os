# PRISMA Tablet Product Packshots 04J

## Objetivo

Activar imágenes de producto en el catálogo POS de Tablet sin meter logos oficiales, fotos sin licencia ni assets que se rompan en card chica.

## Qué instala

- 15 packshots PNG transparentes 512x512 en `products/tablet/app/public/pos-packshots/`.
- Resolver `components/pos/pos-packshots.ts` con reglas por nombre, SKU y categoría.
- README de contrato público de assets.

## Criterio visual

Las imágenes están hechas para:

- card de producto en `/pos`;
- miniatura del ticket/carrito;
- fondo premium oscuro con pedestal/glass ya existente;
- carga rápida desde `public/` de Next;
- fallback tipográfico si un PNG falla.

## Nota honesta

Estos packshots son ilustraciones genéricas. No son arte oficial de Coca-Cola, Bimbo, Sabritas ni ninguna otra marca.
Para producción comercial con marcas reales, reemplaza los PNG manteniendo los mismos nombres o actualiza el resolver.

## Validación sugerida

```powershell
python F:\descargasf\install_prisma_tablet_product_packshots_04j_20260503_v01.py --target-root F:epos\hitech-ospps	erminal-de-venta-system --zip-path F:\descargasf\PRISMA_TABLET_PRODUCT_PACKSHOTS_04J_20260503_v01.zip --dry-run
python F:\descargasf\install_prisma_tablet_product_packshots_04j_20260503_v01.py --target-root F:epos\hitech-ospps	erminal-de-venta-system --zip-path F:\descargasf\PRISMA_TABLET_PRODUCT_PACKSHOTS_04J_20260503_v01.zip --apply
python F:\descargasf\install_prisma_tablet_product_packshots_04j_20260503_v01.py --target-root F:epos\hitech-ospps	erminal-de-venta-system --verify
```

Después abre `/pos` y revisa que productos de bebidas, botanas, lácteos, panadería, limpieza, higiene, mascotas, desechables, mostrador y congelados ya muestren imagen en card y ticket.
