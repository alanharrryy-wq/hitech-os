# PRISMA Light POS — UI Kit

## 0. Propósito

Este UI Kit lista los componentes necesarios para construir la interfaz **PRISMA Light POS** con la misma talla visual que la referencia.

La idea es que Codex no tenga que “interpretar el arte”, porque cuando una IA interpreta demasiado, te entrega un tablero de nave espacial con botones de lavandería.

---

## 1. Lista maestra de componentes

Componentes obligatorios:

1. `AppShell`
2. `Sidebar`
3. `BrandBlock`
4. `NavItem`
5. `TerminalStatusCard`
6. `TopBar`
7. `SearchBar`
8. `ScanButton`
9. `IconButton`
10. `UserMenu`
11. `CategoryRail`
12. `CategoryButton`
13. `ProductGrid`
14. `ProductCard`
15. `ProductImageStage`
16. `FavoriteStar`
17. `Pagination`
18. `CartPanel`
19. `CartHeader`
20. `CartItemRow`
21. `QuantityStepper`
22. `TotalsSummary`
23. `CheckoutButton`
24. `SecondaryActionCard`
25. `Toast`
26. `EmptyState`
27. `ErrorState`

---

## 2. AppShell

### Descripción

Contenedor principal de toda la experiencia.

### Responsabilidad

- crear el layout de 3 columnas
- definir fondo general
- aplicar padding exterior
- mantener separación clara entre zonas

### Slots

```tsx
<AppShell>
  <Sidebar />
  <main>
    <TopBar />
    <SalesWorkspace />
  </main>
  <CartPanel />
</AppShell>
```

### Reglas visuales

- fondo `#F6F7FA`
- gradiente cálido muy leve
- columnas con gap amplio
- altura mínima 100vh

---

## 3. Sidebar

### Descripción

Navegación persistente e identidad visual.

### Subcomponentes

- `BrandBlock`
- `NavList`
- `NavItem`
- `TerminalStatusCard`

### Reglas

- superficie blanca translúcida
- radio grande
- sombra suave
- logo arriba
- status abajo

### Variantes

- expanded: icon + label
- compact: icon only, solo si el viewport obliga

---

## 4. BrandBlock

### Contenido

- logo geométrico PRISMA
- wordmark PRISMA
- subtítulo: `SISTEMA DE GESTIÓN INTELIGENTE`

### Reglas

- centrado o alineado con columna
- espacio generoso
- no saturar con dorado
- logo debe sentirse premium, no sticker

### Tamaños

- logo: 72 a 92 px alto
- wordmark: 28 a 40 px ancho visual
- subtítulo: 9 a 11 px, tracking amplio

---

## 5. NavItem

### Props sugeridas

```ts
type NavItemProps = {
  icon: ReactNode
  label: string
  active?: boolean
  disabled?: boolean
}
```

### Estados

#### Default

- texto gris medio
- icono gris
- fondo transparente

#### Hover

- fondo gris claro
- texto más oscuro

#### Active

- fondo dorado suave
- borde dorado
- sombra cálida
- texto oscuro

### Labels recomendados

```text
Ventas
Dashboard
Inventario
Clientes
Productos
Compras
Caja
Reportes
Gastos
Promociones
Usuarios
Configuración
```

---

## 6. TerminalStatusCard

### Contenido

```text
Terminal 01
En línea
```

Opcional:

- avatar / icono de usuario
- dropdown
- punto verde de conexión

### Reglas

- fondo blanco
- borde suave
- radio 16 a 20 px
- pequeño pero claro

---

## 7. TopBar

### Contenido

- título de pantalla: `Ventas`
- controles derecha:
  - tema / sol
  - campana
  - usuario

### Reglas

- no debe competir con buscador
- debe tener mucho aire
- alineación superior limpia

---

## 8. SearchBar

### Placeholder

```text
Buscar producto por código, nombre o SKU...
```

### Slots

- icono lupa
- input
- icono scanner interno opcional

### Reglas

- elemento ancho y dominante
- altura 56–64 px
- fondo blanco
- sombra suave
- borde claro
- radio 18–22 px

### Estados

- default
- focus dorado suave
- error rojo suave
- disabled

---

## 9. ScanButton

### Label

```text
ESCANEAR
```

### Contenido

- icono scanner dorado
- texto uppercase

### Reglas

- altura similar a buscador
- ancho 120–150 px
- fondo blanco
- borde suave
- sombra ligera

---

## 10. IconButton

Uso:

- opciones
- tema
- notificaciones
- cerrar item
- limpiar cart

### Reglas

- 44 × 44 px mínimo
- radio 14–999 px según forma
- borde sutil
- hover visible

---

## 11. UserMenu

### Contenido

```text
AR
Administrador
Sucursal Centro
```

### Reglas

- pill blanco
- avatar circular gris claro
- nombre fuerte
- sucursal pequeña
- flecha dropdown

---

## 12. CategoryRail

### Descripción

Fila de categorías para filtrar productos.

### Reglas

- horizontal
- con separación clara
- dentro de superficie suave opcional
- no saturar

### Categorías

```text
Todos
Bebidas
Snacks
Lácteos
Abarrotes
Limpieza
Personal
```

---

## 13. CategoryButton

### Contenido

- icono circular
- label debajo

### Estados

#### Active

- icono dentro de círculo con borde dorado
- fondo dorado muy claro
- sombra cálida

