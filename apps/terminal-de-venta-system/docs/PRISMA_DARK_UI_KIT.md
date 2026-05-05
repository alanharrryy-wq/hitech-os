# PRISMA Dark UI Kit

**Purpose:** define the reusable components needed to build the PRISMA Dark POS screen with high visual fidelity.

---

## 1. Component inventory

Canonical components:

1. `PrismaAppShell`
2. `PrismaSidebar`
3. `PrismaLogoBlock`
4. `PrismaNavItem`
5. `TerminalStatusCard`
6. `TopActionBar`
7. `AdminUserChip`
8. `SearchProductInput`
9. `ScanButton`
10. `RoundIconButton`
11. `CategoryRail`
12. `CategoryCircleItem`
13. `ProductGrid`
14. `ProductCard`
15. `ProductImageStage`
16. `PaginationBar`
17. `CartPanel`
18. `CartLineItem`
19. `QuantityStepper`
20. `TotalsSummary`
21. `PayButton`
22. `SecondaryActionCard`
23. `StatusBadge`
24. `ShortcutHint`
25. `GlassPanel`

---

## 2. `PrismaAppShell`

Root layout component.

### Contains

- atmospheric background,
- fixed sidebar,
- main sales area,
- top action bar,
- fixed cart panel.

### Required layout

```txt
canvas: 4:3
sidebar: left, 200px
main: center, around 780px wide
cart: right, around 426px wide
```

### Rule

Do not make it a normal dashboard grid. It must keep the POS composition.

---

## 3. `PrismaSidebar`

### Purpose

Brand identity, navigation and terminal status.

### Required structure

```tsx
<aside>
  <PrismaLogoBlock />
  <nav>
    <PrismaNavItem active label="Ventas" />
    ...
  </nav>
  <TerminalStatusCard />
</aside>
```

### Navigation labels

- Ventas
- Dashboard
- Inventario
- Clientes
- Productos
- Compras
- Caja
- Reportes
- Gastos
- Promociones
- Usuarios
- Configuración

### Style

- Width: 200px.
- Background: near-black glass.
- Right border: subtle.
- Padding: 20px.
- Logo centered above nav.

---

## 4. `PrismaLogoBlock`

### Required content

- PRISMA geometric logo.
- `PRISMA` wordmark.
- `SISTEMA DE GESTIÓN INTELIGENTE` subtitle.

### Visual rule

Use real PRISMA asset if available. Do not invent a logo unless the asset is missing. Logo must feel metallic/monochrome, not cartoonish.

---

## 5. `PrismaNavItem`

### Props

```ts
type PrismaNavItemProps = {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  disabled?: boolean;
}
```

### Size

- Height: 50-52px.
- Radius: 10-12px.
- Icon: 22px.
- Gap: 12px.

### Active style

- Gold border.
- Warm dark-gold fill.
- Gold icon/text.
- Soft glow.

---

## 6. `TerminalStatusCard`

### Content

- user/terminal icon,
- `Terminal 01`,
- `En línea`,
- green status dot,
- chevron.

### Position

Bottom of sidebar.

### Style

Dark glass card, soft border, 12-14px radius.

---

## 7. `TopActionBar`

### Purpose

Global actions near top right.

### Contains

- theme/sun icon,
- notification bell with badge `3`,
- `AdminUserChip`.

### Position

Top right, aligned above cart panel.

---

## 8. `AdminUserChip`

### Content

- avatar with `AR`,
- name `Administrador`,
- subtitle `Sucursal Centro`,
- chevron.

### Style

Pill glass, 54px height, dark background, subtle border.

---

## 9. `SearchProductInput`

### Placeholder

`Buscar producto por código, nombre o SKU...`

### Anatomy

- search icon left,
- placeholder/input text,
- scan/crop icon right.

### Size

- Height: 56px.
- Width: around 595-610px.
- Radius: 14-16px.

### States

| State | Visual |
|---|---|
| Default | glass dark, soft border |
| Focus | gold focus ring |
| Disabled | opacity 0.45 |

---

## 10. `ScanButton`

### Content

- scan icon,
- text `ESCANEAR`.

### Size

- Height: 56px.
- Width: 126-138px.

### Style

Dark glass button, scan icon in warm gold, uppercase label.

---

## 11. `RoundIconButton`

Used for the `...` button and top small actions.

### Size

- 48-56px square.
- Radius 14px or pill depending location.
- Centered icon.

### Style

Dark glass, subtle border, hover gold border.

---

## 12. `CategoryRail`

### Purpose

Horizontal product category filter.

### Required labels

1. Todos
2. Bebidas
3. Snacks
4. Lácteos
5. Abarrotes
6. Limpieza
7. Personal
8. Next arrow

### Layout

Icon circle above label. Large gap between items. Rail sits between search row and product grid.

---

## 13. `CategoryCircleItem`

### Props

```ts
type CategoryCircleItemProps = {
  label: string;
  icon: React.ReactNode;
  active?: boolean;
}
```

### Active style

- 54-58px circle.
- Radial gold background.
- Gold glow.
- Label brighter.

### Default style

- Dark circular glass.
- Muted icon.
- Muted label.

---

## 14. `ProductGrid`

### Layout

```txt
columns: 4
visible rows: 2
gap-x: 14-16px
gap-y: 18px
```

### Rule

The grid must feel tactile and premium. Do not use tables for this sales screen.

---

## 15. `ProductCard`

### Props

```ts
type ProductCardProps = {
  name: string;
  price: number;
  stock: number;
  imageSrc: string;
  favorite?: boolean;
  glowColor?: string;
  selected?: boolean;
  disabled?: boolean;
}
```

