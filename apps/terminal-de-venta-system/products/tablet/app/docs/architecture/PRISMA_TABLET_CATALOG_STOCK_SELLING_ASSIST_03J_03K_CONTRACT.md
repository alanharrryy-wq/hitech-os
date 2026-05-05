# PRISMA Tablet - Catalog Stock Selling Assist 03J 03K

## 1. Intención

Este contrato convierte Catálogo y Existencias en un bloque funcional completo: buscar un producto, leer su estado operativo, entender si puede venderse y mandarlo al carrito real de `/pos`.

La entrega no trata `/catalog` y `/stock` como vitrinas separadas. Las une como flujo de venta asistida porque el cajero no piensa por carpetas, piensa por producto: qué es, cuánto cuesta, cuánto queda y si lo puede cobrar.

## 2. Rutas cubiertas

| Ruta | Rol nuevo |
|---|---|
| `/catalog` | Búsqueda operativa de producto con detalle ligero y acción para agregar a venta. |
| `/stock` | Vista de existencias con filtros de vendibles, stock bajo, sin stock e inactivos. |
| `/existencias` | Alias operativo de `/stock`, sin redirección ciega para conservar contexto visual. |
| `/pos` | Destino del carrito persistido. No se reimplementa venta, se alimenta el flujo ya existente. |

## 3. Archivos principales

| Archivo | Responsabilidad |
|---|---|
| `components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx` | Pantalla cliente compartida para `/catalog`, `/stock` y `/existencias`. |
| `components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css` | Sistema visual del bloque: hero, métricas, filtros, filas y detalle. |
| `src/lib/catalog-stock-selling-assist/catalog-stock-selling-assist-contract.ts` | Tipos, copy visible y constantes del contrato 03J 03K. |
| `src/lib/catalog-stock-selling-assist/catalog-stock-selling-assist-view-model.ts` | Clasificación de producto, filtros, métricas y detalle de stock. |
| `src/lib/catalog-stock-selling-assist/catalog-stock-cart-handoff.ts` | Puente seguro hacia el carrito local usado por `/pos`. |

## 4. Decisiones de arquitectura

### 4.1 No duplicar el POS

El bloque no crea otro carrito visual independiente. Usa la misma clave local de carrito que ya usa `/pos` mediante `POS_CART_STORAGE_KEY` y respeta la forma `CartLine` existente.

Esto evita el clásico pecado de sistema de punto de venta: tener un carrito en una pantalla, otro carrito en otra, y que al final el cajero esté haciendo arqueología digital con cara de “¿dónde quedó mi Coca?”.

### 4.2 No vender producto bloqueado

El bloque solo permite mandar a venta productos con señal:

- `available`
- `low_stock`

Bloquea:

- `out_of_stock`
- `inactive`

La intención es clara: vender producto con stock bajo es válido, pero vender cero existencias es vender humo con etiqueta bonita.

### 4.3 Estado offline visible

La pantalla escucha `navigator.onLine`, muestra estado visible y conserva productos ya cargados. Si la conexión cae después de cargar datos, el cajero puede revisar esos datos y mandar productos vendibles al carrito local.

La regla no promete sincronización ni inventario perfecto offline en este bloque. Solo hace visible el estado y conserva continuidad de venta asistida con datos ya disponibles.

### 4.4 Catálogo y stock comparten modelo

El mismo modelo de producto se usa para ambas rutas:

```ts
CatalogStockSellingAssistProduct
```

La diferencia entre rutas está en:

- copy visible;
- filtro inicial;
- prioridad de ordenamiento;
- intención operativa.

## 5. Señales de producto

| Señal | Condición | Acción |
|---|---|---|
| `available` | Activo y existencia mayor al umbral bajo | Puede agregarse a venta. |
| `low_stock` | Activo y existencia entre 1 y umbral bajo | Puede agregarse a venta con advertencia. |
| `out_of_stock` | Activo con existencia 0 o menor | No se agrega a venta. |
| `inactive` | Producto inactivo | No se agrega a venta. |

## 6. Estados de pantalla

| Estado | Uso |
|---|---|
| `idle` | Antes de primera lectura. |
| `loading` | Consulta en curso. |
| `ready` | Productos disponibles. |
| `empty` | Consulta sin resultados. |
| `error` | No hubo lectura útil. |
| `offline` | Sin conexión visible, usando datos ya cargados cuando existan. |

## 7. Copy operativo permitido

El bloque debe hablar como herramienta de tienda, no como consola de programador.

Permitido:

- “Agregar a venta”
- “Stock bajo”
- “Sin stock”
- “Producto inactivo”
- “Carrito local”
- “Conexión visible”

Prohibido en UI visible del bloque:

- `payload`
- `outbox`
- `runtime`
- `fixture`
- `mock`
- `demo`
- `TODO`

## 8. Flujo principal

```text
1. Cajero entra a /catalog o /stock.
2. La pantalla consulta /api/pos/products/search.
3. El cajero busca por nombre, SKU, categoría o código.
4. La pantalla clasifica cada producto como disponible, stock bajo, sin stock o inactivo.
5. El cajero abre detalle ligero.
6. Si el producto es vendible, pulsa Agregar a venta.
7. El producto se agrega al carrito persistido que lee /pos.
8. El cajero abre /pos y cobra con el flujo existente.
```

## 9. Qué no toca esta entrega

No toca:

- motor de cobro;
- API de cierre de venta;
- esquema Prisma;
- shared kernel;
- PC;
- permisos avanzados;
- sincronización profunda;
- devoluciones;
- turno.

## 10. Criterios de aceptación

Una instalación se considera correcta si:

1. `/catalog` renderiza la pantalla compartida en modo catálogo.
2. `/stock` renderiza la pantalla compartida en modo stock.
3. `/existencias` renderiza el mismo bloque de existencias.
4. Existen filtros de vendibles, stock bajo, sin stock e inactivos.
5. La acción de agregar usa `POS_CART_STORAGE_KEY`.
6. Los productos inactivos y sin stock quedan bloqueados.
7. El estado sin conexión es visible.
8. La UI visible no expone lenguaje técnico crudo.
9. Los verificadores incluidos pasan en instalación.

## 11. Riesgos controlados

| Riesgo | Control |
|---|---|
| Duplicar carrito | Se usa `POS_CART_STORAGE_KEY` existente. |
| Vender producto inactivo | `canSendProductToSale()` bloquea por señal. |
| Vender sin stock | `out_of_stock` deshabilita acción. |
| UI técnica | Verificador anti-copy revisa términos prohibidos en componentes. |
| Ruta suelta | Verificador de rutas exige imports y modos correctos. |

## 12. Compatibilidad con arquitectura PRISMA

La arquitectura base indica que Tablet debe poder vender sola, con catálogo local, stock local, ventas locales y continuidad aunque PC no exista. Este paquete fortalece esa línea porque Catálogo y Stock ya no son pantallas de consulta pasiva: ahora alimentan la venta local.

