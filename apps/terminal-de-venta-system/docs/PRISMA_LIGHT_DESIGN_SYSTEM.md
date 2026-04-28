# PRISMA Light POS — Design System

## 0. Propósito

Este documento define el sistema visual reutilizable de PRISMA Light POS.

Debe servir para construir componentes consistentes, pantallas nuevas y estados del producto sin que cada dev se invente “su versión bonita”, porque ya sabemos cómo termina eso: cinco botones distintos, tres sombras peleándose y una UI con personalidad de control remoto pirata.

---

## 1. Principios del sistema

### 1.1 Claridad operativa

El POS existe para vender rápido.

Cada decisión visual debe responder:

- ¿ayuda a encontrar producto?
- ¿ayuda a cobrar?
- ¿reduce error?
- ¿se entiende en chinga?

### 1.2 Premium sin estorbar

La UI debe verse cara, pero no debe ponerse mamona.

Debe haber:

- sombras suaves
- superficies limpias
- dorado sobrio
- radios grandes
- jerarquía clara

No debe haber:

- ornamento inútil
- animaciones de circo
- exceso de brillos
- botones disfrazados de joyería barata

### 1.3 Hermandad con Dark

Light y Dark deben compartir:

- layout
- componentes
- navegación
- jerarquía
- flujos

Solo cambia:

- luminosidad
- contraste
- tratamiento de superficies
- intensidad del glow

---

## 2. Tokens de color

### 2.1 Background

```css
--prisma-light-bg-app: #F6F7FA;
--prisma-light-bg-page: #F8FAFC;
--prisma-light-bg-warm: #FBF8F1;
--prisma-light-bg-panel: #FFFFFF;
--prisma-light-bg-panel-soft: #FBFCFE;
--prisma-light-bg-input: #FFFFFF;
--prisma-light-bg-hover: #F4F6FA;
```

### 2.2 Text

```css
--prisma-light-text-primary: #171A20;
--prisma-light-text-secondary: #4E5562;
--prisma-light-text-muted: #8B93A1;
--prisma-light-text-soft: #A8AFBA;
--prisma-light-text-inverse: #FFFFFF;
--prisma-light-text-on-gold: #1B1305;
```

### 2.3 Gold accent

```css
--prisma-gold-50: #FFF8E5;
--prisma-gold-100: #FFF1C8;
--prisma-gold-200: #F6D889;
--prisma-gold-300: #E5B44E;
--prisma-gold-400: #D99A22;
--prisma-gold-500: #B97810;
--prisma-gold-600: #875806;
```

### 2.4 Borders

```css
--prisma-light-border-soft: #E7EAF0;
--prisma-light-border-medium: #D9DFE8;
--prisma-light-border-strong: #C7CEDA;
--prisma-light-border-gold: rgba(217,154,34,.45);
```

### 2.5 Status

```css
--status-success: #19A463;
--status-success-bg: #EAF8F1;

--status-warning: #D99A22;
--status-warning-bg: #FFF4D8;

--status-error: #D94C4C;
--status-error-bg: #FDECEC;

--status-info: #4B7BEC;
--status-info-bg: #EDF3FF;
```

---

## 3. Tokens de sombra

### 3.1 Sombras base

```css
--shadow-xs: 0 4px 12px rgba(20, 26, 38, 0.05);
--shadow-sm: 0 10px 28px rgba(20, 26, 38, 0.07);
--shadow-md: 0 18px 45px rgba(20, 26, 38, 0.09);
--shadow-lg: 0 28px 80px rgba(20, 26, 38, 0.12);
```

### 3.2 Sombras cálidas

```css
--shadow-gold-sm: 0 8px 22px rgba(217,154,34,0.18);
--shadow-gold-md: 0 14px 35px rgba(217,154,34,0.25);
--shadow-gold-lg: 0 18px 48px rgba(217,154,34,0.30);
```

### 3.3 Uso

| Nivel | Uso |
|---|---|
| `xs` | inputs, botones secundarios |
| `sm` | nav active, chips |
| `md` | product cards |
| `lg` | panel carrito / sidebar |
| `gold-md` | botón COBRAR |

---

## 4. Tokens de radio

