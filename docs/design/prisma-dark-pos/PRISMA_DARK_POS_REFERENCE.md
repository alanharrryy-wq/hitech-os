# PRISMA Dark POS Reference

**Reference file:** `negra.jpeg`  
**Type:** High-Fidelity Reference Mockup  
**Purpose:** exact visual breakdown of the target screen for implementation and validation.

---

## 1. One-line description

Dark premium PRISMA point-of-sale screen with left navigation, central product catalog, and right-side sales cart, using warm gold accents, glass surfaces, realistic product cards and a large `COBRAR` button.

---

## 2. Canvas

| Property | Value |
|---|---|
| Aspect ratio | 4:3 |
| Recommended mockup size | 1536 x 1024 px |
| Orientation | Landscape |
| UI language | Spanish / es-MX |
| Visual family | Dark premium POS |

---

## 3. Screen map

```txt
┌────────────────────┬──────────────────────────────────────────────┬────────────────────────────┐
│ Sidebar            │ Main Sales Area                              │ Cart / Top Controls        │
│                    │                                              │                            │
│ PRISMA logo        │ Ventas                                       │ Sun / Bell / Admin         │
│ Nav                │ Search + ESCANEAR + ...                      │ Carrito de venta           │
│                    │ Category rail                                │ Cart items                 │
│                    │ Product grid 4 x 2                           │ Subtotal / IVA / Total     │
│ Terminal status    │ Pagination                                   │ COBRAR + actions           │
└────────────────────┴──────────────────────────────────────────────┴────────────────────────────┘
```

---

## 4. Sidebar details

### Position

- Left edge.
- Full height.
- Approx. width: 200px.

### Logo area

Visible content:

```txt
PRISMA
SISTEMA DE GESTIÓN INTELIGENTE
```

The logo is a geometric prism/triangle above the wordmark.

Visual treatment:

- monochrome metallic/gray,
- elegant tracking,
- centered,
- lots of vertical air.

### Navigation list

Exact visible labels:

1. Ventas
2. Dashboard
3. Inventario
4. Clientes
5. Productos
6. Compras
7. Caja
8. Reportes
9. Gastos
10. Promociones
11. Usuarios
12. Configuración

### Active navigation item

Active item: `Ventas`

Visual state:

- gold glass fill,
- gold border,
- cart icon in gold,
- text in gold/cream,
- soft outer glow.

### Bottom terminal card

Visible text:

```txt
Terminal 01
En línea
```

Includes:

- avatar/terminal icon,
- green status dot,
- dropdown chevron.

---

## 5. Top header details

### Screen title

Text:

```txt
Ventas
```

Position:

- top-left of main area,
- large, white/cream,
- semibold/bold.

### Top-right controls

Visible items:

1. Sun icon.
2. Notification bell with badge `3`.
3. Admin pill.

Admin pill text:

```txt
AR
Administrador
Sucursal Centro
```

---

## 6. Search row

### Search input

Placeholder:

```txt
Buscar producto por código, nombre o SKU...
```

Includes:

- search icon left,
- scan/crop icon right.

Visual:

- dark glass background,
- subtle border,
- rounded rectangle,
- approx. 56px height.

### Scan button

Text:

```txt
ESCANEAR
```

Includes scan icon and uppercase label.

### More button

Text/icon:

```txt
...
```

Rounded square button.

---

## 7. Category rail

Visible categories:

| Order | Label | State |
|---:|---|---|
| 1 | Todos | active |
| 2 | Bebidas | default |
| 3 | Snacks | default |
| 4 | Lácteos | default |
| 5 | Abarrotes | default |
| 6 | Limpieza | default |
| 7 | Personal | default |
| 8 | `>` | navigation |

Each category has:

- circular icon button,
- label below.

Active `Todos`:

- gold circle,
- warm glow,
- icon centered.

---

## 8. Product grid

### Layout

- 4 columns.
- 2 rows visible.
- Large cards.
- Cards have rounded corners, dark glass, inner highlight and product glow.

### Product card anatomy

Each product card includes:

1. Favorite star at top.
2. Large product image.
3. Colored glow/pedestal below product.
4. Product name.
5. Price.
6. Stock.

### Products visible

| Position | Product | Price | Stock | Visual glow |
|---:|---|---:|---:|---|
| 1 | Coca Cola 600 ml | $18.00 | 156 | red |
| 2 | Sabritas Original 45 g | $15.00 | 142 | yellow/gold |
| 3 | Leche Lala Entera 1 L | $28.50 | 98 | cool white |
| 4 | Agua Ciel 1 L | $16.00 | 83 | blue |
| 5 | Nescafé Clásico 200 g | $145.00 | 42 | brown/red |
| 6 | Pan Bimbo Blanco Grande | $34.00 | 87 | amber |
| 7 | Ace 1 kg | $38.50 | 28 | orange |
| 8 | Zucaritas Kellogg's 730 g | $67.00 | 31 | blue |

