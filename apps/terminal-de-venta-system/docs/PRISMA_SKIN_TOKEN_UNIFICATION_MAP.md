# PRISMA Skin Token Unification Map

**Propósito:** unificar tokens para que PRISMA Dark POS y PRISMA Light POS compartan componentes sin duplicar UI ni hardcodear colores.

---

## 1. Regla madre

Los componentes POS no deben preguntar:

```ts
if (skin === "dark") useGoldElseBlue()
```

Los componentes deben consumir tokens semánticos:

```css
color: var(--prisma-action-primary);
background: var(--prisma-surface-panel);
box-shadow: var(--prisma-shadow-primary);
```

Luego cada skin define el valor real.

---

## 2. Tokens semánticos compartidos

Estos tokens deben existir para ambos skins:

```css
--prisma-bg-app
--prisma-bg-canvas
--prisma-surface-sidebar
--prisma-surface-panel
--prisma-surface-card
--prisma-surface-cart
--prisma-surface-input

--prisma-text-primary
--prisma-text-secondary
--prisma-text-muted
--prisma-text-faint
--prisma-text-on-primary

--prisma-action-primary
--prisma-action-primary-hover
--prisma-action-primary-deep
--prisma-action-primary-soft
--prisma-action-primary-ring

--prisma-border-soft
--prisma-border-medium
--prisma-border-primary

--prisma-shadow-xs
--prisma-shadow-sm
--prisma-shadow-md
--prisma-shadow-lg
--prisma-shadow-primary

--prisma-radius-sm
--prisma-radius-md
--prisma-radius-lg
--prisma-radius-xl
--prisma-radius-pill

--prisma-state-success
--prisma-state-warning
--prisma-state-danger
--prisma-state-info
```

---

## 3. Mapping Dark POS

```css
html[data-prisma-skin="dark"] {
  color-scheme: dark;

  --prisma-bg-app: #050608;
  --prisma-bg-canvas: #090b10;
  --prisma-surface-sidebar: rgba(7, 8, 12, 0.92);
  --prisma-surface-panel: rgba(17, 19, 26, 0.82);
  --prisma-surface-card: rgba(28, 30, 40, 0.74);
  --prisma-surface-cart: rgba(15, 16, 22, 0.78);
  --prisma-surface-input: rgba(23, 25, 34, 0.72);

  --prisma-text-primary: #f4f1ea;
  --prisma-text-secondary: #b8b5ae;
  --prisma-text-muted: #7e818b;
  --prisma-text-faint: #5f636d;
  --prisma-text-on-primary: #2b2111;

  --prisma-action-primary: #e8bd67;
  --prisma-action-primary-hover: #f5d183;
  --prisma-action-primary-deep: #8b6a32;
  --prisma-action-primary-soft: rgba(232, 189, 103, 0.14);
  --prisma-action-primary-ring: rgba(232, 189, 103, 0.45);

  --prisma-border-soft: rgba(255, 255, 255, 0.08);
  --prisma-border-medium: rgba(255, 255, 255, 0.12);
  --prisma-border-primary: rgba(232, 189, 103, 0.55);

  --prisma-shadow-xs: 0 8px 20px rgba(0, 0, 0, 0.24);
  --prisma-shadow-sm: 0 18px 44px rgba(0, 0, 0, 0.35);
  --prisma-shadow-md: 0 24px 70px rgba(0, 0, 0, 0.45);
  --prisma-shadow-lg: 0 24px 90px rgba(0, 0, 0, 0.50);
  --prisma-shadow-primary: 0 0 30px rgba(232, 189, 103, 0.38);

  --prisma-state-success: #3ad17a;
  --prisma-state-warning: #e8bd67;
  --prisma-state-danger: #ff6b5e;
  --prisma-state-info: #79a8ff;
}
```

---

## 4. Mapping Light POS

```css
html[data-prisma-skin="light"] {
  color-scheme: light;

  --prisma-bg-app: #f7f9ff;
  --prisma-bg-canvas: #ffffff;
  --prisma-surface-sidebar: rgba(255, 255, 255, 0.82);
  --prisma-surface-panel: rgba(255, 255, 255, 0.82);
  --prisma-surface-card: rgba(255, 255, 255, 0.88);
  --prisma-surface-cart: rgba(255, 255, 255, 0.86);
  --prisma-surface-input: rgba(255, 255, 255, 0.86);

  --prisma-text-primary: #10172f;
  --prisma-text-secondary: #47506a;
  --prisma-text-muted: #7a849c;
  --prisma-text-faint: #a8b1c2;
  --prisma-text-on-primary: #ffffff;

  --prisma-action-primary: #1557ff;
  --prisma-action-primary-hover: #7da8ff;
  --prisma-action-primary-deep: #0b38b8;
  --prisma-action-primary-soft: rgba(21, 87, 255, 0.10);
  --prisma-action-primary-ring: rgba(21, 87, 255, 0.38);

  --prisma-border-soft: #e7ebf5;
  --prisma-border-medium: #d7dfef;
  --prisma-border-primary: rgba(21, 87, 255, 0.42);

  --prisma-shadow-xs: 0 5px 14px rgba(20, 26, 38, 0.05);
  --prisma-shadow-sm: 0 12px 30px rgba(20, 26, 38, 0.075);
  --prisma-shadow-md: 0 20px 48px rgba(20, 26, 38, 0.095);
  --prisma-shadow-lg: 0 30px 82px rgba(20, 26, 38, 0.13);
  --prisma-shadow-primary: 0 18px 38px rgba(21, 87, 255, 0.26);

  --prisma-state-success: #1f8f5f;
  --prisma-state-warning: #b7791f;
  --prisma-state-danger: #c2413b;
  --prisma-state-info: #2563eb;
}
```

---

## 5. Tokens estructurales compartidos

Estos no deben cambiar por skin salvo justificación visual fuerte:

```css
:root {
  --prisma-radius-xs: 8px;
  --prisma-radius-sm: 12px;
  --prisma-radius-md: 16px;
  --prisma-radius-lg: 22px;
  --prisma-radius-xl: 28px;
  --prisma-radius-pill: 999px;

  --prisma-font-family: Inter, "SF Pro Display", "SF Pro Text", "Segoe UI", system-ui, sans-serif;

  --prisma-sidebar-width: 220px;
  --prisma-cart-width: 420px;
  --prisma-search-height: 56px;
  --prisma-pay-button-height: 58px;
  --prisma-product-card-radius: 18px;
}
```

---

## 6. Legacy token mapping

Si el repo ya usa tokens `--prisma-light-*` o `--prisma-gold-*`, no borrarlos de golpe. Mapearlos hacia tokens semánticos:

```css
html[data-prisma-skin="light"] {
  --prisma-light-blue-500: var(--prisma-action-primary);
  --prisma-light-bg-card: var(--prisma-surface-card);
}

html[data-prisma-skin="dark"] {
  --prisma-gold-300: var(--prisma-action-primary);
  --prisma-bg-card: var(--prisma-surface-card);
}
```

---

## 7. Regla anti-cochinero

Prohibido en componentes base:

```css
background: #1557ff;
background: #e8bd67;
color: white;
border: 1px solid rgba(...);
```

Permitido:

```css
background: var(--prisma-action-primary);
color: var(--prisma-text-on-primary);
border: 1px solid var(--prisma-border-primary);
```

Los colores viven en el skin. El componente vive feliz, sin saber si hoy le tocó turno nocturno o diurno.
