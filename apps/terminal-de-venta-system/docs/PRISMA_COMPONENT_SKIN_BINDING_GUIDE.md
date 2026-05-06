# PRISMA Component Skin Binding Guide

**Propósito:** explicar cómo deben consumir tokens los componentes POS para soportar Dark y Light sin duplicar UI.

---

## 1. Regla central

Cada componente POS debe tener una sola estructura y dos skins por tokens.

No hacer:

```tsx
return skin === "dark" ? <DarkProductCard /> : <LightProductCard />
```

Hacer:

```tsx
return <ProductCard data-prisma-component="ProductCard" />
```

Y resolver visualmente por CSS:

```css
[data-prisma-component="ProductCard"] {
  background: var(--prisma-surface-card);
  border: 1px solid var(--prisma-border-soft);
  box-shadow: var(--prisma-shadow-sm);
}
```

---

## 2. Binding por componente

| Componente | Tokens principales |
|---|---|
| `PrismaAppShell` | `--prisma-bg-app`, `--prisma-font-family` |
| `PrismaSidebar` | `--prisma-surface-sidebar`, `--prisma-border-soft` |
| `PrismaNavItem` | `--prisma-action-primary`, `--prisma-text-on-primary`, `--prisma-shadow-primary` |
| `SearchProductInput` | `--prisma-surface-input`, `--prisma-border-soft`, `--prisma-action-primary-ring` |
| `ScanButton` | `--prisma-action-primary`, `--prisma-surface-panel` |
| `CategoryCircleItem` | `--prisma-action-primary`, `--prisma-action-primary-soft`, `--prisma-shadow-primary` |
| `ProductCard` | `--prisma-surface-card`, `--prisma-border-soft`, `--prisma-shadow-sm` |
| `CartPanel` | `--prisma-surface-cart`, `--prisma-border-soft`, `--prisma-shadow-lg` |
| `CartLineItem` | `--prisma-border-soft`, `--prisma-text-primary`, `--prisma-text-secondary` |
| `QuantityStepper` | `--prisma-surface-input`, `--prisma-border-soft`, `--prisma-action-primary` |
| `TotalsSummary` | `--prisma-text-primary`, `--prisma-action-primary` |
| `PayButton` | `--prisma-action-primary`, `--prisma-action-primary-deep`, `--prisma-text-on-primary`, `--prisma-shadow-primary` |
| `SecondaryActionCard` | `--prisma-surface-panel`, `--prisma-border-soft`, `--prisma-text-secondary` |

---

## 3. Ejemplo: PayButton

```css
[data-prisma-component="PayButton"] {
  height: var(--prisma-pay-button-height);
  border-radius: var(--prisma-radius-md);
  color: var(--prisma-text-on-primary);
  border: 1px solid var(--prisma-border-primary);
  box-shadow: var(--prisma-shadow-primary), inset 0 1px 0 rgba(255,255,255,.22);
  background: linear-gradient(
    135deg,
    var(--prisma-action-primary),
    var(--prisma-action-primary-deep)
  );
}
```

Resultado:

- Dark: botón gold.
- Light: botón blue.

Mismo componente. Cero drama.

---

## 4. Ejemplo: Nav activo

```css
[data-prisma-component="PrismaNavItem"][data-active="true"] {
  color: var(--prisma-text-on-primary);
  border-color: var(--prisma-border-primary);
  background: linear-gradient(
    135deg,
    var(--prisma-action-primary),
    var(--prisma-action-primary-deep)
  );
  box-shadow: var(--prisma-shadow-primary);
}
```

Si Dark necesita que el texto activo sea gold/cream y no dark-on-gold, se permite override scoped:

```css
html[data-prisma-skin="dark"] [data-prisma-component="PrismaNavItem"][data-active="true"] {
  color: var(--prisma-action-primary-hover);
  background: var(--prisma-action-primary-soft);
}
```

Regla: los overrides por skin son permitidos, pero deben ser pequeños y scoping exacto. Nada de agarrar `button {}` y rezarle al santo del CSS.

---

## 5. Product glow

El glow de producto puede seguir siendo por producto, no por skin. Pero la intensidad sí cambia:

```css
html[data-prisma-skin="dark"] {
  --prisma-product-glow-opacity: .72;
  --prisma-product-glow-blur: 8px;
}

html[data-prisma-skin="light"] {
  --prisma-product-glow-opacity: .34;
  --prisma-product-glow-blur: 10px;
}
```

---

## 6. Prohibiciones

- No duplicar componente por skin salvo necesidad extrema.
- No meter layout dentro de skin.
- No cambiar labels por skin.
- No cambiar productos demo por skin.
- No usar `green` como checkout primary.
- No ocultar shortcuts.
- No romper es-MX.
- No usar tablas en ProductGrid.

---

## 7. Checklist de migración de componente

Para cada componente:

- [ ] usa `data-prisma-component`;
- [ ] no tiene color primario hardcodeado;
- [ ] usa tokens semánticos;
- [ ] se ve correcto en dark;
- [ ] se ve correcto en light;
- [ ] no mueve layout;
- [ ] estados hover/focus existen;
- [ ] accesibilidad mínima preservada.
