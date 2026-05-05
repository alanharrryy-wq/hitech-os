# PRISMA POS Golden Flow 01 - Acceptance Matrix

**Version:** 01  
**Fecha:** 2026-05-03  
**Uso:** checklist de aceptacion para la siguiente inyeccion de `/pos`.

---

## 1. Ready / blocked

| Area | Criterio | Ready cuando |
|---|---|---|
| Captura | Barcode/SKU/nombre | Producto se agrega sin navegar fuera de venta |
| Carrito | Ticket visible | El ticket no desaparece al buscar o agregar |
| Cantidad | Escaneo repetido | Incrementa cantidad, no duplica lineas |
| Validacion | Producto inactivo | Bloquea venta con mensaje claro |
| Validacion | Stock insuficiente | Bloquea o pide override segun politica |
| Cobro | Efectivo | Calcula cambio y cierra ticket |
| Evento | Outbox | Cada venta cerrada deja evento pendiente/enviado |
| Stock | Descuento local | El inventario baja al cerrar venta |
| Reporte | Venta del dia | La venta aparece en resumen operativo |
| UX | Errores | No aparece `[object Object]` ni errores mudos |
| Offline | Venta permitida | La venta basica no depende de PC |

---

## 2. Prueba manual minima

1. Abrir Tablet POS.
2. Confirmar caja/turno abierto.
3. Buscar producto por nombre.
4. Agregar al carrito.
5. Escanear o resolver un codigo/SKU.
6. Confirmar que aumenta cantidad si ya existe.
7. Intentar cobrar con carrito valido.
8. Confirmar ticket cerrado.
9. Confirmar stock descontado.
10. Confirmar outbox/evento creado.
11. Confirmar resumen del dia actualizado.

---

## 3. Prueba de error minima

1. Buscar producto inexistente.
2. Intentar vender producto inactivo.
3. Intentar vender mas piezas que stock disponible.
4. Intentar cobrar carrito vacio.
5. Simular sync pendiente.

Resultado esperado: cada caso muestra mensaje claro en es-MX y no rompe la pantalla.

---

## 4. Smoke tecnico sugerido

```text
pnpm run typecheck
node tools/verify_pos_engine_01a.mjs
node tools/verify_pos_api_01b.mjs
node tools/verify_pos_events_reports_01d.mjs
```

Si alguna prueba no existe en la base instalada, registrar como pendiente y no fingir que paso. Mentir en QA es barrer cucarachas debajo del tapete: funciona hasta que prendes la luz.
