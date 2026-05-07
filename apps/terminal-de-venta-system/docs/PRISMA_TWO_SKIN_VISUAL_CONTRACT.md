# PRISMA Two Skin Visual Contract

**Proyecto:** PRISMA POS / Terminal de Venta System
**Alcance:** dos skins visuales para la misma experiencia POS
**Skins canónicos:** `dark` y `light`
**No incluye:** PC Backoffice, Slate, Mobile, rediseño de layout o lógica funcional.

---

## 1. Decisión central

PRISMA POS debe soportar dos skins visuales paralelos:

| Skin | Nombre canónico | Identidad visual | Acento principal |
|---|---|---|---|
| `dark` | PRISMA Dark POS | dark premium glass, cinematic, gold | warm gold |
| `light` | PRISMA Light POS | white/frosted premium, clean, operational | blue primary |

Ambos skins comparten la misma experiencia POS:

```text
Sidebar izquierda + catálogo central + carrito derecho
```

La piel cambia color, profundidad, materiales, foco y atmósfera. No cambia el producto, no cambia el flujo, no cambia el esqueleto. Misma taquería, dos iluminaciones; no menú nuevo inventado por el sobrino.

---

## 2. Fuente de verdad visual

Cada skin tiene su propia referencia visual:

| Skin | Fuente visual que gana |
|---|---|
| `dark` | PRISMA Dark POS reference / screenshot dark |
| `light` | PRISMA Light POS reference / screenshot white |

Regla:

```text
Si el documento y la imagen contradicen, gana la imagen del skin correspondiente.
```

---

## 3. Lo que se comparte

Ambos skins comparten:

- componentes canónicos POS;
- jerarquía de información;
- labels es-MX;
- estructura de pantalla 4:3;
- productos demo;
- carrito;
- totales;
- atajos F2/F3/F4/F5;
- estados de interacción;
- reglas de accesibilidad;
- tamaños base de layout;
- objetivo de similitud 90-95% contra su referencia.

---

## 4. Lo que cambia por skin

| Capa | Dark POS | Light POS |
|---|---|---|
| App background | graphite/black atmosférico | blanco/frío con radial azul suave |
| Panels | dark glass | white/frosted glass |
| Primary accent | gold | blue |
| Active nav | gold glass | blue gradient |
| Active category | gold circle/glow | blue circle/ring/glow |
| Total amount | gold | blue |
| Pay button | gold gradient | blue gradient |
| Text primary | cream/white | navy |
| Product card | dark glass | frosted white |
| Glow | más dramático | más limpio y suave |

---

## 5. Lo que NO cambia por skin

No cambia:

- sidebar;
- navegación;
- búsqueda;
- categorías;
- grid 4x2;
- producto grande;
- carrito fijo derecho;
- cantidades;
- totales;
- `COBRAR` dominante;
- acciones secundarias;
- idioma visible;
- flujo POS.

Si el cambio de skin mueve layout, es bug. Si convierte productos en tabla, es bug. Si desaparece el carrito, bug con sombrero de mariachi.

---

## 6. Componentes canónicos comunes

Ambos skins deben usar el mismo inventario conceptual:

```text
PrismaAppShell
PrismaSidebar
PrismaLogoBlock
PrismaNavItem
TerminalStatusCard
TopActionBar
AdminUserChip
SearchProductInput
ScanButton
RoundIconButton
CategoryRail
CategoryCircleItem
ProductGrid
ProductCard
ProductImageStage
PaginationBar
CartPanel
CartLineItem
QuantityStepper
TotalsSummary
PayButton
SecondaryActionCard
StatusBadge
ShortcutHint
```

Cada componente debe leer tokens visuales. No debe traer colores hardcodeados por skin dentro del JSX salvo casos de producto/glow controlado.

---

## 7. API visual mínima

El skin activo debe expresarse así:

```html
<html data-prisma-skin="dark">
```

ó:

```html
<html data-prisma-skin="light">
```

Opcionalmente se puede conservar compatibilidad legacy:

```html
<html data-theme="prisma-dark">
<html data-theme="prisma-light">
```

Pero la fuente nueva recomendada es:

```text
data-prisma-skin
```

---

## 8. Definition of Done

El sistema de dos skins está listo cuando:

- existe contrato visual de dos skins;
- existe mapa de tokens unificados;
- existe spec de selector;
- componentes usan tokens compartidos;
- dark y light se pueden alternar sin tocar layout;
- dark se parece a su referencia;
- light se parece a su referencia;
- no hay colores primarios hardcodeados en componentes críticos;
- no hay regresión del flujo POS.
