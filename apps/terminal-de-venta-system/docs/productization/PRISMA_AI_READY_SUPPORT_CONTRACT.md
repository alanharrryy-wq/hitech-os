---
title: PRISMA AI Ready Support Contract
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA AI Ready Support Contract

## 1. Decisión

PRISMA debe preparar desde ahora la estructura para IA futura, sin meter IA en el corazón transaccional de venta.

La IA futura debe vivir en soporte, explicación, resumen, búsqueda y sugerencias; no en cierre de venta, stock ni licencia crítica.

## 2. Modos

| Modo | Permitido |
|---|---|
| read_only | leer contexto autorizado y responder |
| suggest_actions | proponer acciones sin ejecutar |
| draft_response | redactar respuesta para proveedor o cliente |
| execute_approved_actions | futuro, solo con aprobación explícita |

## 3. Contexto autorizado

- versión,
- plan,
- mensajes,
- ticket,
- errores saneados,
- estado sync,
- estado outbox,
- plugins,
- KPIs agregados si el cliente permite.

## 4. Contexto prohibido por defecto

- contraseñas,
- tokens,
- claves,
- datos bancarios,
- DB completa,
- información personal innecesaria,
- comandos arbitrarios.

## 5. Casos de uso futuros

- explicar errores,
- guiar instalación,
- resumir ticket,
- revisar health report,
- sugerir reabasto,
- explicar KPIs,
- detectar productos sin barcode,
- redactar respuesta de soporte,
- clasificar mensajes.

## 6. Reglas

1. IA no debe cerrar ventas.
2. IA no debe modificar stock sin aprobación.
3. IA no debe cambiar precios sin aprobación.
4. IA no debe activar licencias.
5. IA no debe instalar plugins sola.
6. IA no debe procesar pagos.
7. IA debe citar contexto interno cuando aplique.

## 7. Preparación técnica

Crear datos estructurados desde ahora:

```text
support tickets
message threads
diagnostic bundles
health summaries
announcement logs
feature states
plugin manifests
```

## 8. Criterio de aceptación

La IA futura debe ser copiloto, no cajero borracho con permisos de admin.
