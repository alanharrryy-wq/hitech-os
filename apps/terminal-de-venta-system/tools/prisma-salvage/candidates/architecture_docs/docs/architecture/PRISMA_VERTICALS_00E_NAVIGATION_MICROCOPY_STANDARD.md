# PRISMA Verticales 00E - Estándar de navegación y microcopy

## Palabras permitidas
Vender, Cobro, Ticket, Ventas de hoy, Existencias, Turno, Devoluciones, Pendientes por enviar, Enviado, Falló el envío, Se intentará de nuevo, Abrir turno, Cerrar turno, Nueva venta.

## Palabras prohibidas visibles
`checkout`, `cart`, `sync`, `outbox`, `runtime`, `lookup`, `guardrails`, `SaleReturn`, `amountCents`, `restock`, `payload`, `API`, `endpoint`, `worker`, `ack`, `schema`, `queue`


## Pantalla: Vender

- Propósito: iniciar y operar ventas.
- Acción principal: Buscar o escanear producto.
- Estado vacío: "Tu ticket está vacío. Agrega productos para iniciar la venta."
- Cargando: "Un momento, estamos cargando."
- Error: "No pudimos completar la acción. Intenta otra vez."
- Deshabilitado: "Completa lo necesario para continuar."
- Sin conexión: "Puedes seguir trabajando si la operación local está permitida."
- Pendiente por enviar: "Se enviará cuando haya conexión."


## Pantalla: Cobro

- Propósito: cerrar venta y registrar pago.
- Acción principal: Confirmar cobro.
- Estado vacío: "No hay ticket para cobrar."
- Cargando: "Un momento, estamos cargando."
- Error: "No pudimos completar la acción. Intenta otra vez."
- Deshabilitado: "Completa lo necesario para continuar."
- Sin conexión: "Puedes seguir trabajando si la operación local está permitida."
- Pendiente por enviar: "Se enviará cuando haya conexión."


## Pantalla: Ventas de hoy

- Propósito: consultar tickets cerrados.
- Acción principal: Ver detalle de ticket.
- Estado vacío: "Todavía no hay ventas hoy."
- Cargando: "Un momento, estamos cargando."
- Error: "No pudimos completar la acción. Intenta otra vez."
- Deshabilitado: "Completa lo necesario para continuar."
- Sin conexión: "Puedes seguir trabajando si la operación local está permitida."
- Pendiente por enviar: "Se enviará cuando haya conexión."


## Pantalla: Existencias

- Propósito: consultar disponibilidad operativa.
- Acción principal: Buscar producto.
- Estado vacío: "Busca un producto para ver existencias."
- Cargando: "Un momento, estamos cargando."
- Error: "No pudimos completar la acción. Intenta otra vez."
- Deshabilitado: "Completa lo necesario para continuar."
- Sin conexión: "Puedes seguir trabajando si la operación local está permitida."
- Pendiente por enviar: "Se enviará cuando haya conexión."


## Pantalla: Devoluciones

- Propósito: registrar devolución segura.
- Acción principal: Buscar ticket.
- Estado vacío: "Busca el ticket de la venta."
- Cargando: "Un momento, estamos cargando."
- Error: "No pudimos completar la acción. Intenta otra vez."
- Deshabilitado: "Completa lo necesario para continuar."
- Sin conexión: "Puedes seguir trabajando si la operación local está permitida."
- Pendiente por enviar: "Se enviará cuando haya conexión."


## Pantalla: Turno

- Propósito: abrir, revisar o cerrar caja.
- Acción principal: Abrir o cerrar turno.
- Estado vacío: "No hay turno abierto."
- Cargando: "Un momento, estamos cargando."
- Error: "No pudimos completar la acción. Intenta otra vez."
- Deshabilitado: "Completa lo necesario para continuar."
- Sin conexión: "Puedes seguir trabajando si la operación local está permitida."
- Pendiente por enviar: "Se enviará cuando haya conexión."


## Pantalla: Pendientes por enviar

