# PRISMA Light POS - Golden Visual Specs

**Version:** 1.0
**Reference:** white PRISMA POS screenshot
**Goal:** define the exact visual target for a PRISMA light premium POS interface that must look extremely close to the reference.

---

## 1. Non-negotiable visual rule

This is not a loose inspiration board. This is the source of truth for the white operational POS visual skin.

Do not turn it into:

- a generic SaaS dashboard,
- a green checkout app,
- a dark dashboard with the lights turned on,
- a flat white admin template,
- a mobile-first card stack,
- a random POS with blue paint slapped on it like cheap perfume on a bus seat.

---

## 2. Official visual name

**PRISMA Light POS**

Recommended document name:

**PRISMA Light POS - Golden Visual Specs**

---

## 3. Canvas and aspect ratio

| Property | Value |
|---|---|
| Aspect ratio | 4:3 |
| Reference canvas | 1536 x 1024 px |
| Orientation | Landscape |
| UI type | Desktop/tablet POS terminal |
| Language | es-MX |
| Visual style | Light premium frosted POS with blue operational accents |

---

## 4. Global composition

The screen has three major zones:

| Zone | Position | Visual role | Approx. share |
|---|---|---|---:|
| Sidebar | Left | Brand, navigation, terminal status | 14% |
| Main sales area | Center | Search, categories, product catalog | 57% |
| Cart panel | Right | Ticket, totals, payment | 29% |

Approximate layout on 1536 x 1024:

| Element | X | Y | W | H |
|---|---:|---:|---:|---:|
| Sidebar | 0 | 0 | 220 | 1024 |
| Main content | 254 | 32 | 820 | 940 |
| Cart panel | 1098 | 100 | 420 | 860 |
| Top controls | 1170 | 28 | 340 | 54 |

Keep the screen spacious. Do not compress it into a cramped web dashboard. This interface should breathe like premium equipment, not like a register with anxiety.

---

## 5. Mood and visual identity

PRISMA Light POS should feel:

- premium,
- clean,
- operational,
- bright,
- tactile,
- serious,
- modern without being generic.

The visual language is **white frosted glass + deep navy text + blue primary action + realistic product catalog**.

It is not "white background and blue buttons." That is how civilization collapses one UI at a time.

---

## 6. Color palette

### Backgrounds

| Token | Hex | Use |
|---|---|---|
| `--bg-app` | `#f7f9ff` | main app background |
| `--bg-canvas` | `#ffffff` | base canvas |
| `--bg-soft` | `#eef4ff` | soft blue panels |
| `--bg-panel` | `rgba(255,255,255,.82)` | sidebar/cart/panels |
| `--bg-card` | `rgba(255,255,255,.88)` | product cards |
| `--bg-frosted` | `rgba(255,255,255,.72)` | glass surfaces |

### Blues

| Token | Hex | Use |
|---|---|---|
| `--blue-primary` | `#1557ff` | main action/accent |
| `--blue-deep` | `#0b38b8` | gradients/shadows |
| `--blue-soft` | `#dbe8ff` | selected soft surfaces |
| `--blue-ring` | `rgba(21,87,255,.38)` | focus ring |

### Text

| Token | Hex | Use |
|---|---|---|
| `--text-primary` | `#10172f` | main titles |
| `--text-secondary` | `#47506a` | nav labels/body |
| `--text-muted` | `#7a849c` | stock/meta |
| `--text-faint` | `#a8b1c2` | secondary metadata |
| `--text-on-blue` | `#ffffff` | CTA text |

### States

| State | Color |
|---|---|
| Online | `#1f8f5f` |
| Warning | `#b7791f` |
| Danger | `#c2413b` |
| Info | `#2563eb` |

---

## 7. Background atmosphere

The background must not be flat. Use:

- white base,
- soft blue radial light near the top,
- subtle cool reflections,
- mild vignette,
- almost invisible texture if needed.

Conceptual CSS:

```css
background:
  radial-gradient(circle at 42% -8%, rgba(21,87,255,.08), transparent 34%),
  radial-gradient(circle at 88% 10%, rgba(219,232,255,.58), transparent 28%),
  radial-gradient(circle at 8% 30%, rgba(255,255,255,.86), transparent 28%),
  linear-gradient(180deg, #fbfdff 0%, #f7f9ff 48%, #eef2f7 100%);
```

---

## 8. Typography

Recommended fonts:

1. Inter
2. SF Pro Display / SF Pro Text
3. Manrope
4. Geist Sans

