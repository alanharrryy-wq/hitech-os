# PRISMA Light POS — Golden Visual Specs

## 0. Documento maestro

Este archivo es la **fuente visual dorada** para construir la versión **Light / Blanca** de la terminal de venta PRISMA.

No es moodboard.
No es sugerencia bonita.
No es “échale blanco y ya”.

Especifica cómo debe verse, sentirse y comportarse visualmente la interfaz para que Codex, otro ChatGPT, un diseñador o un dev no salgan con una app blanca genérica tipo “sistema de facturación de papelería deprimida”.

---

## 1. Nombre formal del paquete visual

**PRISMA Light POS — Golden Visual Specs**

Nombres equivalentes válidos:

- `PRISMA_LIGHT_POS_GOLDEN_VISUAL_SPECS`
- `PRISMA Light Terminal de Venta — Golden Specs`
- `PRISMA Light POS Visual Source of Truth`

Uso recomendado en repo:

```text
apps/terminal-de-venta-system/docs/PRISMA_LIGHT_POS_GOLDEN_VISUAL_SPECS.md
```

---

## 2. Objetivo visual

La versión Light debe verse como una terminal de venta premium, clara, limpia y de alta confianza, manteniendo el ADN visual de PRISMA:

- fondo blanco / gris muy claro
- superficies suaves con profundidad elegante
- acentos dorados cálidos
- sidebar izquierda con logo PRISMA
- área central de ventas con buscador y grid de productos
- carrito persistente a la derecha
- botón COBRAR dominante
- tarjetas de producto con imagen grande, pedestal y sombra suave
- navegación sobria, no saturada
- estética de sistema serio, no plantilla genérica

La interfaz debe transmitir:

- rapidez
- orden
- claridad
- lujo sobrio
- operación real
- confianza para cobrar dinero

---

## 3. Principio rector

La versión Light no debe ser una app distinta.
Debe ser la **hermana blanca de la versión Dark**.

Mismo esqueleto.
Misma jerarquía.
Misma intención POS.
Otra temperatura visual.

| Elemento | Dark | Light |
|---|---|---|
| Fondo | negro / carbón atmosférico | blanco / marfil / gris niebla |
| Acento | dorado cálido | dorado cálido, más limpio |
| Sensación | nocturna, premium, intensa | diurna, premium, clara |
| Superficies | glass oscuro | glass blanco / soft cards |
| CTA | dorado brillante | dorado cálido sobre blanco |
| Producto | pedestal con glow | pedestal blanco con sombra suave |

---

## 4. Estructura obligatoria de pantalla

La pantalla se divide en tres zonas principales:

```text
┌───────────────┬────────────────────────────────────┬──────────────────────┐
│ Sidebar       │ Área central de venta              │ Carrito de venta     │
│ navegación    │ buscador + categorías + productos  │ ticket + total + CTA │
└───────────────┴────────────────────────────────────┴──────────────────────┘
```

### 4.1 Sidebar izquierda

Debe incluir:

- logo PRISMA arriba
- subtítulo pequeño tipo “Sistema de gestión inteligente”
- navegación vertical
- item activo destacado con fondo dorado suave
- bloque inferior de terminal / usuario / conexión

La sidebar debe sentirse como una columna premium y estable, no como menú Bootstrap disfrazado.

### 4.2 Área central

Debe incluir:

- título de sección: `Ventas`
- buscador grande
- botón de escaneo
- botón de opciones
- fila de categorías
- grid de productos
- paginación inferior

Debe ser la zona de operación rápida.

### 4.3 Carrito derecho

Debe incluir:

- título: `Carrito de venta`
- contador de artículos
- botón limpiar / eliminar
- lista de productos
- controles de cantidad
- subtotal
- impuestos
- total
- botón `COBRAR`
- acciones secundarias: `COTIZACIÓN`, `GUARDAR`, `LIMPIAR`

Debe sentirse como la zona donde se cierra el dinero. Si el botón COBRAR no manda, está mal.

---

## 5. Proporciones visuales

### 5.1 Layout recomendado para escritorio / tablet landscape

- Sidebar: 13% a 16% del ancho
- Área central: 52% a 58%
- Carrito: 26% a 31%

