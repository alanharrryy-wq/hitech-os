# PRISMA Light UI Kit

**Purpose:** define the reusable components needed to build the PRISMA Light POS screen with high visual fidelity.

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
25. `FrostedPanel`

---

## 2. `PrismaAppShell`

Root layout component.

### Contains

- light atmospheric background,
- fixed sidebar,
- main sales area,
- top action bar,
- fixed cart panel.

### Required layout

```txt
canvas: 4:3
sidebar: left, 220px
main: center, around 820px wide
cart: right, around 420px wide
```

### Rule

Do not turn the shell into a generic admin dashboard. The white version is still POS-first.

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
- Configuracion

### Style

- Width: 220px.
- Background: white/frosted.
- Right border: subtle blue-gray.
- Padding: 20px.
- Logo centered above nav.

---

## 4. `PrismaNavItem`

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

- Height: 52-54px.
- Radius: 14-16px.
- Icon: 22px.
- Gap: 12px.

### Active style

- Blue gradient fill.
- White icon/text.
- Soft blue shadow.
- No gold fill in this light skin.

---

## 5. `SearchProductInput`

### Placeholder

`Buscar producto por codigo, nombre o SKU...`

### Anatomy

- search icon left,
- placeholder/input text,
- scan/crop icon right.

### Size

- Height: 56px.
- Width: around 600px.
- Radius: 16px.

### States

| State | Visual |
|---|---|
| Default | white/frosted, soft border |
| Focus | blue focus ring |
| Disabled | opacity 0.45 |
| Error | red border + readable message |

---

## 6. `ScanButton`

### Content

- scan icon,
- text `ESCANEAR`.

### Size

- Height: 56px.
- Width: 126-148px.

### Style

White/frosted button, blue icon, uppercase label, subtle panel shadow.

---

## 7. `CategoryRail` and `CategoryCircleItem`

### Required labels

1. Todos
2. Bebidas
3. Snacks
4. Lacteos
5. Abarrotes
6. Limpieza
7. Personal
8. Next arrow

### Layout

Icon circle above label. Large gap between items. Rail sits between search row and product grid.

### Active style

- 56px circle.
- Blue fill or blue ring.
- White icon when filled.
- Blue label.
- Soft glow.

### Default style

- White circular frosted surface.
- Navy muted icon.
- Muted label.

---

## 8. `ProductGrid`

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

## 9. `ProductCard`

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
6. Add button.

### Size

- Width: approx. 194px.
- Height: approx. 300px.
- Padding: 16px.
- Radius: 16-18px.

### Text

- Name: 15-16px, semibold, max 2 lines.
- Price: 20-22px, bold.
- Stock: 13px, muted.

### Visual requirements

- Card has frosted white surface.
- Product image is large.
- Product has soft colored pedestal.
- Add button uses blue.
- Card has subtle inset highlight.

---

## 10. `CartPanel`

### Purpose

Current ticket, totals and payment.

### Anatomy

1. Header.
2. Cart lines.
3. Totals.
4. Pay button.
5. Secondary action cards.

### Size

- Width: approx. 420px.
- Height: approx. 860px.
- Radius: 22-24px.

### Style concept

```css
background: rgba(255,255,255,.78);
border: 1px solid rgba(213,220,235,.92);
box-shadow: 0 24px 80px rgba(32,45,82,.14), inset 0 1px 0 rgba(255,255,255,.86);
backdrop-filter: blur(24px) saturate(1.08);
```

---

## 11. `CartLineItem`

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
  grid-template-columns: 28px 72px 1fr auto 82px 22px;
  gap: 12px;
  align-items: center;
  padding: 18px 0;
  border-bottom: 1px solid rgba(218,225,238,.9);
}
```

---

## 12. `QuantityStepper`

### Content

`- 1 +`

### Style

- White pill background.
- Integrated buttons.
- Quantity centered.
- 86-100px wide.
- 36-38px high.
- Blue plus/minus icons.

---

## 13. `TotalsSummary`

### Required rows

| Label | Value |
|---|---:|
| Subtotal | $113.50 |
| Impuestos (IVA 16%) | $18.16 |
| Total | $131.66 |

### Rule

Total is large, blue and visually dominant.

---

## 14. `PayButton`

### Text

`COBRAR`

### Shortcut

`F2`

### Style

Blue gradient, white text, strong shadow, full width.

### Rule

The pay button must be the clearest action in the cart. If the user has to hunt for it, the interface is selling confusion by the kilo.

---

## 15. UI Kit prohibitions

- Do not replace categories with plain tabs.
- Do not replace product cards with rows.
- Do not make the pay button green.
- Do not remove product shadows/glow.
- Do not hide stock.
- Do not remove shortcut labels.
- Do not use English labels.
- Do not invent a different layout.
- Do not make the white version look like generic fintech.
