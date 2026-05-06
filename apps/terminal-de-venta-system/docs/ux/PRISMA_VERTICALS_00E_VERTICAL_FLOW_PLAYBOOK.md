# PRISMA Verticales 00E - Playbook de flujos operativos


## Tienda de conveniencia

### Ruta feliz
1. El operador entra a **Vender**.
2. Ejecuta el gesto principal del giro: venta de productos por código de barras, ticket rápido, efectivo, tarjeta, devolución simple y corte de turno.
3. Corrige errores simples sin salir del flujo.
4. Pasa a cobro o cierre operativo.
5. Recibe confirmación clara.
6. Si no hay conexión, la operación queda como pendiente por enviar.

### Ruta con error 1: producto no encontrado
- Mensaje corto: "No se puede continuar: producto no encontrado."
- Acción sugerida: volver a la pantalla principal o corregir el dato.
- No usar lenguaje técnico.

### Ruta con error 2: producto sin stock
- Mensaje corto: "Revisa este dato antes de continuar."
- Acción sugerida: cambiar cantidad, elegir otra opción o pedir autorización.

### Ruta con error 3: precio faltante
- Mensaje corto: "Hace falta completar esta información."
- Acción sugerida: completar, cancelar o volver.

### Ruta offline
- Mostrar que la operación local está guardada.
- Mostrar si se puede seguir operando.
- Mostrar pendientes sin palabras técnicas.


## Restaurante / cafetería

### Ruta feliz
1. El operador entra a **Vender**.
2. Ejecuta el gesto principal del giro: pedido abierto, mesa o para llevar, envío a cocina, cierre de cuenta, propina opcional y corte.
3. Corrige errores simples sin salir del flujo.
4. Pasa a cobro o cierre operativo.
5. Recibe confirmación clara.
6. Si no hay conexión, la operación queda como pendiente por enviar.

### Ruta con error 1: pedido sin mesa
- Mensaje corto: "No se puede continuar: pedido sin mesa."
- Acción sugerida: volver a la pantalla principal o corregir el dato.
- No usar lenguaje técnico.

### Ruta con error 2: producto agotado
- Mensaje corto: "Revisa este dato antes de continuar."
- Acción sugerida: cambiar cantidad, elegir otra opción o pedir autorización.

### Ruta con error 3: cocina no disponible
- Mensaje corto: "Hace falta completar esta información."
- Acción sugerida: completar, cancelar o volver.

### Ruta offline
- Mostrar que la operación local está guardada.
- Mostrar si se puede seguir operando.
- Mostrar pendientes sin palabras técnicas.


## Farmacia

### Ruta feliz
1. El operador entra a **Vender**.
2. Ejecuta el gesto principal del giro: venta de producto sensible, revisión de lote/caducidad, bloqueo por permiso, ticket y auditoría.
3. Corrige errores simples sin salir del flujo.
4. Pasa a cobro o cierre operativo.
5. Recibe confirmación clara.
6. Si no hay conexión, la operación queda como pendiente por enviar.

### Ruta con error 1: receta requerida
- Mensaje corto: "No se puede continuar: receta requerida."
- Acción sugerida: volver a la pantalla principal o corregir el dato.
- No usar lenguaje técnico.

### Ruta con error 2: lote vencido
- Mensaje corto: "Revisa este dato antes de continuar."
- Acción sugerida: cambiar cantidad, elegir otra opción o pedir autorización.

### Ruta con error 3: producto restringido
- Mensaje corto: "Hace falta completar esta información."
- Acción sugerida: completar, cancelar o volver.

### Ruta offline
- Mostrar que la operación local está guardada.
- Mostrar si se puede seguir operando.
- Mostrar pendientes sin palabras técnicas.


## Estética / barbería / salón

