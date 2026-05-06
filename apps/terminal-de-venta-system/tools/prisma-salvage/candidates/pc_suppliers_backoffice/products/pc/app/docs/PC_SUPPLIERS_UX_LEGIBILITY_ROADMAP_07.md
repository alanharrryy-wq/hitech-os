# PRISMA PC Proveedores UX Legibility Roadmap 07

## Objetivo

Convertir `/proveedores` en una pantalla demo-presentable: recomendaciones legibles, razones en acordeón premium, checklist de confianza, agenda agrupada por día y auditoría como roadmap visual.

## Alcance

- Solo PC.
- Solo módulo Proveedores / Compra Inteligente.
- No toca Tablet.
- No toca shared-kernel.
- No introduce persistencia nueva.

## Cambios visibles

1. Cards de recomendación con jerarquía clara.
2. Productos sugeridos en filas separadas con SKU, existencia, cobertura, cantidad sugerida y costo.
3. Acordeón dorado: `¿POR QUÉ PRISMA LO RECOMIENDA?`.
4. Criterios de confianza como checklist visual.
5. Calendario como timeline por día.
6. Auditoría como roadmap: recomendación -> pedido -> recepción -> pago -> evidencia.
7. Limpieza de copy visible: sin `safe`, `blocked`, `order_cutoff`, `expected_receiving`, `sync`, `ingest` o `backoffice` en UI de Proveedores.

## Validación visual recomendada

Abrir:

```text
http://127.0.0.1:3130/proveedores
```

Validar a zoom 100%, 125% y 150%:

- no hay texto pegado entre números y etiquetas;
- los productos se entienden por fila/card;
- el acordeón dorado invita a abrir razones;
- el calendario se lee por día;
- la auditoría cuenta la historia de decisión.