En una referencia de 1536 × 1024 px:

- Sidebar: 200 px aprox.
- Contenido central: 820 px aprox.
- Carrito: 430 px aprox.
- Gaps: 24 px aprox.

### 5.2 Alto visual

- La interfaz debe ocupar prácticamente toda la pantalla.
- Debe dejar respiración alrededor: 8 a 20 px.
- Las tarjetas deben alinearse en filas limpias.

### 5.3 Sistema de espacio

- margen exterior general: 12 a 24 px
- gap entre columnas: 24 px
- gap entre tarjetas: 16 a 20 px
- padding interno de tarjetas: 20 a 24 px
- padding de paneles grandes: 24 a 32 px

---

## 6. Paleta visual Light

### 6.1 Fondos

| Token | Uso | Valor sugerido |
|---|---|---|
| `bg.app` | fondo general | `#F6F7FA` |
| `bg.page` | lienzo central | `#F8FAFC` |
| `bg.warm` | zonas cálidas sutiles | `#FBF8F1` |
| `bg.panel` | panel principal | `#FFFFFF` |
| `bg.panel-soft` | panel secundario | `#FBFCFE` |
| `bg.input` | inputs | `#FFFFFF` |

### 6.2 Texto

| Token | Uso | Valor sugerido |
|---|---|---|
| `text.primary` | títulos | `#171A20` |
| `text.secondary` | labels | `#4E5562` |
| `text.muted` | metadatos | `#8B93A1` |
| `text.soft` | placeholders | `#A8AFBA` |
| `text.inverse` | texto sobre dorado oscuro | `#1B1305` |

### 6.3 Dorados PRISMA

| Token | Uso | Valor sugerido |
|---|---|---|
| `gold.primary` | CTA principal | `#D99A22` |
| `gold.light` | fondos suaves | `#FFF1C8` |
| `gold.mid` | iconos / bordes | `#E5B44E` |
| `gold.deep` | texto énfasis | `#B97810` |
| `gold.glow` | glow / sombra | `rgba(217, 154, 34, 0.28)` |

### 6.4 Bordes y sombras

| Token | Uso | Valor sugerido |
|---|---|---|
| `border.soft` | cards | `#E7EAF0` |
| `border.warm` | activos dorados | `#E5B44E` |
| `shadow.soft` | elevación card | `0 18px 45px rgba(20, 26, 38, 0.08)` |
| `shadow.panel` | panel grande | `0 22px 70px rgba(20, 26, 38, 0.10)` |
| `shadow.gold` | activo / CTA | `0 14px 35px rgba(217, 154, 34, 0.25)` |

---

## 7. Atmósfera visual

La versión Light debe tener luz suave, casi de estudio fotográfico.

Debe sentirse:

- limpia
- cara
- calmada
- funcional
- con objetos flotando suavemente sobre el fondo

No debe sentirse:

- plana
- clínica
- saturada
- como dashboard SaaS genérico
- como POS barato con botones gigantes sin gracia

### 7.1 Luz

Usar:

- sombras difusas
- glow dorado muy controlado
- blur ambiental sutil
- highlights suaves sobre productos

No usar:

- sombras negras duras
- bordes grises pesados
- fondos totalmente blancos sin capas
- gradientes de arcoíris o azules aleatorios

---

## 8. Sidebar detallada

### 8.1 Composición

Orden recomendado:

1. Logo PRISMA
2. Nombre PRISMA
3. Subtítulo pequeño
4. Menú principal
5. Spacer flexible
6. Tarjeta de terminal / conexión

### 8.2 Nav items

Cada item debe tener:

- icono lineal
- label
- padding generoso
- radio grande
- estado activo claro

Ejemplo de navegación:

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

### 8.3 Item activo

El item activo debe usar:

- fondo dorado claro
- borde dorado suave
- sombra cálida discreta
- texto más oscuro y fuerte
- icono dorado

Ejemplo:

```css
background: linear-gradient(135deg, #FFF2C9, #F6D994);
border: 1px solid rgba(217,154,34,.45);
box-shadow: 0 14px 28px rgba(217,154,34,.20);
```

---