### Ruta feliz
1. El operador entra a **Agenda**.
2. Ejecuta el gesto principal del giro: cita o servicio sin cita, selección de servicio, asignación de personal, cobro y comisión.
3. Corrige errores simples sin salir del flujo.
4. Pasa a cobro o cierre operativo.
5. Recibe confirmación clara.
6. Si no hay conexión, la operación queda como pendiente por enviar.

### Ruta con error 1: cita empalmada
- Mensaje corto: "No se puede continuar: cita empalmada."
- Acción sugerida: volver a la pantalla principal o corregir el dato.
- No usar lenguaje técnico.

### Ruta con error 2: servicio sin precio
- Mensaje corto: "Revisa este dato antes de continuar."
- Acción sugerida: cambiar cantidad, elegir otra opción o pedir autorización.

### Ruta con error 3: personal no asignado
- Mensaje corto: "Hace falta completar esta información."
- Acción sugerida: completar, cancelar o volver.

### Ruta offline
- Mostrar que la operación local está guardada.
- Mostrar si se puede seguir operando.
- Mostrar pendientes sin palabras técnicas.


## Ferretería

### Ruta feliz
1. El operador entra a **Vender**.
2. Ejecuta el gesto principal del giro: venta por pieza, metro, kilo o paquete, cotización rápida, conversión de unidades y cobro.
3. Corrige errores simples sin salir del flujo.
4. Pasa a cobro o cierre operativo.
5. Recibe confirmación clara.
6. Si no hay conexión, la operación queda como pendiente por enviar.

### Ruta con error 1: unidad inválida
- Mensaje corto: "No se puede continuar: unidad inválida."
- Acción sugerida: volver a la pantalla principal o corregir el dato.
- No usar lenguaje técnico.

### Ruta con error 2: cantidad decimal inválida
- Mensaje corto: "Revisa este dato antes de continuar."
- Acción sugerida: cambiar cantidad, elegir otra opción o pedir autorización.

### Ruta con error 3: cotización vencida
- Mensaje corto: "Hace falta completar esta información."
- Acción sugerida: completar, cancelar o volver.

### Ruta offline
- Mostrar que la operación local está guardada.
- Mostrar si se puede seguir operando.
- Mostrar pendientes sin palabras técnicas.


## Ropa / boutique

### Ruta feliz
1. El operador entra a **Vender**.
2. Ejecuta el gesto principal del giro: venta por talla/color, cambio de producto, ticket y consulta de variantes disponibles.
3. Corrige errores simples sin salir del flujo.
4. Pasa a cobro o cierre operativo.
5. Recibe confirmación clara.
6. Si no hay conexión, la operación queda como pendiente por enviar.

### Ruta con error 1: talla agotada
- Mensaje corto: "No se puede continuar: talla agotada."
- Acción sugerida: volver a la pantalla principal o corregir el dato.
- No usar lenguaje técnico.

### Ruta con error 2: color agotado
- Mensaje corto: "Revisa este dato antes de continuar."
- Acción sugerida: cambiar cantidad, elegir otra opción o pedir autorización.

### Ruta con error 3: cambio fuera de política
- Mensaje corto: "Hace falta completar esta información."
- Acción sugerida: completar, cancelar o volver.

### Ruta offline
- Mostrar que la operación local está guardada.
- Mostrar si se puede seguir operando.
- Mostrar pendientes sin palabras técnicas.


## Taller / reparaciones

### Ruta feliz
1. El operador entra a **Órdenes**.
2. Ejecuta el gesto principal del giro: orden de trabajo, diagnóstico simple, refacción, mano de obra, anticipo y cierre.
3. Corrige errores simples sin salir del flujo.
4. Pasa a cobro o cierre operativo.
5. Recibe confirmación clara.
6. Si no hay conexión, la operación queda como pendiente por enviar.

### Ruta con error 1: orden incompleta
- Mensaje corto: "No se puede continuar: orden incompleta."
- Acción sugerida: volver a la pantalla principal o corregir el dato.
- No usar lenguaje técnico.