```css
--radius-xs: 8px;
--radius-sm: 12px;
--radius-md: 16px;
--radius-lg: 22px;
--radius-xl: 28px;
--radius-2xl: 34px;
--radius-pill: 999px;
```

Uso recomendado:

| Elemento | Radio |
|---|---|
| Nav item | 14–18 px |
| Search | 18–22 px |
| Product card | 20–24 px |
| Cart panel | 26–32 px |
| CTA | 14–18 px |
| Avatar / categoría circular | 999 px |

---

## 5. Tokens de spacing

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-7: 28px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
```

Reglas:

- Panel grande: 24–32 px
- Card producto: 18–22 px
- Gap grid: 16–20 px
- Gap columnas: 24 px
- Botones touch: mínimo 44 px de alto

---

## 6. Tipografía

### 6.1 Familia recomendada

Usar una sans moderna:

- Inter
- SF Pro
- Geist
- Plus Jakarta Sans
- Segoe UI como fallback Windows

Stack sugerido:

```css
font-family: Inter, "SF Pro Display", "Segoe UI", system-ui, sans-serif;
```

### 6.2 Escala

| Token | Tamaño | Peso | Uso |
|---|---:|---:|---|
| `display` | 34 px | 700 | título principal si aplica |
| `h1` | 30 px | 700 | `Ventas` |
| `h2` | 22 px | 700 | panel titles |
| `h3` | 18 px | 600 | secciones |
| `body` | 15 px | 400 | texto base |
| `body-sm` | 13 px | 400 | stock, meta |
| `label` | 12 px | 600 | shortcuts, badges |
| `price` | 20 px | 650 | precio producto |
| `total` | 32 px | 700 | monto total |

---

## 7. Componentes base

## 7.1 AppShell

Estructura:

```tsx
<AppShell>
  <Sidebar />
  <SalesWorkspace />
  <CartPanel />
</AppShell>
```

CSS conceptual:

```css
.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 200px minmax(0, 1fr) 430px;
  gap: 24px;
  padding: 12px;
  background:
    radial-gradient(circle at 50% 0%, rgba(217,154,34,.10), transparent 34%),
    linear-gradient(135deg, #F8FAFC, #F4F6FA);
}
```

---

## 7.2 Sidebar

```css
.sidebar {
  background: rgba(255,255,255,.88);
  backdrop-filter: blur(18px);
  border: 1px solid var(--prisma-light-border-soft);
  box-shadow: var(--shadow-lg);
  border-radius: var(--radius-xl);
  padding: 24px 18px;
}
```

### NavItem

```css
.nav-item {
  height: 48px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 14px;
  border-radius: var(--radius-md);
  color: var(--prisma-light-text-secondary);
}

.nav-item.active {
  color: var(--prisma-light-text-on-gold);
  background: linear-gradient(135deg, var(--prisma-gold-100), var(--prisma-gold-200));
  border: 1px solid var(--prisma-light-border-gold);
  box-shadow: var(--shadow-gold-sm);
}
```

---

## 7.3 SearchBar

```css
.search-bar {
  height: 60px;
  border-radius: 20px;
  background: rgba(255,255,255,.92);
  border: 1px solid var(--prisma-light-border-soft);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  padding: 0 20px;
}
```

Estados:

- focus: borde dorado suave
- placeholder: gris tenue
- icon: gris medio

---

## 7.4 ScanButton

```css
.scan-button {
  height: 56px;
  padding: 0 22px;
  border-radius: 18px;
  background: #FFFFFF;
  border: 1px solid var(--prisma-light-border-soft);
  box-shadow: var(--shadow-sm);
  color: var(--prisma-light-text-primary);
}

.scan-button .icon {
  color: var(--prisma-gold-400);
}
```

---

## 7.5 CategoryButton

```css
.category-button {
  display: grid;
  place-items: center;
  gap: 8px;
  color: var(--prisma-light-text-secondary);
}

.category-icon {
  width: 52px;
  height: 52px;
  border-radius: 999px;
  background: #FFFFFF;
  border: 1px solid var(--prisma-light-border-soft);
  box-shadow: var(--shadow-xs);
}