## 9. Header y buscador

### 9.1 Título de pantalla

Texto:

```text
Ventas
```

Estilo:

- tamaño 28 a 34 px
- peso 700
- color `text.primary`
- margen inferior amplio

### 9.2 Buscador

Debe ser grande y dominante.

Contenido:

```text
Buscar producto por código, nombre o SKU...
```

Debe incluir:

- icono de lupa
- placeholder gris suave
- botón/ícono de enfoque de scanner al final si aplica
- radio 18 a 22 px
- sombra suave
- borde claro

Altura recomendada:

- 56 a 64 px

### 9.3 Botón ESCANEAR

Debe ir a la derecha del buscador.

Estilo:

- superficie blanca
- borde suave
- icono scanner dorado
- label uppercase pequeño
- sombra ligera
- radio 18 a 22 px

---

## 10. Categorías

### 10.1 Forma

Categorías circulares o semi-circulares con icono arriba y label abajo.

Categorías base:

- Todos
- Bebidas
- Snacks
- Lácteos
- Abarrotes
- Limpieza
- Personal

### 10.2 Activo

El estado activo debe ser dorado:

- círculo con borde dorado
- fondo blanco cálido
- sombra dorada controlada
- icono dorado

### 10.3 Inactivo

- círculo blanco
- borde gris suave
- icono gris oscuro
- label gris medio

---

## 11. Grid de productos

### 11.1 Layout

Grid recomendado:

- 4 columnas en desktop ancho
- 2 filas visibles iniciales
- gap 16 a 20 px

Card típica:

- ancho: 180 a 210 px
- alto: 260 a 300 px

### 11.2 Product card

Cada tarjeta debe incluir:

- estrella/favorito arriba
- imagen grande centrada
- pedestal/sombra bajo producto
- nombre del producto
- precio grande
- stock

Orden:

```text
[estrella]
[imagen producto centrada]
[nombre]
[precio]
[stock]
```

### 11.3 Imagen del producto

Reglas:

- producto grande, no miniatura miserable
- debe tener aire alrededor
- debe asentarse en un pedestal / sombra elíptica
- puede tener halo de color muy suave relacionado al empaque

Ejemplo:

- Coca Cola: halo rojo sutil
- Sabritas: halo amarillo/dorado
- Agua: halo azul suave
- Leche: halo blanco/azul
- Café: halo café/rojo

### 11.4 Precio

- tamaño 18 a 22 px
- peso 600 o 700
- color negro / gris muy oscuro
- no usar azul
- opcional dorado solo si la jerarquía lo pide

### 11.5 Stock

- tamaño 12 a 13 px
- gris medio
- texto ejemplo: `Stock: 156`

---

## 12. Carrito de venta

### 12.1 Panel

El panel debe sentirse como una tarjeta alta premium:

- fondo blanco
- borde muy suave
- sombra elegante
- radio 24 a 32 px
- padding 24 a 32 px

### 12.2 Header

Contenido:

```text
Carrito de venta
4 artículos
[icono limpiar]
```

El contador debe estar en pill suave.

### 12.3 Línea de producto

Cada item debe tener:

- índice circular pequeño
- miniatura del producto
- nombre
- precio unitario
- stepper cantidad
- total línea
- botón X

Layout aproximado:

```text
(1) [img] Coca Cola 600 ml     X
        $18.00     [- 2 +]   $36.00
```

### 12.4 Separadores

Usar líneas muy suaves:

```css
border-bottom: 1px solid rgba(20, 26, 38, 0.08);
```

Nada de líneas negras agresivas.

---

## 13. Totales

### 13.1 Filas

Obligatorias:

```text
Subtotal
Impuestos (IVA 16%)
Total
```

### 13.2 Total

Debe dominar visualmente, antes del botón.

Estilo:

- label `Total` en 20 a 24 px
- monto en 30 a 36 px
- color dorado profundo
- peso 700

Ejemplo:

```text
Total                     $131.66
```

---

## 14. Botón COBRAR

### 14.1 Jerarquía

El botón COBRAR es el objeto de dinero. Debe mandar.

Debe ser:

- ancho completo
- alto 56 a 64 px
- fondo dorado en gradiente
- texto oscuro
- label fuerte
- tecla rápida a la derecha: `F2`

Ejemplo:

```text
COBRAR                                      F2
```

### 14.2 Estilo

```css
background: linear-gradient(135deg, #F6D889 0%, #D99A22 100%);
color: #1B1305;
border: 1px solid rgba(185, 120, 16, .35);
box-shadow: 0 18px 36px rgba(217,154,34,.28);
border-radius: 16px;
```

### 14.3 Hover / active

Hover:

- elevar 1 a 2 px
- aumentar brillo 5%
- sombra dorada ligeramente mayor

Active:

- reducir escala a 0.99
- sombra menor

---

## 15. Acciones secundarias

Botones:

- COTIZACIÓN `F3`
- GUARDAR `F4`
- LIMPIAR `F5`

Deben ser:

- tarjetas pequeñas
- fondo blanco
- borde suave
- icono dorado
- label uppercase pequeño
- shortcut debajo

No deben competir con COBRAR.

---

## 16. Top right controls

Zona superior derecha:

- toggle tema / sol
- notificaciones
- usuario administrador

### 16.1 Usuario

Debe incluir:

- avatar circular con iniciales
- nombre: `Administrador`
- sucursal: `Sucursal Centro`
- flecha dropdown

Estilo:

- pill blanco
- sombra suave
- borde claro
- radio grande

---

## 17. Paginación

Abajo del grid:

- botón anterior
- páginas 1, 2, 3, 4, 5
- botón siguiente

Estado activo:

- borde dorado
- fondo blanco cálido
- texto oscuro

Debe estar centrado o alineado con grid.

---

## 18. Estados visuales

### 18.1 Hover producto

- sombra más visible
- ligero translateY(-2px)
- borde un poco más dorado si está activo / favorito
- no exagerar animación

### 18.2 Producto seleccionado / agregado

Opciones:

- borde dorado
- glow suave
- check o estado “En carrito”
- microfeedback temporal

### 18.3 Producto sin stock

- imagen opacada
- stock en rojo suave
- botón deshabilitado
- card con menor contraste

### 18.4 Error de escaneo

- toast arriba o cerca del buscador
- color rojo suave
- mensaje claro:
  - `Código no encontrado`
  - `Producto inactivo`
  - `SKU sin precio`

---

## 19. Animación

Usar animación mínima:

- hover cards: 140ms a 180ms
- botones: 120ms
- panel/cart update: 180ms
- toast: 220ms

Easing:

```css
cubic-bezier(.2,.8,.2,1)
```

No usar rebotes infantiles. Esto cobra dinero, no vende globos.

---

## 20. Accesibilidad

Debe cumplir:

- contraste legible
- targets mínimos de 44 × 44 px
- labels visibles junto a iconos principales
- focus ring claro
- no depender solo del color para estados críticos
- texto de precio y total siempre claro

---

## 21. Checklist de fidelidad

Antes de aprobar una implementación Light, validar:

- [ ] ¿Tiene sidebar izquierda con PRISMA?
- [ ] ¿Tiene área central de ventas?
- [ ] ¿Tiene buscador grande?
- [ ] ¿Tiene botón ESCANEAR?
- [ ] ¿Tiene categorías circulares/chips?
- [ ] ¿Tiene grid de productos con imágenes grandes?
- [ ] ¿Las tarjetas parecen premium y suaves?
- [ ] ¿El carrito está fijo a la derecha?
- [ ] ¿El total destaca?
- [ ] ¿El botón COBRAR domina?
- [ ] ¿El dorado es elegante y no naco?
- [ ] ¿La interfaz sigue sintiéndose POS y no dashboard genérico?
- [ ] ¿La versión Light parece hermana de la Dark?

---

## 22. Frase de implementación para Codex

```text
Implement the PRISMA Light POS interface following the Golden Visual Specs exactly.
Preserve the three-zone layout: left sidebar, central product sales grid, right cart.
Use white / warm light surfaces, soft shadows, rounded premium cards, and warm gold accents.
Do not reinterpret the screen as a generic dashboard.
The result must look like a faithful light-mode sibling of the PRISMA dark POS reference.
```
