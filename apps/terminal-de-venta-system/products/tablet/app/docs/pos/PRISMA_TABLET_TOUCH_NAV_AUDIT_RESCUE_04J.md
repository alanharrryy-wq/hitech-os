# PRISMA Tablet Touch Nav Audit Rescue 04J

## Objetivo

Cerrar el estado parcial detectado por auditoría después de 04H/04I.

## Correcciones

- Mantiene el flujo POS touch-only: sin puente de teclado `PosPaymentKeyboardBridge`.
- Reescribe `pos-screen.tsx` y `pos-ticket-panel.tsx` con acciones táctiles.
- Reescribe el shell Tablet para usar navegación guiada por estado de flujo.
- Reescribe `tablet-nav.ts` con metadata contextual: `TabletFlowStage`, `getVisibleTabletNavItems`, `getTabletFlowCopy`.
- Elimina `products/tablet/app/components/pos/pos-payment-keyboard-bridge.tsx` si aún existe.

## Criterio de aceptación

- El sidebar en `/` muestra solo Inicio.
- `/pos` muestra navegación mínima de operación.
- Catálogo y Existencias no aparecen como menú default desde inicio.
- No hay copys F2/F3/F4/F5/F6 en el ticket POS.
- No existe ni se monta `PosPaymentKeyboardBridge`.
