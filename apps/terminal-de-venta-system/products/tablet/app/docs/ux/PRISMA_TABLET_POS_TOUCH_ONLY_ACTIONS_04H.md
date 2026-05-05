# PRISMA Tablet POS - Touch Only Actions 04H

**Paquete:** PRISMA_TABLET_POS_TOUCH_ONLY_ACTIONS_04H_20260503_v01
**Superficie:** Tablet POS / Vender
**Tipo:** refinamiento funcional touch-first
**No toca:** PC, shared-kernel, Prisma schema ni contratos twin.

## 1. Decisión

La Tablet no debe comunicar operación primaria con teclas de función. En una pantalla touch el flujo debe hablar en acciones táctiles visibles: cobrar, guardar, limpiar y recuperar.

La iteración 04G dejó buena base con tickets guardados, pero conservó copys tipo F2, F3, F4, F5 y F6. Eso sirve para PC o teclado físico; en Tablet se siente como instructivo pegado en microondas de fonda: técnicamente dice algo, pero no pertenece ahí.

## 2. Cambios de esta ronda

- Se elimina el puente de teclado `PosPaymentKeyboardBridge`.
- Se desmontan los listeners globales de `keydown` en `/pos`.
- Se retiran etiquetas visibles F2/F3/F4/F5/F6 del ticket real.
- Se retiran etiquetas visibles F2/F3/F4/F5 de la referencia `prisma-dark-pos`.
- El CTA principal queda como acción táctil: `COBRAR` con indicador `Tocar`.
- Acciones secundarias quedan expresadas como botones touch: `Cotización`, `Guardar`, `Limpiar`.
- La recuperación de tickets guardados queda como botón explícito `Recuperar` dentro de cada tarjeta.

## 3. Contrato UX

| Acción | Control touch | Regla |
|---|---|---|
| Cobrar | Botón grande `COBRAR` | solo activo con ticket válido |
| Guardar ticket | Botón `Guardar` | requiere ticket activo |
| Limpiar ticket | Botón `Limpiar` | requiere ticket activo |
| Recuperar ticket | Botón `Recuperar` en tarjeta guardada | bloqueado si ya hay ticket activo |
| Cotización | Botón visible deshabilitado | reservado para siguiente bloque |

## 4. Criterio visual

El cajero no debe leer una tecla. Debe ver una acción. La interfaz debe funcionar como mostrador real: dedo, mirada, confirmación.

## 5. Riesgo controlado

Este paquete no cambia la lógica de guardado ni el almacenamiento local de tickets. Solo corrige la superficie de interacción para Tablet y elimina el listener de teclado que no pertenece a este dispositivo.