Scale:

| Use | Size | Weight |
|---|---:|---:|
| Screen title `Ventas` | 28-32 px | 700 |
| Panel title | 19-22 px | 700 |
| Product name | 15-16 px | 600 |
| Product price | 20-22 px | 700 |
| Stock/meta | 13-14 px | 500 |
| Total amount | 29-34 px | 800 |
| CTA `COBRAR` | 16-18 px | 800 |

---

## 9. Sidebar requirements

Sidebar is fixed left, full height.

Must include:

- PRISMA geometric logo at top,
- text `PRISMA`,
- subtitle `SISTEMA DE GESTION INTELIGENTE`,
- vertical navigation,
- active `Ventas` item in blue,
- bottom terminal card.

Navigation order:

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

Active item style:

```css
background: linear-gradient(135deg, #1557ff, #0b38b8);
box-shadow: 0 18px 38px rgba(21,87,255,.26);
color: #ffffff;
```

---

## 10. Main sales area

Must include:

- title `Ventas`,
- large search input,
- `ESCANEAR` button,
- more options button,
- circular category rail,
- 4-column product grid,
- pagination.

Search placeholder:

`Buscar producto por codigo, nombre o SKU...`

Categories:

- Todos
- Bebidas
- Snacks
- Lacteos
- Abarrotes
- Limpieza
- Personal
- next arrow

Active category: circular blue icon with glow or ring.

---

## 11. Product cards

Product cards are the soul of the screen. If they look flat or tiny, the whole thing dies like a taco without salsa.

Each card must include:

- favorite star top,
- large product image,
- pedestal/shadow below image,
- product name,
- price,
- stock,
- add button.

Approximate size:

| Property | Value |
|---|---:|
| Width | 194 px |
| Height | 300 px |
| Radius | 18 px |
| Padding | 16 px |
| Image height | 125-150 px |

Base card CSS:

```css
background: linear-gradient(180deg, rgba(255,255,255,.95), rgba(248,251,255,.86));
border: 1px solid #e7ebf5;
border-radius: 18px;
box-shadow: 0 18px 44px rgba(20,26,38,.08), inset 0 1px 0 rgba(255,255,255,.9);
```

---

## 12. Right cart panel

The cart panel is fixed right, tall, frosted white, with subtle blue-gray border.

Header:

- `Carrito de venta`
- chip `4 articulos`
- trash icon

Each line item:

- index circle,
- product thumbnail,
- name,
- unit price,
- quantity stepper `- n +`,
- line total,
- remove `x`.

Totals:

- `Subtotal` `$113.50`
- `Impuestos (IVA 16%)` `$18.16`
- `Total` `$131.66`

The total amount must be large and blue.

---

## 13. Main CTA

Button text:

`COBRAR`

Shortcut:

`F2`

Style:

```css
height: 58px;
border-radius: 14px;
background: linear-gradient(135deg, #1557ff 0%, #0b38b8 100%);
color: #ffffff;
font-weight: 800;
box-shadow: 0 18px 38px rgba(21,87,255,.26), inset 0 1px 0 rgba(255,255,255,.25);
```

It must dominate the cart. If it does not dominate, the hierarchy is wrong.

---

## 14. Secondary actions

Three bottom cards:

| Action | Shortcut |
|---|---|
| COTIZACION | F3 |
| GUARDAR | F4 |
| LIMPIAR | F5 |

Frosted white cards, subtle border, small navy/blue icon.

---

## 15. Motion

Allowed:

- hover elevation 1-2 px,
- soft blue focus ring,
- 160-220 ms transitions,
- subtle shadow changes.

Not allowed:

- bouncing animations,
- casino effects,
- loud particles,
- exaggerated scaling,
- anything that distracts from selling.

---

## 16. Visual acceptance checklist

- [ ] 4:3 aspect ratio.
- [ ] Sidebar left with PRISMA logo.
- [ ] `Ventas` active in blue.
- [ ] Search row matches reference.
- [ ] Category icons are circular.
- [ ] Grid has 4 columns.
- [ ] Product cards are large and frosted.
- [ ] Product images have shadow/pedestal.
- [ ] Cart is fixed right.
- [ ] Total is large and blue.
- [ ] `COBRAR` is the strongest CTA.
- [ ] F2/F3/F4/F5 shortcuts appear.
- [ ] No generic dashboard vibes.

Target similarity: 90-95% perceptual match against the white reference.
