# PRISMA Light POS — High-Fidelity Reference Notes

## 0. Propósito

Este archivo describe la referencia visual final de la versión blanca / Light para que otro ChatGPT, Codex o un dev pueda implementarla con alta similitud.

Este documento debe leerse junto con:

- `PRISMA_LIGHT_POS_GOLDEN_VISUAL_SPECS.md`
- `PRISMA_LIGHT_DESIGN_SYSTEM.md`
- `PRISMA_LIGHT_UI_KIT.md`
- `PRISMA_LIGHT_VISUAL_GUIDELINES.md`

---

## 1. Descripción general de la referencia

La pantalla Light muestra una terminal POS llamada PRISMA en modo claro.

La composición tiene:

- sidebar izquierda blanca
- logo PRISMA grande arriba
- navegación vertical
- terminal status abajo
- área central titulada `Ventas`
- buscador ancho
- botón `ESCANEAR`
- fila de categorías con iconos circulares
- grid de productos en cards blancas
- productos con imagen grande y pedestal
- paginación inferior
- carrito derecho blanco
- lista de productos del ticket
- controles de cantidad
- subtotal, impuestos y total
- botón dorado `COBRAR`
- acciones secundarias debajo

Debe ser casi una traducción Light de la versión Dark original.

---

## 2. Mapa visual textual

```text
┌────────────────────┬─────────────────────────────────────────────────────┬──────────────────────────────┐
│ PRISMA             │ Ventas                                              │ usuario / top controls       │
│                    │ ┌─────────────────────────────┐ ┌───────────────┐   │                              │
│ [Ventas activo]    │ │ Buscar producto...          │ │ ESCANEAR      │   │ Carrito de venta             │
│ Dashboard          │ └─────────────────────────────┘ └───────────────┘   │ 4 artículos                  │
│ Inventario         │                                                     │                              │
│ Clientes           │ [Todos] [Bebidas] [Snacks] [Lácteos] ...            │ 1 Coca Cola                  │
│ Productos          │                                                     │ 2 Sabritas                   │
│ Compras            │ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │ 3 Leche                      │
│ Caja               │ │ Coca   │ │ Sabri  │ │ Leche  │ │ Agua   │        │ 4 Pan                        │
│ Reportes           │ │ $18    │ │ $15    │ │ $28.5  │ │ $16    │        │                              │
│ ...                │ └────────┘ └────────┘ └────────┘ └────────┘        │ Subtotal                     │
│                    │ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │ Impuestos                    │
│ Terminal 01        │ │ Café   │ │ Pan    │ │ Ace    │ │ Zucar  │        │ Total $131.66                │
│ En línea           │ └────────┘ └────────┘ └────────┘ └────────┘        │ [ COBRAR             F2 ]    │
└────────────────────┴─────────────────────────────────────────────────────┴──────────────────────────────┘
```

---

## 3. Sidebar reference

### Visual

- panel vertical blanco
- ocupa todo el alto con márgenes pequeños
- esquinas redondeadas
- sombra suave
- logo arriba centrado
- navegación con iconos lineales

### Active item

`Ventas` activo:

- fondo dorado suave
- icono carrito dorado
- texto oscuro
- glow cálido

### Bottom card

Terminal:

```text
Terminal 01
En línea
```

Con:

- icono usuario
- punto verde
- dropdown

---

## 4. Central area reference

### Title

```text
Ventas
```

Debe estar arriba, fuerte, negro.

### Search row

Elementos:

1. Search input grande
2. Scan button
3. Options button

Search:

```text
Buscar producto por código, nombre o SKU...
```

Scan:

```text
ESCANEAR
```

Options:

```text
...
```

---

## 5. Category row reference

Categorías visibles:

- Todos
- Bebidas
- Snacks
- Lácteos
- Abarrotes
- Limpieza
- Personal

Cada una:

- icono circular arriba
- label abajo
- activo `Todos` con borde dorado

Debe haber un botón de avance a la derecha si hay más categorías.

---

## 6. Product grid reference

### Productos visibles recomendados

Fila 1:

1. Coca Cola 600 ml — `$18.00` — `Stock: 156`
2. Sabritas Original 45 g — `$15.00` — `Stock: 142`
3. Leche Lala Entera 1 L — `$28.50` — `Stock: 98`
4. Agua Ciel 1 L — `$16.00` — `Stock: 83`

Fila 2:

