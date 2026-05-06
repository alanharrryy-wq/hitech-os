# PRISMA Light Design System

**System:** PRISMA Light POS
**Mode:** light premium
**Purpose:** reusable design rules, tokens and behaviors for building the PRISMA white POS screen with high visual fidelity.

---

## 1. Core principles

### 1.1 Premium operativo

The UI must look expensive, but it must still be fast to use. This is a point-of-sale screen, not a museum piece guarded by a confused intern.

### 1.2 Light with depth

Light does not mean flat white. Use layers:

- app background,
- frosted panels,
- elevated cards,
- inner highlights,
- shadows,
- subtle blue glow.

### 1.3 Blue means action and focus

Blue is used for:

- primary action,
- active navigation,
- active category,
- important total,
- focus state,
- scan/add highlights.

Do not paint everything blue. If everything screams, the user hears nothing and the caja line starts looking at you feo.

---

## 2. CSS token set

```css
:root,
[data-theme="prisma-light"] {
  color-scheme: light;

  --prisma-light-bg-app: #f7f9ff;
  --prisma-light-bg-canvas: #ffffff;
  --prisma-light-bg-soft: #eef4ff;
  --prisma-light-bg-frosted: rgba(255, 255, 255, 0.78);
  --prisma-light-bg-card: rgba(255, 255, 255, 0.88);
  --prisma-light-bg-sidebar: rgba(255, 255, 255, 0.82);
  --prisma-light-bg-cart: rgba(255, 255, 255, 0.86);

  --prisma-light-blue-50: #eef4ff;
  --prisma-light-blue-100: #dbe8ff;
  --prisma-light-blue-300: #7da8ff;
  --prisma-light-blue-500: #1557ff;
  --prisma-light-blue-600: #0f46d6;
  --prisma-light-blue-700: #0b38b8;
  --prisma-light-blue-900: #071b5f;

  --prisma-light-text-primary: #10172f;
  --prisma-light-text-secondary: #47506a;
  --prisma-light-text-muted: #7a849c;
  --prisma-light-text-faint: #a8b1c2;
  --prisma-light-text-on-blue: #ffffff;

  --prisma-light-border-soft: #e7ebf5;
  --prisma-light-border-medium: #d7dfef;
  --prisma-light-border-strong: #bdc9dd;
  --prisma-light-border-blue: rgba(21, 87, 255, 0.42);

  --prisma-light-success: #1f8f5f;
  --prisma-light-warning: #b7791f;
  --prisma-light-danger: #c2413b;
  --prisma-light-info: #2563eb;
  --prisma-light-focus-ring: rgba(21, 87, 255, 0.38);

  --prisma-light-radius-xs: 8px;
  --prisma-light-radius-sm: 12px;
  --prisma-light-radius-md: 16px;
  --prisma-light-radius-lg: 22px;
  --prisma-light-radius-xl: 28px;
  --prisma-light-radius-pill: 999px;

  --prisma-light-shadow-xs: 0 5px 14px rgba(20, 26, 38, 0.05);
  --prisma-light-shadow-sm: 0 12px 30px rgba(20, 26, 38, 0.075);
  --prisma-light-shadow-md: 0 20px 48px rgba(20, 26, 38, 0.095);
  --prisma-light-shadow-lg: 0 30px 82px rgba(20, 26, 38, 0.13);
  --prisma-light-shadow-blue: 0 18px 38px rgba(21, 87, 255, 0.26);

  --prisma-light-blue-gradient: linear-gradient(135deg, #1557ff 0%, #0b38b8 100%);
  --prisma-light-frosted-gradient: linear-gradient(145deg, rgba(255,255,255,.92), rgba(243,247,255,.72));

  --prisma-light-font-family: Inter, "SF Pro Display", "SF Pro Text", "Segoe UI", system-ui, sans-serif;
}
```

---

## 3. Surface system

### App background

```css
.prisma-light-app-bg {
  background:
    radial-gradient(circle at 42% -8%, rgba(21,87,255,.08), transparent 34%),
    radial-gradient(circle at 88% 10%, rgba(219,232,255,.58), transparent 28%),
    radial-gradient(circle at 8% 30%, rgba(255,255,255,.86), transparent 28%),
    linear-gradient(180deg, #fbfdff 0%, #f7f9ff 48%, #eef2f7 100%);
}
```

