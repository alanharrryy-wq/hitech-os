# UX PRISMA Tablet - Catálogo + Existencias + Agregar a venta 03J 03K

## 1. Objetivo UX

Que un cajero encuentre un producto y lo mande a venta en menos pasos:

```text
buscar -> revisar estado -> agregar a venta -> cobrar en /pos
```

La pantalla debe resolver la pregunta que pasa en caja cada treinta segundos:

> “¿Este producto existe, cuesta cuánto, queda cuánto y lo puedo cobrar?”

No necesita enseñar la tubería interna. El cajero no fue a comprar cables pelados.

## 2. Principio de diseño

Catálogo y Existencias son dos puertas al mismo acto operativo. En Catálogo el usuario entra pensando en el producto. En Stock entra pensando en disponibilidad. En ambos casos debe poder terminar en venta.

## 3. Jerarquía visual

1. Estado de conexión.
2. Hero con intención del flujo y resumen de riesgo.
3. Métricas de catálogo y stock.
4. Buscador operativo.
5. Filtros por señal.
6. Lista de productos.
7. Detalle ligero y acción de venta.

## 4. Señales visuales

| Señal | Color semántico | Mensaje |
|---|---|---|
| Disponible | éxito | Listo para vender. |
| Stock bajo | advertencia | Vendible, pero vigilar. |
| Sin stock | peligro | Bloqueado para venta. |
| Inactivo | peligro | Bloqueado hasta reactivar. |

## 5. Búsqueda operativa

La búsqueda debe aceptar:

- nombre;
- SKU;
- categoría;
- código de barras;
- códigos secundarios cuando existan.

El botón “Resolver código” permite tratar el campo como lectura exacta de escáner o código pegado.

## 6. Detalle ligero

El detalle no es ficha administrativa pesada. Debe mostrar lo mínimo útil:

- precio;
- SKU;
- código;
- categoría;
- existencia;
- umbral bajo;
- estado;
- acción de venta;
- link a `/pos`.

## 7. Acción “Agregar a venta”

La acción agrega una unidad al carrito persistido de `/pos`. Si el producto ya existe en el carrito, aumenta cantidad con la lógica actual del motor de carrito.

La pantalla debe confirmar el resultado con texto simple:

```text
{Producto} agregado a venta. Carrito: {n} pieza(s).
```

## 8. Bloqueos esperados

### Producto inactivo

Mensaje:

```text
Producto inactivo: no se manda a venta hasta reactivarlo.
```

### Sin stock

Mensaje:

```text
Sin stock: evita vender aire premium, eso ni el marketing lo salva.
```

El tono puede ser chusco, pero el bloqueo debe ser claro. La caja no es lugar para poesía confusa.

## 9. Estado sin conexión

La pantalla debe distinguir dos casos:

1. Sin conexión antes de cargar productos: error visible.
2. Sin conexión después de cargar productos: se conserva lectura local en pantalla y se permite agregar productos vendibles al carrito local.

El mensaje visible evita términos técnicos.

## 10. Empty states

Catálogo:

```text
No hay productos en este filtro.
Cambia la búsqueda o revisa si el producto está inactivo.
```

Stock:

```text
Sin existencias que mostrar.
El filtro actual no encontró productos.
```

## 11. Navegación

El bloque ofrece link claro a `/pos` porque la venta se cobra ahí. No se intenta cobrar desde Catálogo o Stock.

Eso evita un monstruo de dos cabezas: cada ruta hace su chamba y le pasa la estafeta a quien toca.

## 12. Accesibilidad mínima

- Botones con `type="button"` o submit explícito.
- `aria-label` en regiones principales.
- `role="alert"` para bloqueos y errores.
- `role="status"` para confirmaciones.
- Filtros con `aria-pressed`.

## 13. Prueba manual sugerida

1. Abrir `/catalog`.
2. Buscar producto activo.
3. Seleccionar fila.
4. Revisar detalle.
5. Agregar a venta.
6. Abrir `/pos`.
7. Confirmar que el producto aparece en el carrito.
8. Repetir desde `/stock` con producto bajo stock.
9. Confirmar que producto sin stock queda bloqueado.
10. Confirmar que producto inactivo queda bloqueado.