5. Nescafé Clásico 200 g — `$145.00` — `Stock: 42`
6. Pan Bimbo Blanco Grande — `$34.00` — `Stock: 87`
7. Ace 1 kg — `$38.50` — `Stock: 28`
8. Zucaritas Kellogg's 730 g — `$67.00` — `Stock: 31`

### Card visual

Cada card:

- superficie blanca
- borde gris tenue
- radio grande
- sombra suave
- producto centrado
- pedestal elíptico
- favorito arriba
- nombre abajo
- precio
- stock

### Imagen

Debe verse grande, limpia, protagonista.

No usar miniaturas pegadas al borde.
No meter fondos sucios.

---

## 7. Paginación reference

Abajo del grid:

```text
<  1  2  3  4  5  >
```

Página 1 activa:

- borde dorado
- fondo blanco cálido
- texto oscuro

---

## 8. Cart panel reference

### Header

```text
Carrito de venta            4 artículos   [trash]
```

### Items

#### Item 1

```text
1
Coca Cola 600 ml
$18.00
[- 2 +]
$36.00
```

#### Item 2

```text
2
Sabritas Original 45 g
$15.00
[- 1 +]
$15.00
```

#### Item 3

```text
3
Leche Lala Entera 1 L
$28.50
[- 1 +]
$28.50
```

#### Item 4

```text
4
Pan Bimbo Blanco Grande
$34.00
[- 1 +]
$34.00
```

### Reglas

- miniatura en caja blanca pequeña
- número en círculo dorado/outline
- X a la derecha para remover
- separador suave entre items
- stepper visible

---

## 9. Totals reference

```text
Subtotal                  $113.50
Impuestos (IVA 16%)        $18.16

Total                     $131.66
```

Total:

- label grande
- monto dorado
- alineado derecha
- mucho más fuerte que subtotal

---

## 10. Checkout action reference

Botón:

```text
COBRAR                                  F2
```

Visual:

- fondo dorado gradiente
- texto negro/dorado oscuro
- radio 16 px
- sombra cálida
- alto aprox. 58 px
- ancho completo

---

## 11. Secondary actions reference

Tres botones:

```text
COTIZACIÓN   F3
GUARDAR      F4
LIMPIAR      F5
```

Cada uno:

- card blanca
- borde suave
- icono dorado
- label uppercase
- shortcut debajo
- menor peso visual que COBRAR

---

## 12. Top right reference

Controles:

- icono sol
- campana con badge dorado `3`
- user menu pill

User menu:

```text
AR
Administrador
Sucursal Centro
```

---

## 13. Prompt para otro ChatGPT o generador de imagen

```text
Create a high-fidelity light-mode PRISMA POS interface.

It must be extremely similar to the PRISMA dark POS reference, but translated into a premium white/light theme.

Use a 3-column layout:
left sidebar with PRISMA logo and navigation,
center sales workspace with search, scan button, category icons, and product cards,
right checkout cart with ticket items, quantity steppers, totals, and a large COBRAR button.

Visual style:
white and warm light gray background,
soft glass-like panels,
large rounded cards,
warm gold accents,
premium shadows,
product images large and centered on subtle pedestals.

Do not make it a generic dashboard.
Do not remove the right cart.
Do not use blue as the main accent.
Do not make it flat white.
Keep the gold PRISMA identity and POS workflow.
```

---

## 14. Prompt para Codex

```text
Implement the PRISMA Light POS UI from the Golden Visual Specs pack.

Create a high-fidelity React/Next.js interface that matches the reference layout:
- fixed left sidebar
- center product sales workspace
- persistent right checkout panel

Use the light PRISMA design system:
- warm white / gray background
- white elevated cards
- gold active states and checkout button
- large rounded corners
- soft shadows
- product cards with image stage
- category circular buttons
- cart item rows with quantity steppers
- total summary and COBRAR CTA

Do not implement a generic dashboard or table-heavy admin view.
Prioritize visual fidelity over extra features.
Use Spanish labels exactly where specified.
```

---

## 15. Anti-prompts

No hacer:

```text
dashboard analytics
blue SaaS interface
minimal flat white app
top navigation only
no cart panel
generic ecommerce grid
dark mode
neon UI
mobile-only checkout
spreadsheet POS
```

---

## 16. Criterio final

La referencia Light está correcta si al verla se entiende:

> “Es la misma PRISMA terminal de venta, pero en modo blanco premium”.

Si parece otra app, falló.
