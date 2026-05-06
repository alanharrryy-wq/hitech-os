# PRISMA Light POS Reference

**Reference file:** white PRISMA POS screenshot
**Type:** High-Fidelity Reference Mockup
**Purpose:** exact visual breakdown of the white / light PRISMA POS screen for implementation and validation.

---

## 1. One-line description

PRISMA Light POS is a clean premium point-of-sale screen with left navigation, central product catalog, and right-side sales cart. It uses white and frosted surfaces, deep navy text, blue primary actions, soft shadows, realistic product cards, and a large `COBRAR` button.

This is the calm daytime cousin of PRISMA Dark POS. Same family, different outfit. Not a repaint with correction fluid, gracias.

---

## 2. Canvas

| Property | Value |
|---|---|
| Aspect ratio | 4:3 |
| Recommended mockup size | 1536 x 1024 px |
| Orientation | Landscape |
| UI language | Spanish / es-MX |
| Visual family | Light premium operational POS |
| Primary accent | Blue primary |
| Surface language | Frosted white, soft panels, clean depth |

---

## 3. Screen map

```txt
+--------------------+----------------------------------------------+----------------------------+
| Sidebar            | Main Sales Area                              | Cart / Top Controls        |
|                    |                                              |                            |
| PRISMA logo        | Ventas                                       | Sun / Bell / Admin         |
| Nav                | Search + ESCANEAR + ...                      | Carrito de venta           |
|                    | Category rail                                | Cart items                 |
|                    | Product grid 4 x 2                           | Subtotal / IVA / Total     |
| Terminal status    | Pagination                                   | COBRAR + actions           |
+--------------------+----------------------------------------------+----------------------------+
```

This three-zone composition is mandatory. The UI can evolve, but this skeleton is the concrete slab. Pretty pixels on a wrong skeleton are just a taco stand built on wet cardboard.

---

## 4. Sidebar details

### Position

- Left edge.
- Full height.
- Approx. width: 220px.
- White / frosted panel with subtle right border.

### Logo area

Visible content:

```txt
PRISMA
SISTEMA DE GESTION INTELIGENTE
```

Visual treatment:

- Geometric prism logo.
- Blue / crystal mark allowed.
- Wide wordmark tracking.
- Centered.
- Lots of vertical air.

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
12. Configuracion

### Active navigation item

Active item: `Ventas`

Visual state:

- Deep blue fill or blue gradient.
- White text.
- White/blue cart icon.
- Rounded rectangle.
- Soft blue shadow.

### Bottom terminal card

Visible text:

```txt
Terminal 01
En linea
```

Includes:

- avatar/terminal icon,
- green status dot,
- dropdown chevron,
- frosted rounded card.

---

## 5. Top header details

### Screen title

Text:

```txt
Ventas
```

Style:

- Top-left of main area.
- Navy text.
- 28-32 px.
- Semibold/bold.

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

Style:

- Frosted rounded pill.
- Pale blue avatar.
- Deep navy text.
- Subtle border and shadow.

---

## 6. Search row

### Search input

Placeholder:

```txt
Buscar producto por codigo, nombre o SKU...
```

Includes:

- search icon left,
- scan/crop icon right,
- very soft blue focus state.

Visual:

- white/frosted background,
- subtle border,
- rounded rectangle,
- approx. 56px height,
- deep navy placeholder and icon hierarchy.

### Scan button

Text:

```txt
ESCANEAR
```

Includes scan icon and uppercase label.

Style:

- White/frosted button.
- Blue icon and label.
- Soft border.
- Mild shadow.

### More button

Text/icon:

```txt
...
```

Rounded square button, frosted, with navy icon.

---

## 7. Category rail

Visible categories:

| Order | Label | State |
|---:|---|---|
| 1 | Todos | active |
| 2 | Bebidas | default |
| 3 | Snacks | default |
| 4 | Lacteos | default |
| 5 | Abarrotes | default |
| 6 | Limpieza | default |
| 7 | Personal | default |
| 8 | `>` | navigation |

Each category has:

- circular icon button,
- label below,
- enough spacing for touch clarity.

Active `Todos`:

- Blue ring or blue fill.
- White icon when filled.
- Label in blue.
- Soft blue glow.

---

## 8. Product grid

### Layout

- 4 columns.
- 2 rows visible.
- Large cards.
- Cards have rounded corners, white/frosted glass, inner highlight and product shadow.

### Product card anatomy

Each product card includes:

1. Favorite star at top.
2. Large product image.
3. Subtle product shadow or color pedestal.
4. Product name.
5. Price.
6. Stock.
7. Add button.

### Products visible

| Position | Product | Price | Stock | Visual glow |
|---:|---|---:|---:|---|
| 1 | Coca Cola 600 ml | $18.00 | 156 | red soft |
| 2 | Sabritas Original 45 g | $15.00 | 142 | yellow soft |
| 3 | Leche Lala Entera 1 L | $28.50 | 98 | cool white |
| 4 | Agua Ciel 1 L | $16.00 | 83 | blue soft |
| 5 | Nescafe Clasico 200 g | $145.00 | 42 | brown/red soft |
| 6 | Pan Bimbo Blanco Grande | $34.00 | 87 | amber soft |
| 7 | Ace 1 kg | $38.50 | 28 | orange soft |
| 8 | Zucaritas Kellogg's 730 g | $67.00 | 31 | blue soft |

### Notes

- Product image should occupy around half the card height.
- Stock is small and muted.
- Price is stronger than stock.
- Add button is a compact blue action.
- Cards must feel clean, not sterile.

---

## 9. Pagination

Position:

- bottom of product area,
- centered.

Visible controls:

```txt
< 1 2 3 4 5 >
```

Active page `1`:

- Blue fill.
- White text.
- Soft blue shadow.

---

## 10. Cart panel

### Position and style

- Fixed right.
- Tall rounded panel.
- White/frosted surface.
- Subtle blue-gray border.
- Soft shadow.

### Header

Visible text:

```txt
Carrito de venta
4 articulos
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

The total label stays navy. The amount is blue, large and visually dominant.

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
- blue gradient,
- white text,
- strong rounded rectangle,
- controlled blue shadow.

This is the strongest action in the UI.

---

## 14. Secondary action cards

Visible bottom actions:

| Label | Shortcut |
|---|---|
| COTIZACION | F3 |
| GUARDAR | F4 |
| LIMPIAR | F5 |

Each card:

- white/frosted surface,
- icon above,
- uppercase label,
- shortcut below,
- subtle border.

---

## 15. Visual matching priorities

When implementing, match in this order:

1. Overall three-zone composition.
2. Sidebar width and content.
3. Cart width, height and border.
4. Main area position.
5. Search row.
6. Category rail.
7. Product grid dimensions.
8. Product image size and shadow/glow.
9. Total and `COBRAR` hierarchy.
10. Typography and icon polish.

Target: 90-95% perceptual similarity against the white reference.
