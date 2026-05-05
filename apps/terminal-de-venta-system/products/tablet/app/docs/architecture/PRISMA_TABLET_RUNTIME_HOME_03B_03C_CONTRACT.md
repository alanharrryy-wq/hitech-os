# PRISMA Tablet Runtime + Home 03B/03C - Contrato técnico

## 1. Decisión de producto

Home y Shell deben consumir la misma lectura operativa. El operador no debe ver un estado en la barra superior y otro en la pantalla principal. Eso produce errores de caja, dudas de turno y ventas hechas con el sistema pensando una cosa y la persona otra.

## 2. Contrato de snapshot

El contrato 03B contiene identidad, turno, conexión, catálogo, ventas, capacidades y advertencias. No reemplaza la base de datos ni inventa una sincronización nueva. Sólo ordena la lectura que ya necesita la operación diaria.

## 3. Shell

La shell muestra navegación de seis entradas y chips de estado. Vender conserva peso visual principal. Las rutas secundarias siguen existiendo, pero no compiten con el menú principal.

## 4. Home

Home 03C usa el snapshot para calcular CTA principal, métricas, alertas y checklist. Si el turno está cerrado manda a abrir turno. Si hay pendientes manda a revisarlos. Si todo está listo manda a vender.

## 5. API

El endpoint /api/tablet/runtime/snapshot permite consultar el estado operativo sin abrir DevTools. Devuelve ok/data/meta con el formato ya usado por las APIs POS.

## 6. DB y Prisma

El paquete consulta modelos existentes: Business, Terminal, CashSession, Product, StockMovement, OutboxEvent y Sale mediante el resumen de ventas existente. No modifica schema.prisma.

## 7. Frontera twin

No toca PC, Mobile ni shared-kernel. Tampoco mete proveedores, compras ni recepción formal en Tablet. La Tablet debe vender sola, no convertirse en backoffice con pantalla táctil.

## 8. Verificación

El verificador principal valida archivos, navegación, snapshot, Home y copy visible. El verificador profundo revisa contratos, CSS, rutas alias, escenarios, duplicidad sospechosa y superficies bloqueadas.

## 9. Riesgos

El riesgo principal es que una pantalla futura ignore el snapshot y vuelva a inventar estado local. La mitigación es exigir que Home, Shell y pantallas principales acepten o consuman TabletRuntimeSnapshot.

## 10. Siguiente entrega

La siguiente entrega natural es PRISMA_TABLET_SELL_CART_03D: usar el mismo estado operativo para endurecer carrito, totales, bloqueo de cobro y preparación de confirmación.

## 11. Archivos instalados por responsabilidad

### UI visible

```text
components/tablet-shell/prisma-tablet-shell.tsx
components/tablet-shell/tablet-nav.ts
components/tablet-shell/prisma-tablet-shell.module.css
components/tablet-runtime/tablet-runtime-status-strip.tsx
components/tablet-runtime/tablet-runtime-panel.tsx
components/tablet-home/tablet-home-screen.tsx
components/tablet-home/tablet-home.module.css
```

### Contratos cliente

```text
src/lib/tablet-runtime-snapshot/shell-contract.ts
src/lib/tablet-runtime-snapshot/view-model.ts
src/lib/tablet-runtime-snapshot/visible-copy.ts
src/lib/tablet-home/home-view-model.ts
```

### Servidor

```text
src/server/tablet-runtime-snapshot/index.ts
src/server/tablet-runtime-snapshot/env.ts
src/server/tablet-runtime-snapshot/build.ts
src/server/tablet-runtime-snapshot/queries.prisma.ts
src/server/tablet-runtime-snapshot/types.ts
```

### Rutas

```text
app/page.tsx
app/api/tablet/runtime/snapshot/route.ts
app/inventory/page.tsx
app/existencias/page.tsx
app/runtime-snapshot-preview/page.tsx
```

## 12. Estados visibles aprobados

```text
Turno abierto
Turno cerrado
Cerrando turno
Revisar turno
En linea
Sin conexion
Pendientes por enviar
Revisar pendientes
Catalogo listo
Catalogo vacio
Revisar catalogo
Revisar existencias
```

## 13. Términos prohibidos en UI visible

```text
outbox
runtime
payload
schema
mutation
query
lookup
amountCents
terminalId
businessId
undefined
null
NaN
fatal
```

## 14. Razón de esta arquitectura

La Tablet necesita velocidad. Un POS que pregunta demasiado antes de vender parece empleado nuevo en hora pico. Pero también necesita seguridad: turno, pendientes y catálogo no pueden estar escondidos. El snapshot permite mostrar seguridad sin convertir la interfaz en una libreta de auditoría.

## 15. Criterio profesional

Este paquete no existe para decorar. Existe para que las siguientes pantallas no vuelvan a pelearse por estados globales. Home 03C queda como consumidor de referencia. Shell queda como expositor permanente. La API queda como diagnóstico. Los verificadores quedan como portero del antro: si no cumples, no pasas.


## 16. Matriz de aceptación funcional

| Caso | Resultado esperado | Motivo |
|---|---|---|
| Turno cerrado | Home debe mostrar Abrir turno como CTA dominante | Evita vender con caja sin contexto |
| Turno abierto | Home debe mostrar Ir a vender como CTA natural | Reduce fricción del cajero |
| Pendientes > 0 | Shell y Home deben señalar Pendientes por enviar | No es bloqueo de venta, sí es señal operativa |
| Productos activos = 0 | Home debe pedir revisar catálogo | Sin catálogo vender es teatro |
| Stock presionado | Home debe mandar a Existencias | Evita prometer producto que no hay |
| Ruta /inventory | Debe redirigir a /stock | Compatibilidad sin duplicar pantalla |
| Ruta /existencias | Debe redirigir a /stock | Compatibilidad en español |
| PC caído | Snapshot conserva localSalesAllowed=true | Tablet no pide permiso para vender |

## 17. Notas para implementación futura

- 03D debe tomar `snapshot.shift.state` para decidir si muestra advertencia de turno antes de cobrar.
- 03E debe usar `snapshot.localSalesAllowed` para no depender de PC al confirmar venta.
- 03F debe mostrar estado pendiente cuando la venta cierre localmente pero queden eventos por enviar.
- 03G debe usar la misma fecha del snapshot para evitar que Ventas de hoy y Home calculen días distintos.
- 03M debe reemplazar lenguaje técnico por Pendientes por enviar y Revisar pendientes.