### Anatomy

1. Favorite star.
2. Product image stage.
3. Product name.
4. Price.
5. Stock.

### Size

- Width: approx. 188px.
- Height: approx. 272px.
- Padding: 16px.
- Radius: 16px.

### Text

- Name: 15-16px, semibold, max 2 lines.
- Price: 20-22px, bold.
- Stock: 13px, muted.

### Visual requirements

- Card has glass surface.
- Product image is large.
- Product has glow/pedestal.
- Card has subtle inset highlight.

---

## 16. `ProductImageStage`

### Purpose

Makes product images look premium.

### Anatomy

- container stage,
- blurred glow ellipse,
- product image,
- drop shadow.

### CSS concept

```css
.productStage {
  position: relative;
  height: 154px;
  display: grid;
  place-items: center;
}

.productGlow {
  position: absolute;
  bottom: 16px;
  width: 118px;
  height: 28px;
  border-radius: 999px;
  background: radial-gradient(ellipse, var(--product-glow), transparent 70%);
  filter: blur(6px);
}

.productImage {
  z-index: 2;
  max-height: 138px;
  max-width: 118px;
  object-fit: contain;
  filter: drop-shadow(0 16px 20px rgba(0,0,0,.45));
}
```

---

## 17. `PaginationBar`

### Content

- left arrow,
- pages `1 2 3 4 5`,
- right arrow.

### Style

- wide dark glass container,
- active page with gold border/glow,
- square rounded buttons.

---

## 18. `CartPanel`

### Purpose

Current ticket, totals and payment.

### Anatomy

1. Header.
2. Cart lines.
3. Totals.
4. Pay button.
5. Secondary action cards.

### Size

- Width: approx. 426px.
- Height: approx. 862px.
- Radius: 22-24px.

### Style

```css
background: rgba(15,16,22,.78);
border: 1px solid rgba(232,189,103,.28);
box-shadow: 0 24px 90px rgba(0,0,0,.50), inset 0 1px 0 rgba(255,255,255,.05);
backdrop-filter: blur(24px);
```

---

## 19. `CartLineItem`

### Props

```ts
type CartLineItemProps = {
  index: number;
  name: string;
  unitPrice: number;
  quantity: number;
  total: number;
  imageSrc: string;
}
```

### Anatomy

- index circle,
- product thumbnail,
- name,
- unit price,
- quantity stepper,
- line total,
- remove button.

### Layout concept

```css
.cartLine {
  display: grid;
  grid-template-columns: 24px 72px 1fr auto 74px 20px;
  gap: 12px;
  align-items: center;
  padding: 18px 0;
  border-bottom: 1px solid rgba(255,255,255,.08);
}
```

---

## 20. `QuantityStepper`

### Content

`- 1 +`

### Style

- Pill dark background.
- Integrated buttons.
- Quantity centered.
- 86-96px wide.
- 36-38px high.

---

## 21. `TotalsSummary`

### Required rows

| Label | Value |
|---|---:|
| Subtotal | $113.50 |
| Impuestos (IVA 16%) | $18.16 |
| Total | $131.66 |

### Rule

Total is large, gold and visually dominant.

---

## 22. `PayButton`

### Text

`COBRAR`

### Shortcut

`F2`

### Style

Gold gradient, dark text, strong shadow, full width.

### Rule

The pay button must be the clearest action in the cart. If the user has to hunt for it, the UI is doing clown work.

---

## 23. `SecondaryActionCard`

### Required actions

| Label | Shortcut |
|---|---|
| COTIZACIÓN | F3 |
| GUARDAR | F4 |
| LIMPIAR | F5 |

### Style

- dark glass card,
- subtle border,
- small gold icon,
- uppercase label,
- shortcut below.

---

## 24. Screen assembly example

```tsx
<PrismaAppShell>
  <PrismaSidebar active="Ventas" />

  <main className="salesArea">
    <h1>Ventas</h1>
    <div className="searchRow">
      <SearchProductInput />
      <ScanButton />
      <RoundIconButton icon="ellipsis" />
    </div>
    <CategoryRail active="Todos" />
    <ProductGrid products={products} />
    <PaginationBar current={1} pages={[1, 2, 3, 4, 5]} />
  </main>

  <TopActionBar />
  <CartPanel cart={cart} totals={totals} />
</PrismaAppShell>
```

---

## 25. Demo data required for visual match

Use these products in previews:

- Coca Cola 600 ml — $18.00 — Stock: 156
- Sabritas Original 45 g — $15.00 — Stock: 142
- Leche Lala Entera 1 L — $28.50 — Stock: 98
- Agua Ciel 1 L — $16.00 — Stock: 83
- Nescafé Clásico 200 g — $145.00 — Stock: 42
- Pan Bimbo Blanco Grande — $34.00 — Stock: 87
- Ace 1 kg — $38.50 — Stock: 28
- Zucaritas Kellogg's 730 g — $67.00 — Stock: 31

Cart preview:

- Coca Cola 600 ml x2 — $36.00
- Sabritas Original 45 g x1 — $15.00
- Leche Lala Entera 1 L x1 — $28.50
- Pan Bimbo Blanco Grande x1 — $34.00

Totals:

- Subtotal $113.50
- IVA 16% $18.16
- Total $131.66

---

## 26. UI Kit prohibitions

- Do not replace categories with plain tabs.
- Do not replace product cards with rows.
- Do not make the pay button green.
- Do not remove product glow.
- Do not hide stock.
- Do not remove shortcut labels.
- Do not use English labels.
- Do not invent a different layout.
