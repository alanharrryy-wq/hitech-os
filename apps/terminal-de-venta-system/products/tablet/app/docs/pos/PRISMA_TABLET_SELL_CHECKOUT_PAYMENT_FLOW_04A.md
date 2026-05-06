# PRISMA Tablet Sell Checkout Payment Flow 04A

## Qué cambia

Este paquete amarra la primera pieza seria del flujo Vender: cobrar desde el ticket sin abandonar `/pos`.

## Flujo esperado

1. Cajero agrega productos al ticket.
2. Pulsa COBRAR o F2.
3. Selecciona Efectivo, Tarjeta o Transferencia.
4. Si es Efectivo, captura recibido y revisa cambio.
5. Confirma venta.
6. API cierra venta local, descuenta stock, deja eventos/outbox y devuelve ticket.
7. UI limpia carrito y muestra ticket cerrado.

## Frontera

Este paquete no implementa devolución ni corte de caja. Eso queda para los ZIPs siguientes, porque meterlo todo aquí sería hacer caldo de pollo con licuadora industrial.