.category-button.active .category-icon {
  border-color: var(--prisma-gold-400);
  color: var(--prisma-gold-500);
  background: linear-gradient(135deg, #FFFFFF, var(--prisma-gold-50));
  box-shadow: var(--shadow-gold-sm);
}
```

---

## 7.6 ProductCard

```css
.product-card {
  min-height: 292px;
  border-radius: 22px;
  background: rgba(255,255,255,.94);
  border: 1px solid var(--prisma-light-border-soft);
  box-shadow: var(--shadow-md);
  padding: 18px 18px 20px;
  transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(217,154,34,.28);
}
```

### ProductImageStage

```css
.product-stage {
  height: 145px;
  display: grid;
  place-items: center;
  position: relative;
}

.product-stage::after {
  content: "";
  position: absolute;
  width: 92px;
  height: 18px;
  bottom: 8px;
  border-radius: 50%;
  background: rgba(20,26,38,.10);
  filter: blur(6px);
}
```

---

## 7.7 CartPanel

```css
.cart-panel {
  background: rgba(255,255,255,.92);
  backdrop-filter: blur(18px);
  border: 1px solid var(--prisma-light-border-soft);
  box-shadow: var(--shadow-lg);
  border-radius: 28px;
  padding: 28px 24px;
}
```

---

## 7.8 CartItem

```css
.cart-item {
  display: grid;
  grid-template-columns: 24px 76px 1fr auto;
  gap: 14px;
  align-items: center;
  padding: 18px 0;
  border-bottom: 1px solid rgba(20,26,38,.08);
}
```

### QuantityStepper

```css
.stepper {
  display: inline-flex;
  align-items: center;
  height: 32px;
  border-radius: 999px;
  background: #FFFFFF;
  border: 1px solid var(--prisma-light-border-soft);
  box-shadow: var(--shadow-xs);
}

.stepper button {
  width: 32px;
  height: 32px;
  border: 0;
  background: transparent;
}
```

---

## 7.9 CheckoutButton

```css
.checkout-button {
  height: 58px;
  width: 100%;
  border: 0;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--prisma-gold-200), var(--prisma-gold-400));
  color: var(--prisma-light-text-on-gold);
  font-weight: 700;
  font-size: 16px;
  box-shadow: var(--shadow-gold-md);
}
```

---

## 8. Estados de componentes

### 8.1 Default

- blanco limpio
- borde suave
- sombra mínima
- texto legible

### 8.2 Hover

- elevación mínima
- borde un poco más cálido
- nada chillón

### 8.3 Focus

```css
outline: 3px solid rgba(217,154,34,.22);
outline-offset: 2px;
```

### 8.4 Disabled

- opacidad 0.5–0.6
- cursor not-allowed
- sin sombra fuerte

### 8.5 Error

- borde rojo suave
- fondo rojo pálido
- texto explicativo, no solo color

---

## 9. Iconografía

Estilo recomendado:

- lineal
- stroke 1.7 a 2 px
- esquinas redondeadas
- misma familia visual
- tamaño base 20–22 px

No mezclar íconos filled, outline y emojis como si fuera menú de fonda con cinco tipografías.

---

## 10. Responsividad

### 10.1 Desktop / landscape

Mantener 3 columnas.

### 10.2 Tablet mediana

Reducir sidebar o hacerlo más compacto.
Mantener carrito visible si hay espacio.

### 10.3 Mobile / narrow

- sidebar colapsable
- cart como drawer
- grid 2 columnas
- CTA fijo inferior opcional

Pero la referencia principal es landscape.

---

## 11. Clase de tema sugerida

```css
.theme-prisma-light {
  color-scheme: light;
  --bg: var(--prisma-light-bg-app);
  --surface: var(--prisma-light-bg-panel);
  --accent: var(--prisma-gold-400);
  --accent-soft: var(--prisma-gold-100);
}
```

---

## 12. Criterios de aceptación

Una implementación cumple el Design System si:

- respeta tokens
- usa dorado como acción principal
- mantiene superficies blancas premium
- conserva radio grande
- conserva sidebar + workspace + cart
- producto y carrito dominan más que métricas
- no parece SaaS genérico
- no parece dark mode lavado con cloro

---

## 13. Mínimo CSS global recomendado

```css
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Inter, "SF Pro Display", "Segoe UI", system-ui, sans-serif;
  background: var(--prisma-light-bg-app);
  color: var(--prisma-light-text-primary);
}

button,
input {
  font: inherit;
}

button {
  cursor: pointer;
}
```
