# Release note - PC I04 Operación

## Entrega

`install_pc_i04_operacion.py` genera localmente `pc_i04_operacion.zip` e instala compras, recepción, reabasto y dashboard KPI formal dentro de `products/pc/app/**`.

## Cambio funcional

- `/purchasing` deja de ser overview y muestra órdenes con pendientes y riesgo.
- `/receiving` muestra recepciones contra orden y discrepancias.
- `/replenishment` muestra señales con prioridad, stock, min/max y sugerido.
- `/dashboard` muestra KPIs con fórmula, fuente, confianza y rango.

## No alcance

- No hace sync completo.
- No migra DB.
- No escribe en Tablet.
- No toca contratos compartidos.