#### Default

- círculo blanco
- borde gris suave
- label gris medio

### Tamaño

- círculo: 52–58 px
- label: 12–13 px

---

## 14. ProductGrid

### Reglas

- grid 4 columnas en referencia grande
- 2 filas visibles principales
- gap 16–20 px
- alinear cards

### Ejemplo CSS

```css
.product-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(160px, 1fr));
  gap: 18px;
}
```

---

## 15. ProductCard

### Contenido obligatorio

- favorite star
- image stage
- product name
- price
- stock

### Ejemplo de datos

```ts
{
  name: "Coca Cola 600 ml",
  price: "$18.00",
  stock: 156,
  favorite: true,
  image: "/products/coca-cola.png"
}
```

### Reglas visuales

- fondo blanco
- sombra suave
- radio 22 px
- imagen grande
- precio claramente visible
- stock pequeño

---

## 16. ProductImageStage

### Descripción

Área superior de la card donde vive la imagen.

### Reglas

- producto centrado
- pedestal / sombra elíptica
- halo suave opcional según color del producto
- altura 130–155 px

### Halos sugeridos

| Producto | Halo |
|---|---|
| Coca Cola | rojo suave |
| Sabritas | dorado suave |
| Leche | azul/gris suave |
| Agua | azul hielo |
| Café | café/rojo suave |
| Pan | dorado pan |

---

## 17. FavoriteStar

### Reglas

- arriba izquierda o derecha según composición
- dorado si favorito
- gris si no favorito
- pequeño pero visible

---

## 18. Pagination

### Contenido

```text
< 1 2 3 4 5 >
```

### Reglas

- centrada abajo del grid
- botón activo con borde dorado
- botones blancos con sombra suave
- radio 14–16 px

---

## 19. CartPanel

### Descripción

Panel derecho persistente de venta.

### Contenido

- `CartHeader`
- `CartItemList`
- `TotalsSummary`
- `CheckoutButton`
- `SecondaryActionGrid`

### Reglas

- radio 28 px
- sombra panel
- fondo blanco
- debe ocupar alto casi completo

---

## 20. CartHeader

### Contenido

```text
Carrito de venta
4 artículos
[trash]
```

### Reglas

- título fuerte
- contador en pill gris claro
- acción limpiar pequeña

---

## 21. CartItemRow

### Contenido

- número de línea
- thumbnail
- nombre
- precio unitario
- stepper
- total línea
- eliminar

### Reglas

- separación por línea suave
- altura suficiente para touch
- thumbnail en card mini
- total línea alineado derecha

---

## 22. QuantityStepper

### Contenido

```text
-  2  +
```

### Reglas

- forma pill
- botones individuales de 32 px
- número centrado
- borde suave
- hover claro

### Validaciones

- mínimo 1
- si llega a 0, pedir confirmación o eliminar según UX definida
- disabled si stock insuficiente

---

## 23. TotalsSummary

### Filas

```text
Subtotal              $113.50
Impuestos (IVA 16%)    $18.16
Total                 $131.66
```

### Reglas

- separación vertical limpia
- total más grande
- monto total dorado
- label total oscuro

---

## 24. CheckoutButton

### Label

```text
COBRAR                                  F2
```

### Reglas

- ancho completo
- fondo gradiente dorado
- texto oscuro
- radio 16 px
- sombra dorada
- altura 58–64 px

### Estados

- default
- hover: más luminoso
- active: escala 0.99
- disabled: opacidad 0.55

---

## 25. SecondaryActionCard

### Acciones

- `COTIZACIÓN` / `F3`
- `GUARDAR` / `F4`
- `LIMPIAR` / `F5`

### Reglas

- 3 columnas
- fondo blanco
- borde suave
- icono dorado
- label pequeño uppercase
- shortcut debajo

---

## 26. Toast

### Usos

- producto agregado
- ticket guardado
- error de escaneo
- pago completado

### Variantes

- success
- warning
- error
- info

### Reglas

- esquina superior derecha o bajo header
- sombra suave
- borde según estado
- mensaje directo

---

## 27. EmptyState

### Producto vacío

```text
No encontramos productos
Prueba con otro nombre, SKU o código.
```

### Carrito vacío

```text
Tu carrito está vacío
Agrega productos para iniciar la venta.
```

### Reglas

- icono suave
- texto claro
- CTA opcional

---

## 28. ErrorState

### Ejemplos

```text
No se pudo cargar el catálogo
Código no encontrado
Producto sin precio asignado
Sin conexión con sincronización pendiente
```

### Reglas

- rojo suave
- explicación breve
- acción de recuperación

---

## 29. Orden recomendado de implementación

1. AppShell
2. Sidebar
3. TopBar
4. SearchBar + ScanButton
5. CategoryRail
6. ProductGrid + ProductCard
7. CartPanel
8. CartItemRow + QuantityStepper
9. TotalsSummary + CheckoutButton
10. Estados y polish

---

## 30. Checklist de UI Kit

- [ ] Todos los componentes tienen estado default
- [ ] Todos los componentes interactivos tienen hover/focus
- [ ] El botón COBRAR es el CTA más fuerte
- [ ] Las product cards mantienen imagen dominante
- [ ] El carrito se mantiene persistente
- [ ] La sidebar no se ve como menú genérico
- [ ] El dorado está controlado
- [ ] La versión Light no parece plantilla blanca sin alma
