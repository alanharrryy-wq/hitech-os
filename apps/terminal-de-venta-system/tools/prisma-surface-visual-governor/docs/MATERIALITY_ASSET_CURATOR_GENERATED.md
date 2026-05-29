# PRISMA M-04 · Materiality Asset Curator

- Generated: `2026-05-28T14:47:59`
- Engine: `M-04.1-materiality-asset-curator`
- Assets clasificados: **516**
- Preview assets copiados: **215**

## Conteo por rol

| Rol | Conteo | Uso |
|---|---:|---|
| `atmosphere_background` | 208 | Fondos y atmósferas reales aptas para Atmosphere Engine. |
| `decorative_landing` | 0 | Decorativos o hero/landing. Requieren gate antes de usarse como background. |
| `brand_logo` | 19 | Marca, logos e identidad. No son fondos. |
| `product_packshot` | 253 | Producto/catálogo/packshot. No debe usarse como atmósfera de interfaz. |
| `screenshot_qa` | 29 | Capturas, evidencia, snapshots o regresión visual. Sólo evidencia. |
| `ui_icon` | 7 | Íconos, glyphs o SVG utilitarios. No son backgrounds. |
| `unknown_review` | 0 | No clasificado con confianza. Requiere decisión humana. |

## Regla

Sólo `atmosphere_background` entra directo al Atmosphere Engine. `decorative_landing` requiere gate. Logos, packshots, screenshots, íconos y unknown quedan bloqueados como fondo.

## Siguiente

Revisar curated preview board. Luego aplicar primer piloto visual real a Control Center o PC con assets curated.