### Ruta con error 2: anticipo insuficiente
- Mensaje corto: "Revisa este dato antes de continuar."
- Acción sugerida: cambiar cantidad, elegir otra opción o pedir autorización.

### Ruta con error 3: refacción sin stock
- Mensaje corto: "Hace falta completar esta información."
- Acción sugerida: completar, cancelar o volver.

### Ruta offline
- Mostrar que la operación local está guardada.
- Mostrar si se puede seguir operando.
- Mostrar pendientes sin palabras técnicas.


## Venta en campo / ruta

### Ruta feliz
1. El operador entra a **Ruta**.
2. Ejecuta el gesto principal del giro: visita a cliente, venta offline, cobro, crédito permitido, pendiente de envío y cierre de ruta.
3. Corrige errores simples sin salir del flujo.
4. Pasa a cobro o cierre operativo.
5. Recibe confirmación clara.
6. Si no hay conexión, la operación queda como pendiente por enviar.

### Ruta con error 1: cliente sin ruta
- Mensaje corto: "No se puede continuar: cliente sin ruta."
- Acción sugerida: volver a la pantalla principal o corregir el dato.
- No usar lenguaje técnico.

### Ruta con error 2: crédito no permitido
- Mensaje corto: "Revisa este dato antes de continuar."
- Acción sugerida: cambiar cantidad, elegir otra opción o pedir autorización.

### Ruta con error 3: sin conexión
- Mensaje corto: "Hace falta completar esta información."
- Acción sugerida: completar, cancelar o volver.

### Ruta offline
- Mostrar que la operación local está guardada.
- Mostrar si se puede seguir operando.
- Mostrar pendientes sin palabras técnicas.


## Abarrotes con báscula

### Ruta feliz
1. El operador entra a **Vender**.
2. Ejecuta el gesto principal del giro: producto pesable, lectura de peso o captura manual, precio por unidad, ticket y cobro.
3. Corrige errores simples sin salir del flujo.
4. Pasa a cobro o cierre operativo.
5. Recibe confirmación clara.
6. Si no hay conexión, la operación queda como pendiente por enviar.

### Ruta con error 1: peso inválido
- Mensaje corto: "No se puede continuar: peso inválido."
- Acción sugerida: volver a la pantalla principal o corregir el dato.
- No usar lenguaje técnico.

### Ruta con error 2: báscula no disponible
- Mensaje corto: "Revisa este dato antes de continuar."
- Acción sugerida: cambiar cantidad, elegir otra opción o pedir autorización.

### Ruta con error 3: producto no pesable
- Mensaje corto: "Hace falta completar esta información."
- Acción sugerida: completar, cancelar o volver.

### Ruta offline
- Mostrar que la operación local está guardada.
- Mostrar si se puede seguir operando.
- Mostrar pendientes sin palabras técnicas.


## Food truck / punto móvil de comida

### Ruta feliz
1. El operador entra a **Vender**.
2. Ejecuta el gesto principal del giro: pedido rápido, menú limitado, cobro, estado offline, corte por ubicación o evento.
3. Corrige errores simples sin salir del flujo.
4. Pasa a cobro o cierre operativo.
5. Recibe confirmación clara.
6. Si no hay conexión, la operación queda como pendiente por enviar.

### Ruta con error 1: menú agotado
- Mensaje corto: "No se puede continuar: menú agotado."
- Acción sugerida: volver a la pantalla principal o corregir el dato.
- No usar lenguaje técnico.

### Ruta con error 2: sin conexión
- Mensaje corto: "Revisa este dato antes de continuar."
- Acción sugerida: cambiar cantidad, elegir otra opción o pedir autorización.

### Ruta con error 3: ubicación sin abrir
- Mensaje corto: "Hace falta completar esta información."
- Acción sugerida: completar, cancelar o volver.

### Ruta offline
- Mostrar que la operación local está guardada.
- Mostrar si se puede seguir operando.
- Mostrar pendientes sin palabras técnicas.
