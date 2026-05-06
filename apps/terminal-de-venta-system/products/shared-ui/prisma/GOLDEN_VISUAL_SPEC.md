# PRISMA POS Golden Visual Spec

Este documento convierte la referencia visual aprobada en contrato de ejecucion.
Tablet y PC deben verse como la misma familia PRISMA. Tablet es el POS
operativo; PC conserva su rol de backoffice/control tower.

## Objetivo Visual

La pantalla debe sentirse como una terminal retail premium:

- glass oscuro cinematografico
- profundidad atmosferica
- acentos oro calido
- productos en vitrina iluminada
- carrito persistente y dominante
- CTA `COBRAR` como punto final de la mirada

La version Light debe ser el equivalente diurno: frosted glass, blancos calidos,
bordes icy suaves y oro controlado. No debe convertirse en SaaS azul.

## Composicion Canonica

Vista POS en desktop:

```text
sidebar 220px | workspace catalogo flexible | carrito 420px
```

Elementos obligatorios:

1. Sidebar glass con marca PRISMA arriba.
2. Navegacion vertical con item activo gold.
3. Estado de terminal abajo.
4. Header superior con titulo de modulo y acciones de usuario.
5. Buscador ancho con icono search y boton de scan.
6. Category rail circular.
7. Product grid de 4 columnas cuando el ancho lo permite.
8. Product cards con imagen/figura grande, pedestal y glow.
9. Cart panel derecho con items, total grande y `COBRAR`.
10. Acciones secundarias debajo del CTA, sin competir con `COBRAR`.

## Proporciones

- Sidebar desktop: 220px a 236px.
- Cart desktop: 400px a 440px.
- Gap principal: 18px a 28px.
- Card product desktop: 285px a 310px de alto.
- Product image stage: minimo 150px.
- Search: 58px a 64px de alto.
- CTA `COBRAR`: 58px a 72px de alto.

## Tokens De Identidad

Usar tokens compartidos de `tokens/prisma-theme.css`:

- `--prisma-app-background`
- `--prisma-surface`
- `--prisma-glass-surface`
- `--prisma-sidebar-surface`
- `--prisma-card-surface`
- `--prisma-cart-panel-surface`
- `--prisma-text-primary`
- `--prisma-text-secondary`
- `--prisma-text-muted`
- `--prisma-border-soft`
- `--prisma-border-gold`
- `--prisma-accent-gold`
- `--prisma-accent-gold-soft`
- `--prisma-accent-gold-strong`
- `--prisma-accent-cool-frosted`
- `--prisma-frosted-accent-gradient`
- `--prisma-shadow-glass`
- `--prisma-shadow-gold`

## Dark Theme

Debe verse:

- profundo
- lujoso
- glassy
- premium
- operacional

Reglas:

- fondos charcoal/black con luz atmosferica
- bordes sutiles, no blancos fuertes
- gold solo en seleccion, CTA, precio/total e highlights
- productos con pedestal/glow
- carrito con total grande en oro

Prohibido:

- verde como CTA principal
- magenta/purple/cyan como identidad
- dashboard generico
- tarjetas planas sin profundidad

## Light Theme

Debe verse:

- blanco calido
- frosted
- tactil
- limpio
- premium

Reglas:

- acentos frios como vidrio translúcido, no azul plano
- bordes icy suaves
- sombras limpias y capas claras
- gold sigue siendo la identidad principal
- `COBRAR` mantiene jerarquia visual

Prohibido:

- azul SaaS como bloque activo
- blanco esteril sin capas
- Bootstrap/CRUD visual
- grises clinicos

## Componentes Normalizados

Los componentes visuales deben declarar `data-prisma-component` cuando aplique:

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
- EmptyState
- ErrorState

## Criterio De Aceptacion Visual

PASS si:

- la primera impresion coincide con la referencia PRISMA
- Tablet y PC comparten shell, glass, gold y jerarquia
- Tablet sigue siendo POS funcional
- PC sigue siendo backoffice
- Light se siente frosted y no azul SaaS
- `COBRAR` domina el carrito
- productos tienen vitrina/stage visual, no lista plana
- el sistema usa tokens compartidos, no colores sueltos

FAIL si:

- parece dashboard generico
- parece dark mode comun
- el Light se ve como app fintech/SaaS azul
- los productos pierden presencia visual
- el carrito no manda
- PC y Tablet parecen productos distintos