- Propósito: explicar operaciones locales no enviadas.
- Acción principal: Reintentar envío.
- Estado vacío: "Todo está enviado."
- Cargando: "Un momento, estamos cargando."
- Error: "No pudimos completar la acción. Intenta otra vez."
- Deshabilitado: "Completa lo necesario para continuar."
- Sin conexión: "Puedes seguir trabajando si la operación local está permitida."
- Pendiente por enviar: "Se enviará cuando haya conexión."


## Pantalla: Catálogo

- Propósito: consultar producto o crear básico.
- Acción principal: Buscar producto.
- Estado vacío: "Busca por nombre, SKU o código."
- Cargando: "Un momento, estamos cargando."
- Error: "No pudimos completar la acción. Intenta otra vez."
- Deshabilitado: "Completa lo necesario para continuar."
- Sin conexión: "Puedes seguir trabajando si la operación local está permitida."
- Pendiente por enviar: "Se enviará cuando haya conexión."


## Microcopy por vertical: Tienda de conveniencia

- Acción inicial: "Vender"
- Bloqueo común: "No se puede continuar: producto no encontrado."
- Ayuda corta: "Revisa cobro o vuelve a vender."
- Error offline: "La operación quedó guardada en esta Tablet. Se enviará después."
- Éxito: "Operación completada."


## Microcopy por vertical: Restaurante / cafetería

- Acción inicial: "Vender"
- Bloqueo común: "No se puede continuar: pedido sin mesa."
- Ayuda corta: "Revisa mesa o pedido o vuelve a vender."
- Error offline: "La operación quedó guardada en esta Tablet. Se enviará después."
- Éxito: "Operación completada."


## Microcopy por vertical: Farmacia

- Acción inicial: "Vender"
- Bloqueo común: "No se puede continuar: receta requerida."
- Ayuda corta: "Revisa cobro o vuelve a vender."
- Error offline: "La operación quedó guardada en esta Tablet. Se enviará después."
- Éxito: "Operación completada."


## Microcopy por vertical: Estética / barbería / salón

- Acción inicial: "Agenda"
- Bloqueo común: "No se puede continuar: cita empalmada."
- Ayuda corta: "Revisa cobro o vuelve a agenda."
- Error offline: "La operación quedó guardada en esta Tablet. Se enviará después."
- Éxito: "Operación completada."


## Microcopy por vertical: Ferretería

- Acción inicial: "Vender"
- Bloqueo común: "No se puede continuar: unidad inválida."
- Ayuda corta: "Revisa cotización rápida o vuelve a vender."
- Error offline: "La operación quedó guardada en esta Tablet. Se enviará después."
- Éxito: "Operación completada."


## Microcopy por vertical: Ropa / boutique

- Acción inicial: "Vender"
- Bloqueo común: "No se puede continuar: talla agotada."
- Ayuda corta: "Revisa cambios o vuelve a vender."
- Error offline: "La operación quedó guardada en esta Tablet. Se enviará después."
- Éxito: "Operación completada."


## Microcopy por vertical: Taller / reparaciones

- Acción inicial: "Órdenes"
- Bloqueo común: "No se puede continuar: orden incompleta."
- Ayuda corta: "Revisa cobro o vuelve a órdenes."
- Error offline: "La operación quedó guardada en esta Tablet. Se enviará después."
- Éxito: "Operación completada."


## Microcopy por vertical: Venta en campo / ruta

- Acción inicial: "Ruta"
- Bloqueo común: "No se puede continuar: cliente sin ruta."
- Ayuda corta: "Revisa vender o vuelve a ruta."
- Error offline: "La operación quedó guardada en esta Tablet. Se enviará después."
- Éxito: "Operación completada."


## Microcopy por vertical: Abarrotes con báscula

- Acción inicial: "Vender"
- Bloqueo común: "No se puede continuar: peso inválido."
- Ayuda corta: "Revisa pesaje o vuelve a vender."
- Error offline: "La operación quedó guardada en esta Tablet. Se enviará después."
- Éxito: "Operación completada."


## Microcopy por vertical: Food truck / punto móvil de comida

- Acción inicial: "Vender"
- Bloqueo común: "No se puede continuar: menú agotado."
- Ayuda corta: "Revisa pedido o vuelve a vender."
- Error offline: "La operación quedó guardada en esta Tablet. Se enviará después."
- Éxito: "Operación completada."
