# PRISMA POS Golden Flow 01

**Proyecto:** PRISMA POS / Terminal de Venta System  
**Superficie principal:** Tablet POS  
**Superficie relacionada:** PC Backoffice  
**Estado:** criterio operativo para siguiente inyeccion  
**Version:** 01  
**Fecha:** 2026-05-03  
**Idioma visible:** es-MX

---

## 1. Decision madre

El flujo ganador de PRISMA Tablet debe ser **scan-first, carrito siempre visible, cobro rapido, offline gobernado y evento auditado**.

Dicho en cristiano de mostrador: el cajero no debe pelearse con la pantalla mientras el cliente ya esta sacando monedas, el niño llora, la fila resopla y el sistema decide ponerse filosofico.

PRISMA Tablet vende.  
PRISMA PC gobierna.  
Los eventos son la verdad operativa.  
Sync es el puente, no el permiso para vender.

---

## 2. Flujo dorado resumido

```text
Apertura de turno
  -> venta scan-first
  -> carrito siempre visible
  -> pre-cobro con validaciones
  -> cobro rapido
  -> ticket + stock + evento
  -> outbox/sync
  -> PC consolida cuando exista
  -> corte de caja
```

---

## 3. Pantalla principal POS

La pantalla principal debe resolver tres cosas sin navegar como turista perdido:

1. encontrar producto;
2. armar ticket;
3. cobrar.

### 3.1 Estructura recomendada

```text
[Header operativo]
  estado de caja | terminal | turno | sync | hora

[Zona izquierda / centro]
  buscador unico
  favoritos / categorias / resultados
  tarjeta de producto

[Zona derecha]
  ticket siempre visible
  total
  acciones de carrito
  cobrar
```

### 3.2 Buscador unico

El buscador debe aceptar:

- codigo de barras;
- SKU;
- nombre parcial;
- categoria;
- descripcion corta;
- productos recientes;
- productos favoritos.

Regla: si el resultado es exacto por barcode o SKU, se agrega al carrito directo. Si hay ambiguedad, muestra opciones. Nada de mandar al cajero a abrir un buscador, luego una ficha, luego otro modal, luego rezar. Eso ya es viacrucis con CSS.

---

## 4. Captura scan-first

### 4.1 Comportamiento esperado

Cuando el cajero escanea:

1. normalizar codigo;
2. buscar en catalogo local;
3. validar producto activo;
4. validar stock y politicas;
5. agregar al carrito;
6. si ya existe la linea, incrementar cantidad;
7. mostrar confirmacion breve.

### 4.2 Estados minimos

```text
PRODUCT_FOUND
PRODUCT_NOT_FOUND
PRODUCT_INACTIVE
INSUFFICIENT_STOCK
BARCODE_DUPLICATED
PRICE_STALE
SYNC_PENDING
```

### 4.3 Hack operativo

Escaneo repetido del mismo producto no debe crear varias lineas iguales. Debe aumentar cantidad:

```text
Coca-Cola 600 ml x3
```

Esto evita tickets que parecen lista de pendientes del compadre moroso.

---

## 5. Tarjeta de producto

La tarjeta visible en terminal debe mostrar lo justo para decidir rapido:

```text
Nombre comercial
Precio grande
Stock disponible
SKU
Codigo de barras
Categoria
Estado operativo
```

### 5.1 Badges recomendados

| Badge | Uso |
|---|---|
| OK | producto activo, precio vigente, stock suficiente |
| Bajo stock | se puede vender, pero debe alertar |
| Sin stock | bloquear o pedir autorizacion segun politica |
| Inactivo | no vender |
| Precio por revisar | vender solo si politica lo permite |
| Sync pendiente | venta local permitida, consolidacion posterior |

---

## 6. Carrito vivo

El ticket debe estar siempre visible mientras se busca, escanea o navega catalogo.

### 6.1 Acciones minimas

- aumentar cantidad;
- disminuir cantidad;
- eliminar linea;
- limpiar carrito;
- guardar carrito;
- recuperar carrito;
- descuento por linea con permiso;
- descuento general con permiso;
- nota opcional por ticket.

### 6.2 Carrito guardado

Formato sugerido:

```text
Carrito 12:42 - $238.50 - 5 articulos
```

No pedir nombre obligatorio. Si el sistema obliga a escribir, la gente escribira `aaa`, `cliente`, `x`, o alguna poesia triste que luego nadie entiende.

---

## 7. Pre-cobro

Antes de cobrar, PRISMA debe validar:

- carrito no vacio;
- turno abierto;
- terminal valida;
- productos activos;
- stock suficiente o politica de override;
- precio vigente o politica de advertencia;
- impuestos calculados;
- descuentos autorizados;
- metodo de pago permitido;
- estado offline aceptable.

### 7.1 Boton cobrar inteligente

Estado bueno:

```text
COBRAR
4 articulos · stock OK · caja abierta
```

Estado bloqueado:

```text
No puedo cobrar todavia:
Leche Lala tiene stock insuficiente.
```

Prohibido mostrar errores tipo `[object Object]`. Eso no es error, es una flatulencia de JavaScript con uniforme.

---

## 8. Cobro rapido

### 8.1 Metodos iniciales

- efectivo;
- tarjeta;
- transferencia;
- mixto;
- vale o credito interno, solo si el negocio lo requiere.

### 8.2 Efectivo

Debe tener botones rapidos:

```text
$50 | $100 | $200 | $500 | exacto | otro
```

