# PRISMA Tablet - Contrato técnico Cobro, Ticket, Ventas y Devolución 03E-03I

## Decisión

El cobro pertenece a `/pos` como panel interno de Vender. No se crea pestaña principal de Cobro. El ticket cerrado se muestra como resultado del flujo de venta y no como pantalla huérfana.

## Flujo principal

```text
/pos
  -> buscar producto
  -> agregar a ticket
  -> abrir Cobro
  -> revisar total y método
  -> confirmar venta
  -> API complete sale
  -> ticket cerrado
  -> nueva venta
```

## Flujos secundarios

```text
/sales/today
  -> resumen del día
  -> lista de tickets
  -> detalle de ticket
  -> devolución contextual
```

## Reglas de seguridad operativa

1. Confirmar venta se bloquea mientras la solicitud está en curso.
2. Cada intento usa `clientRequestId` para reducir riesgo de doble cobro.
3. Si falla el cierre, el sistema no debe decir que el ticket quedó vendido.
4. Si el ticket cerró, se limpia carrito y se muestra estado de éxito.
5. Devolución nace del ticket cerrado y exige motivo.
6. Cancelación de recepción, compras o proveedores no pertenecen a Tablet; son PC.

## Rutas alias

| Ruta | Destino |
|---|---|
| `/checkout` | `/pos` |
| `/sales` | `/sales/today` |
| `/returns` | `/sales/today` |
| `/inventory` | `/stock` |
| `/existencias` | `/stock` |

## Estado visible permitido

- Cobro dentro de Vender
- Confirmar venta
- Guardando venta
- Ticket cerrado
- Nueva venta
- Ventas de hoy
- Ver detalle
- Hacer devolución
- Confirmar devolución

## Estado visible prohibido

- `outbox`
- `payload`
- `schema`
- `mutation`
- `query`
- `amountCents`
- `saleReturn`
- `undefined`
- `null`
- stack traces

## Datos mínimos de ticket

Un ticket cerrado debe poder mostrar:

- folio;
- total;
- método de pago;
- operador;
- terminal;
- líneas;
- piezas;
- estado;
- acción de nueva venta;
- acción de devolución si aplica.

## Datos mínimos de devolución

Una devolución debe registrar:

- ticket origen;
- líneas seleccionadas;
- cantidades;
- motivo;
- importe;
- operador;
- fecha;
- evento `sale.return.created`.

## Regla de frontera

Tablet ejecuta devolución operativa desde ticket. PC audita, consolida y gobierna políticas avanzadas.