### Frosted panel

```css
.prisma-light-panel {
  background: rgba(255,255,255,.82);
  backdrop-filter: blur(24px) saturate(1.08);
  border: 1px solid #e7ebf5;
  box-shadow: 0 22px 70px rgba(32,45,82,.14);
}
```

### Product card

```css
.prisma-light-product-card {
  background: linear-gradient(180deg, rgba(255,255,255,.95), rgba(248,251,255,.86));
  border: 1px solid #e7ebf5;
  border-radius: 18px;
  box-shadow: 0 18px 44px rgba(20,26,38,.08), inset 0 1px 0 rgba(255,255,255,.9);
}
```

### Active blue surface

```css
.prisma-light-active-blue {
  background: linear-gradient(135deg, #1557ff, #0b38b8);
  color: #fff;
  border: 1px solid rgba(21,87,255,.42);
  box-shadow: 0 18px 38px rgba(21,87,255,.26);
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
| `title-lg` | 30px | 38px | 700 | screen title |
| `title-md` | 22px | 30px | 700 | panel title |
| `body-lg` | 18px | 26px | 600 | large buttons |
| `body-md` | 16px | 24px | 500 | nav/product names |
| `body-sm` | 14px | 20px | 500 | metadata |
| `caption` | 12px | 16px | 600 | shortcuts/badges |

Rules:

- Product names max 2 lines.
- Prices are bold and readable.
- Total is the largest number in the cart.
- Avoid low-contrast gray for operational text.

---

## 5. Layout system

Base frame: 1536 x 1024.

```txt
Sidebar width: 220px
Main left: 254px
Main width: 820px
Cart right margin: 16-32px
Cart width: 420px
Top margin: 28-32px
```

Product grid:

```txt
Columns: 4
Rows visible: 2
Card width: ~194px
Card height: ~300px
Column gap: 14-16px
Row gap: 16-18px
```

Touch targets:

| Component | Minimum |
|---|---:|
| Nav item height | 52px |
| Category circle | 56px |
| Search height | 56px |
| Primary CTA height | 58px |
| Quantity stepper height | 36px |

---

## 6. Interaction states

### Default

- Frosted white background.
- Soft border.
- Navy/gray text.

### Hover

- Slight lift: `translateY(-1px)`.
- Border brightens.
- Shadow increases slightly.

### Focus

```css
box-shadow:
  0 0 0 3px rgba(21,87,255,.22),
  0 0 0 6px rgba(21,87,255,.08);
```

### Active

- Blue fill.
- White text.
- Soft blue shadow.

### Disabled

- Opacity `.45`.
- No hover transform.

---

## 7. Button system

### Primary: `COBRAR`

```css
height: 58px;
border-radius: 14px;
background: linear-gradient(135deg, #1557ff 0%, #0b38b8 100%);
color: #ffffff;
font-weight: 800;
letter-spacing: .02em;
box-shadow: 0 18px 38px rgba(21,87,255,.26), inset 0 1px 0 rgba(255,255,255,.25);
```

### Secondary frosted

```css
height: 54px;
border-radius: 14px;
background: rgba(255,255,255,.78);
border: 1px solid #e7ebf5;
color: #10172f;
```

---

## 8. Form controls

Search input:

- Height: 56px.
- Radius: 16px.
- Left icon: search.
- Right icon: scan.
- Placeholder: `Buscar producto por codigo, nombre o SKU...`

```css
background: rgba(255,255,255,.86);
border: 1px solid #e7ebf5;
box-shadow: 0 18px 42px rgba(32,45,82,.10);
backdrop-filter: blur(18px);
```

Quantity stepper:

- Pill background.
- Integrated minus and plus.
- Quantity centered.
- Width: 86-100px.
- Height: 36-38px.

---

## 9. Quality gate

A screen follows the design system if:

- light surfaces have depth,
- blue is controlled and reserved for action/focus,
- cards look premium,
- products are visually dominant,
- sidebar and cart match the reference composition,
- actions are obvious,
- the result does not look like a generic fintech template wearing a PRISMA sticker.
