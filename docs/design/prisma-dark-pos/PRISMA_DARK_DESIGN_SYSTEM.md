# PRISMA Dark Design System

**System:** PRISMA Dark POS  
**Mode:** dark premium  
**Purpose:** reusable design rules, tokens and behaviors for building the PRISMA POS screen with high visual fidelity.

---

## 1. Core principles

### 1.1 Premium operativo

The UI must look expensive, but it must still be fast to use. This is a point-of-sale screen, not a museum piece guarded by a confused intern.

### 1.2 Dark with depth

Dark does not mean flat black. Use layers:

- app background,
- glass panels,
- elevated cards,
- inner highlights,
- shadows,
- subtle glow.

### 1.3 Gold means action and focus

Warm gold is used for:

- primary action,
- active navigation,
- active category,
- important total,
- focus state,
- small premium highlights.

Do not paint everything gold. If everything screams, the user hears nothing.

---

## 2. CSS token set

```css
:root {
  --prisma-bg-black: #050608;
  --prisma-bg-deep: #090b10;
  --prisma-bg-main: #0d0f15;
  --prisma-bg-panel: rgba(17, 19, 26, 0.82);
  --prisma-bg-card: rgba(28, 30, 40, 0.74);
  --prisma-bg-card-hover: rgba(36, 38, 50, 0.84);
  --prisma-bg-sidebar: rgba(7, 8, 12, 0.92);

  --prisma-gold-50: #fff4cf;
  --prisma-gold-100: #f8df9b;
  --prisma-gold-200: #f5d183;
  --prisma-gold-300: #e8bd67;
  --prisma-gold-400: #d7ac5b;
  --prisma-gold-500: #bc8d3e;
  --prisma-gold-600: #8b6a32;
  --prisma-gold-700: #5c4624;

  --prisma-text-primary: #f4f1ea;
  --prisma-text-secondary: #b8b5ae;
  --prisma-text-muted: #7e818b;
  --prisma-text-faint: #5f636d;
  --prisma-text-on-gold: #2b2111;

  --prisma-border-soft: rgba(255, 255, 255, 0.08);
  --prisma-border-medium: rgba(255, 255, 255, 0.12);
  --prisma-border-strong: rgba(255, 255, 255, 0.18);
  --prisma-border-gold: rgba(232, 189, 103, 0.55);

  --prisma-online: #3ad17a;
  --prisma-danger: #ff6b5e;
  --prisma-warning: #e8bd67;

  --prisma-radius-xs: 8px;
  --prisma-radius-sm: 10px;
  --prisma-radius-md: 14px;
  --prisma-radius-lg: 18px;
  --prisma-radius-xl: 24px;
  --prisma-radius-pill: 999px;

  --prisma-space-1: 4px;
  --prisma-space-2: 8px;
  --prisma-space-3: 12px;
  --prisma-space-4: 16px;
  --prisma-space-5: 20px;
  --prisma-space-6: 24px;
  --prisma-space-8: 32px;
  --prisma-space-10: 40px;

  --prisma-blur-card: 16px;
  --prisma-blur-panel: 22px;
}
```

---

## 3. Surface system

### App background

```css
.prisma-app-bg {
  background:
    radial-gradient(circle at 48% -6%, rgba(232,189,103,.18), transparent 30%),
    radial-gradient(circle at 26% 100%, rgba(160,40,35,.10), transparent 26%),
    radial-gradient(circle at 76% 92%, rgba(60,90,150,.10), transparent 28%),
    linear-gradient(180deg, #11131a 0%, #08090d 55%, #050608 100%);
}
```

### Glass panel

```css
.prisma-glass-panel {
  background: rgba(17, 19, 26, .76);
  backdrop-filter: blur(22px);
  border: 1px solid rgba(255,255,255,.10);
  box-shadow: 0 24px 80px rgba(0,0,0,.42);
}
```

### Product card

```css
.prisma-product-card {
  background: linear-gradient(180deg, rgba(42,44,56,.78), rgba(20,22,30,.78));
  border: 1px solid rgba(255,255,255,.10);
  border-radius: 16px;
  box-shadow: 0 18px 44px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.06);
}
```

### Active gold surface

```css
.prisma-active-gold {
  background: linear-gradient(180deg, rgba(111,85,42,.48), rgba(29,25,19,.80));
  border: 1px solid rgba(232,189,103,.58);
  box-shadow: 0 0 26px rgba(232,189,103,.26), inset 0 1px 0 rgba(255,255,255,.12);
}
```

---

## 4. Type system

Recommended font stack:

```css
font-family: Inter, "SF Pro Display", "SF Pro Text", Manrope, system-ui, sans-serif;
```

| Token | Size | Line height | Weight | Use |
|---|---:|---:|---:|---|
| `display-sm` | 32px | 40px | 800 | totals |
| `title-lg` | 29px | 36px | 700 | screen title |
| `title-md` | 22px | 30px | 700 | panel title |
| `body-lg` | 18px | 26px | 600 | large buttons |
| `body-md` | 16px | 24px | 500 | nav/product names |
| `body-sm` | 14px | 20px | 500 | metadata |
| `caption` | 12px | 16px | 600 | shortcuts/badges |

Rules:

- Product names max 2 lines.
- Prices are bold and readable.
- Total is the largest number in the cart.
- Avoid pure white for everything. Use hierarchy.

---

## 5. Layout system

Base frame: **1536 x 1024**.

```txt
Sidebar width: 200px
Main left: 235px
Main width: 780px
Cart right margin: 70px
Cart width: 426px
Top margin: 28-30px
```

Product grid:

```txt
Columns: 4
Rows visible: 2
Card width: ~188px
Card height: ~272px
Column gap: 14-16px
Row gap: 18px
```

Touch targets:

| Component | Minimum |
|---|---:|
| Nav item height | 50px |
| Category circle | 54px |
| Search height | 56px |
| Primary CTA height | 58px |
| Quantity stepper height | 36px |

---

## 6. Elevation

| Level | Use | Shadow |
|---|---|---|
| 0 | background | none |
| 1 | nav/card soft | `0 8px 20px rgba(0,0,0,.24)` |
| 2 | product card | `0 18px 44px rgba(0,0,0,.35)` |
| 3 | cart/search | `0 24px 70px rgba(0,0,0,.45)` |
| 4 | gold active/CTA | shadow + gold glow |

---

## 7. Interaction states

### Default

- Glass dark background.
- Soft border.
- Secondary text.

### Hover

- Slight lift: `translateY(-1px)`.
- Border brightens.
- Glow increases slightly.

### Focus

```css
box-shadow:
  0 0 0 2px rgba(232,189,103,.45),
  0 0 0 6px rgba(232,189,103,.10);
```

### Active

- Gold border.
- Gold glow.
- Warmer background.

### Disabled

- Opacity `.45`.
- No glow.
- No hover transform.

---

## 8. Icons

Recommended libraries:

- `lucide-react`
- `phosphor-icons`

Rules:

- Stroke width: 1.75-2 px.
- Nav icon: 22 px.
- Category icon: 24 px.
- Button icon: 18-22 px.
- Active icon: gold.
- Default icon: muted gray.

No cartoon icons. No filled emoji-looking icons. Esto no es menú de lonchería escolar.

---

## 9. Button system

### Primary: `COBRAR`

```css
height: 58px;
border-radius: 13px;
background: linear-gradient(180deg, #f7d88a 0%, #e8bd67 48%, #c89136 100%);
color: var(--prisma-text-on-gold);
font-weight: 800;
letter-spacing: .02em;
box-shadow: 0 0 30px rgba(232,189,103,.38), inset 0 1px 0 rgba(255,255,255,.45);
```

### Secondary glass

```css
height: 54px;
border-radius: 14px;
background: rgba(27, 29, 38, .70);
border: 1px solid rgba(255,255,255,.10);
color: var(--prisma-text-secondary);
```

### Icon circle active

```css
width: 56px;
height: 56px;
border-radius: 999px;
background: radial-gradient(circle at 45% 35%, #f5d183, #8b6a32 70%);
box-shadow: 0 0 28px rgba(232,189,103,.40);
```

---

## 10. Form controls

Search input:

- Height: 56px.
- Radius: 14-16px.
- Left icon: search.
- Right icon: scan.
- Placeholder: `Buscar producto por código, nombre o SKU...`

```css
background: rgba(23,25,34,.72);
border: 1px solid rgba(255,255,255,.11);
backdrop-filter: blur(18px);
```

Quantity stepper:

- Pill background.
- Integrated minus and plus.
- Quantity centered.
- Width: 86-96px.
- Height: 36-38px.

---

## 11. Tailwind extension suggestion

```js
export const prismaTheme = {
  colors: {
    prisma: {
      black: '#050608',
      deep: '#090B10',
      panel: '#11131A',
      card: '#1C1E28',
      gold: '#E8BD67',
      goldSoft: '#D7AC5B',
      goldBright: '#F5D183',
      goldDeep: '#8B6A32',
      text: '#F4F1EA',
      muted: '#7E818B',
      online: '#3AD17A',
      danger: '#FF6B5E'
    }
  },
  borderRadius: {
    prismaSm: '10px',
    prismaMd: '14px',
    prismaLg: '18px',
    prismaXl: '24px'
  },
  boxShadow: {
    prismaCard: '0 18px 44px rgba(0,0,0,.35)',
    prismaPanel: '0 24px 80px rgba(0,0,0,.42)',
    prismaGold: '0 0 30px rgba(232,189,103,.38)'
  }
}
```

---

## 12. Copy rules

Visible language must be **es-MX**.

Correct labels:

- `Ventas`
- `Buscar producto por código, nombre o SKU...`
- `ESCANEAR`
- `Carrito de venta`
- `Subtotal`
- `Impuestos (IVA 16%)`
- `Total`
- `COBRAR`
- `COTIZACIÓN`
- `GUARDAR`
- `LIMPIAR`
- `Terminal 01`
- `En línea`

Avoid English labels like `Checkout`, `Cart`, `Inventory`, `Pay Now`.

---

## 13. Quality gate

A screen follows the design system if:

- dark surfaces have depth,
- gold is warm and controlled,
- cards look premium,
- products are visually dominant,
- sidebar and cart match the reference composition,
- actions are obvious,
- the result does not look like a generic template wearing a fake mustache.