Debe calcular cambio automaticamente.

### 8.3 Tarjeta

Debe mostrar:

- lector conectado;
- monto;
- estado de pago;
- resultado;
- reintento si falla;
- advertencia si se opera offline.

### 8.4 Offline gobernado

Offline no significa permiso para hacer cualquier barbaridad con sonrisa de cajero cansado.

Permitido offline:

- vender productos activos del catalogo local;
- tickets locales;
- corte local;
- consulta local;
- exportacion local.

Bloqueable offline:

- devoluciones sensibles;
- descuentos fuertes;
- cambio masivo de precio;
- ajuste grande de inventario;
- cambios de permisos;
- operaciones multi-sucursal.

---

## 9. Cierre de venta

Al confirmar cobro, el sistema debe ejecutar una transaccion local:

```text
1. crear Sale
2. crear SaleLine
3. descontar stock local
4. crear StockMovement
5. crear OutboxEvent
6. responder ticket cerrado
7. actualizar reporte del dia
8. dejar evento disponible para export/sync
```

### 9.1 Eventos minimos

```text
sale.created
sale.completed
ticket.closed
stock.decremented
inventory.low_stock_detected
```

### 9.2 Identificadores obligatorios

Cada venta debe tener:

```text
ticketNumber
businessId
terminalId
operatorId
shiftId
offlineId si aplica
createdAt
completedAt
```

Sin esto, no hay auditoria; hay espiritismo administrativo.

---

## 10. Postventa

Despues de cobrar, la pantalla debe ofrecer:

- nueva venta;
- imprimir ticket;
- reimprimir;
- ver detalle;
- devolver desde ticket;
- exportar o compartir ticket cuando aplique.

### 10.1 Devoluciones

La devolucion debe nacer desde un ticket original, no desde producto suelto.

Motivos minimos:

```text
Producto danado
Cliente se equivoco
Error de captura
Cambio autorizado
Otro con nota obligatoria
```

---

## 11. Corte de caja

El corte debe cerrar el ciclo operativo:

```text
caja inicial
+ efectivo recibido
+ tarjeta
+ transferencias
- devoluciones
= caja esperada
vs caja contada
= diferencia
```

Debe registrar:

- cajero;
- terminal;
- turno;
- hora de apertura;
- hora de cierre;
- ventas;
- cancelaciones;
- devoluciones;
- diferencias;
- eventos pendientes de sync.

---

## 12. Rol de PC

PC no es requisito para vender. PC debe entrar para:

- publicar catalogo y politicas;
- consolidar ventas;
- auditar movimientos;
- resolver conflictos;
- administrar inventario profundo;
- ver KPIs;
- controlar multi-sucursal.

Regla: si Tablet no puede cerrar una venta local permitida porque PC no esta disponible, el flujo esta mal armado.

---

## 13. Criterios de aceptacion de la siguiente inyeccion

La siguiente inyeccion sobre `/pos` debe considerarse lista solo si cumple esto:

### 13.1 Captura

- buscar por nombre;
- buscar por SKU;
- resolver por barcode;
- agregar al carrito;
- incrementar cantidad si el producto ya existe;
- mostrar producto no encontrado sin romper pantalla.

### 13.2 Carrito

- mostrar ticket siempre visible;
- `+` y `-` por linea;
- eliminar linea;
- limpiar carrito;
- total actualizado;
- estado vacio decente.

### 13.3 Cobro

- boton cobrar bloqueado si carrito vacio;
- validacion de stock;
- validacion de producto activo;
- cobro efectivo basico;
- cambio calculado;
- ticket cerrado.

### 13.4 Backend/eventos

- crear venta local;
- crear lineas;
- descontar stock;
- crear movimiento;
- crear outbox;
- actualizar reporte del dia.

### 13.5 UX

- errores visibles en es-MX;
- sin `[object Object]`;
- sin textos de demo;
- sin depender de PC para vender;
- sin bloquear toda la pantalla por sync pendiente.

---

## 14. No objetivos de esta inyeccion

No meter todavia:

- fiscalizacion real;
- CFDI;
- integracion bancaria real;
- pagos con tarjeta reales;
- permisos avanzados multi-rol;
- reconciliacion PC completa;
- dashboard ejecutivo.

Eso va despues. Meterlo ahorita seria construir un segundo piso mientras el albañil todavia esta preguntando donde va la puerta.

---

## 15. Fuentes externas revisadas

- Shopify POS: busqueda global por barcode, SKU, titulo, variantes, tags, proveedor y descripcion; carrito visible durante busqueda global.
- Square POS/Retail: armado de carrito por busqueda, categorias, barcode, grid/favoritos; guardado de carrito.
- Stripe Terminal: pagos offline con reconciliacion mediante identificador propio y envio posterior cuando regresa conectividad.
- PCI SSC: las terminales de pago que capturan datos de tarjeta quedan dentro del entorno sujeto a controles PCI DSS aplicables.

---

## 16. Resumen brutal

El POS bueno no es el que se ve bonito parado en screenshot.  
El POS bueno es el que aguanta fila, cajero cansado, internet malo, producto sin stock, cliente indeciso, devolucion rara y corte de caja sin ponerse a llorar.

Para PRISMA, el flujo dorado es:

```text
Escanear rapido.
Ver carrito siempre.
Cobrar sin rodeos.
Registrar todo.
Sincronizar despues.
Auditar en PC.
```