### Notes

- Product image should occupy around half the card height.
- Stock is small and muted.
- Price is clear and stronger than stock.
- Some stars are gold, some are muted.

---

## 9. Pagination

Position:

- bottom of product area,
- centered inside wide glass bar.

Visible controls:

```txt
< 1 2 3 4 5 >
```

Active page `1`:

- gold border,
- subtle gold glow.

---

## 10. Cart panel

### Position and style

- Fixed right.
- Tall rounded panel.
- Dark glass background.
- Subtle gold border.
- Deep shadow.

### Header

Visible text:

```txt
Carrito de venta
4 artículos
```

Also includes trash icon.

---

## 11. Cart line items

Exact visible items:

| Line | Product | Unit price | Quantity | Total |
|---:|---|---:|---:|---:|
| 1 | Coca Cola 600 ml | $18.00 | 2 | $36.00 |
| 2 | Sabritas Original 45 g | $15.00 | 1 | $15.00 |
| 3 | Leche Lala Entera 1 L | $28.50 | 1 | $28.50 |
| 4 | Pan Bimbo Blanco Grande | $34.00 | 1 | $34.00 |

Each line item has:

- index circle,
- thumbnail,
- product name,
- unit price,
- quantity stepper,
- line total,
- remove `x`.

Visual separators are subtle horizontal lines.

---

## 12. Totals section

Exact visible values:

| Label | Value |
|---|---:|
| Subtotal | $113.50 |
| Impuestos (IVA 16%) | $18.16 |
| Total | $131.66 |

### Total style

The total label and amount are gold. The amount is large and visually dominant.

---

## 13. Primary payment button

Text:

```txt
COBRAR
```

Shortcut:

```txt
F2
```

Style:

- full width,
- gold gradient,
- dark text,
- strong rounded rectangle,
- warm glow.

This is the strongest action in the UI.

---

## 14. Secondary action cards

Visible bottom actions:

| Label | Shortcut |
|---|---|
| COTIZACIÓN | F3 |
| GUARDAR | F4 |
| LIMPIAR | F5 |

Each card:

- dark glass surface,
- icon above,
- uppercase label,
- shortcut below,
- subtle border.

---

## 15. Exact visible text list

Use this list for demo matching:

```txt
PRISMA
SISTEMA DE GESTIÓN INTELIGENTE
Ventas
Dashboard
Inventario
Clientes
Productos
Compras
Caja
Reportes
Gastos
Promociones
Usuarios
Configuración
Terminal 01
En línea
Buscar producto por código, nombre o SKU...
ESCANEAR
Todos
Bebidas
Snacks
Lácteos
Abarrotes
Limpieza
Personal
Carrito de venta
4 artículos
Subtotal
Impuestos (IVA 16%)
Total
COBRAR
F2
COTIZACIÓN
F3
GUARDAR
F4
LIMPIAR
F5
Administrador
Sucursal Centro
```

---

## 16. Visual matching priorities

When implementing, match in this order:

1. Overall 3-zone composition.
2. Sidebar width and content.
3. Cart width, height and border.
4. Main area position.
5. Search row.
6. Category rail.
7. Product grid dimensions.
8. Product image size and glow.
9. Total and `COBRAR` hierarchy.
10. Typography and icon polish.

If only one thing can be perfect, make the layout perfect first. Pretty details on the wrong skeleton are just lipstick on a shopping cart.

---

## 17. Implementation fidelity rules

A result is acceptable only if:

- it is clearly the same PRISMA dark POS screen,
- it keeps the left sidebar / center catalog / right cart structure,
- it uses warm gold as the main accent,
- it has large product cards with glow,
- it uses Spanish labels,
- it keeps the cart totals and payment button prominent,
- it avoids generic admin dashboard styling.

Target: **90-95% visual similarity**.

---

## 18. Blockers

Reject the implementation if:

- `COBRAR` is green,
- product grid is replaced by a table,
- sidebar is missing,
- cart is not fixed to the right,
- product images are tiny,
- background is flat black,
- interface uses English labels,
- gold accent is missing,
- layout becomes mobile-first,
- it looks like a generic template.

---

## 19. Final reference rule

The image `negra.jpeg` wins over any written interpretation.

If a written rule and the screenshot conflict, follow the screenshot.
