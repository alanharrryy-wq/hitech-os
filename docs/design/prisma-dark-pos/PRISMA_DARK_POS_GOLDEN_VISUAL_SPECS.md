# PRISMA Dark POS - Golden Visual Specs

**Version:** 1.0  
**Reference:** `negra.jpeg`  
**Goal:** define the exact visual target for a PRISMA dark premium POS interface that must look extremely close to the reference.

## 1. Non-negotiable visual rule

This is not a loose inspiration board. This is the source of truth. The implementation must feel like it was built from the same screen.

Do not turn it into:

- a generic SaaS dashboard,
- a green checkout app,
- a cyberpunk neon panel,
- a flat dark admin template,
- a mobile-first card stack,
- a random POS with gold paint slapped on it like cheap perfume on a bus seat.

## 2. Official visual name

**PRISMA Dark POS**

Recommended document name:

**PRISMA Dark POS - Golden Visual Specs**

## 3. Canvas and aspect ratio

| Property | Value |
|---|---|
| Aspect ratio | **4:3** |
| Reference canvas | **1536 x 1024 px** |
| Orientation | Landscape |
| UI type | Desktop/tablet POS terminal |
| Language | es-MX |
| Visual style | Dark premium glassmorphism with warm gold accents |

## 4. Global composition

The screen has three major zones:

| Zone | Position | Visual role | Approx. share |
|---|---|---|---:|
| Sidebar | Left | Brand, navigation, terminal status | 13% |
| Main sales area | Center | Search, categories, product catalog | 57% |
| Cart panel | Right | Ticket, totals, payment | 30% |

Approximate layout on 1536 x 1024:

| Element | X | Y | W | H |
|---|---:|---:|---:|---:|
| Sidebar | 0 | 0 | 200 | 1024 |
| Main content | 235 | 30 | 780 | 945 |
| Cart panel | 1040 | 96 | 426 | 862 |
| Top controls | 1120 | 28 | 340 | 54 |

Keep the screen spacious. Do not compress it into a cramped web dashboard. This interface should breathe like premium equipment, not like a register with anxiety.

## 5. Mood and visual identity

PRISMA Dark POS should feel:

- premium,
- intelligent,
- operational,
- cinematic,
- tactile,
- serious,
- expensive without being flashy.

The visual language is **dark glass + warm gold + illuminated product catalog**.

It is not “black background and yellow buttons.” That is how civilization collapses one UI at a time.

## 6. Color palette

Approximate colors from the reference:

### Backgrounds

| Token | Hex | Use |
|---|---|---|
| `--bg-black` | `#050608` | deepest background |
| `--bg-deep` | `#090B10` | main app background |
| `--bg-panel` | `#11131A` | sidebar/cart/panels |
| `--bg-card` | `#1C1E28` | product cards |
| `--bg-glass` | `rgba(25,27,36,.70)` | glass surfaces |
| `--bg-glass-strong` | `rgba(30,32,42,.84)` | active panels |

### Golds

| Token | Hex | Use |
|---|---|---|
| `--gold-primary` | `#E8BD67` | main action/accent |
| `--gold-soft` | `#D7AC5B` | borders/icons |
| `--gold-bright` | `#F5D183` | glow/highlight |
| `--gold-deep` | `#8B6A32` | gradients/shadows |
| `--gold-muted` | `#6D552D` | subtle depth |

### Text

| Token | Hex | Use |
|---|---|---|
| `--text-primary` | `#F4F1EA` | main titles |
| `--text-secondary` | `#B8B5AE` | nav labels/body |
| `--text-muted` | `#7E818B` | stock/meta |
| `--text-faint` | `#5F636D` | secondary metadata |
| `--text-on-gold` | `#2B2111` | CTA text |

### States

| State | Color |
|---|---|
| Online | `#3AD17A` |
| Warning | `#E8BD67` |
| Danger | `#FF6B5E` |

## 7. Background atmosphere

The background must not be flat. Use:

- deep black base,
- soft warm radial light near the top center,
- subtle red/blue low reflections,
- slight vignette,
- very light noise/blur.

Conceptual CSS:

```css
background:
  radial-gradient(circle at 48% -6%, rgba(232,189,103,.18), transparent 30%),
  radial-gradient(circle at 26% 100%, rgba(160,40,35,.10), transparent 26%),
  radial-gradient(circle at 76% 92%, rgba(60,90,150,.10), transparent 28%),
  linear-gradient(180deg, #11131a 0%, #08090d 55%, #050608 100%);
```

## 8. Typography

Recommended fonts:

1. Inter
2. SF Pro Display / SF Pro Text
3. Manrope
4. Geist Sans

Scale:

| Use | Size | Weight |
|---|---:|---:|
| Screen title `Ventas` | 28-31 px | 700 |
| Panel title | 19-22 px | 700 |
| Product name | 15-16 px | 600 |
| Product price | 20-22 px | 700 |
| Stock/meta | 13-14 px | 500 |
| Total amount | 29-34 px | 800 |
| CTA `COBRAR` | 16-18 px | 800 |

## 9. Sidebar requirements

Sidebar is fixed left, full height.

Must include:

- PRISMA geometric logo at top,
- text `PRISMA`,
- subtitle `SISTEMA DE GESTIÓN INTELIGENTE`,
- vertical navigation,
- active `Ventas` item in gold,
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
12. Configuración

Active item style:

```css
background: linear-gradient(90deg, rgba(232,189,103,.34), rgba(232,189,103,.13));
border: 1px solid rgba(232,189,103,.60);
box-shadow: 0 0 24px rgba(232,189,103,.22);
color: #f5d183;
```

Bottom card content:

- `Terminal 01`
- `En línea`
- green dot
- user/terminal icon
- chevron

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

`Buscar producto por código, nombre o SKU...`

Categories:

- Todos
- Bebidas
- Snacks
- Lácteos
- Abarrotes
- Limpieza
- Personal
- next arrow

Active category: circular gold icon with glow.

## 11. Product cards

Product cards are the soul of the screen. If they look flat or tiny, the whole thing dies like a taco without salsa.

Each card must include:

- favorite star top,
- large product image,
- pedestal/glow below image,
- product name,
- price,
- stock.

Approximate size:

| Property | Value |
|---|---:|
| Width | 188 px |
| Height | 272 px |
| Radius | 16 px |
| Padding | 16 px |
| Image height | 125-145 px |

Base card CSS:

```css
background: linear-gradient(180deg, rgba(42,44,56,.78), rgba(20,22,30,.78));
border: 1px solid rgba(255,255,255,.10);
border-radius: 16px;
box-shadow: 0 18px 44px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.06);
```

## 12. Product visual treatment

Use product PNGs or well-cut product images.

Each product sits on:

- a subtle circular pedestal,
- a glow matching package color,
- a drop shadow.

Suggested glow:

| Product | Glow |
|---|---|
| Coca Cola | red |
| Sabritas | yellow/gold |
| Leche Lala | cool white |
| Agua Ciel | blue |
| Nescafé | brown/red |
| Bimbo | amber |
| Ace | orange |
| Zucaritas | blue |

## 13. Right cart panel

The cart panel is fixed right, tall, dark glass, with subtle gold border.

Header:

- `Carrito de venta`
- chip `4 artículos`
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

The total must be large and gold.

## 14. Main CTA

Button text:

`COBRAR`

Shortcut:

`F2`

Style:

```css
height: 58px;
border-radius: 13px;
background: linear-gradient(180deg, #f7d88a 0%, #e8bd67 48%, #c89136 100%);
color: #2b2111;
font-weight: 800;
box-shadow: 0 0 30px rgba(232,189,103,.38), inset 0 1px 0 rgba(255,255,255,.45);
```

It must dominate the cart. If it does not dominate, the hierarchy is wrong.

## 15. Secondary actions

Three bottom cards:

| Action | Shortcut |
|---|---|
| COTIZACIÓN | F3 |
| GUARDAR | F4 |
| LIMPIAR | F5 |

Glass dark cards, subtle border, small gold icon.

## 16. Motion

Allowed:

- hover elevation 1-2 px,
- soft gold focus ring,
- 160-220 ms transitions,
- subtle glow changes.

Not allowed:

- bouncing animations,
- casino effects,
- loud particles,
- exaggerated scaling,
- anything that distracts from selling.

## 17. Visual acceptance checklist

- [ ] 4:3 aspect ratio.
- [ ] Sidebar left with PRISMA logo.
- [ ] `Ventas` active in gold.
- [ ] Search row matches reference.
- [ ] Category icons are circular.
- [ ] Grid has 4 columns.
- [ ] Product cards are large and glassy.
- [ ] Product images have glow/pedestal.
- [ ] Cart is fixed right.
- [ ] Total is large and gold.
- [ ] `COBRAR` is the strongest CTA.
- [ ] F2/F3/F4/F5 shortcuts appear.
- [ ] No generic dashboard vibes.

Target similarity: **90-95% perceptual match** against `negra.jpeg`.
