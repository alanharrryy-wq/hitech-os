# PRISMA Shared UI

Esta carpeta es la capa visual compartida para PC y Tablet.

El contrato visual de referencia vive en `GOLDEN_VISUAL_SPEC.md`.

## Activacion de temas

Las apps consumen el tema desde `data-theme` en el elemento `html`.

- `data-theme="prisma-dark"`
- `data-theme="prisma-light"`

Por defecto ambas apps usan `prisma-dark`. Para probar Light:

```powershell
$env:NEXT_PUBLIC_PRISMA_THEME="prisma-light"
```

Luego inicia la app con el launcher oficial del proyecto.

## Tokens canonicos

Los tokens viven en `tokens/prisma-theme.css` y cubren:

- fondos de app, superficies, glass, sidebar, cards y cart
- textos primario, secundario y muted
- bordes soft, medium, strong y gold
- acentos gold y cool frosted
- estados success, warning, danger e info
- focus ring, sombras, radios y motion

Los componentes deben consumir tokens semanticos como `--prisma-surface`,
`--prisma-accent-gold` y `--prisma-accent-cool-frosted`. Evita colores sueltos
cuando ya exista un token.

## Componentes compartidos

`components/prisma-components.css` define comportamiento comun mediante
`data-prisma-component`.

Los nombres oficiales normalizados son:

- AppShell
- Sidebar
- BrandBlock
- NavItem
- TerminalStatusCard
- TopBar
- SearchBar
- ScanButton
- IconButton
- UserMenu
- CategoryRail
- CategoryButton
- ProductGrid
- ProductCard
- ProductImageStage
- FavoriteStar
- Pagination
- CartPanel
- CartHeader
- CartItemRow
- QuantityStepper
- TotalsSummary
- CheckoutButton
- SecondaryActionCard
- Toast
- EmptyState
- ErrorState

## Reglas visuales

- Gold es el acento principal de identidad PRISMA.
- Dark debe mantenerse premium, cinematico, profundo y glassy.
- Light debe ser blanco calido, tactil y premium.
- En Light, los acentos frios se interpretan como glass/frosted, no como azul plano.
- No usar morado, magenta o cyan como identidad de marca.
- No usar verde como CTA principal.
- `COBRAR` debe ser el CTA dominante.
