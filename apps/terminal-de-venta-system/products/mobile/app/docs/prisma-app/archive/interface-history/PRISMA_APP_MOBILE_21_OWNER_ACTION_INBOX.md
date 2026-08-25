# PRISMA App Mobile 21 - Owner Action Inbox

## Objetivo

Agregar una bandeja móvil de acciones para el dueño, derivada del snapshot operativo y del Centro de Mando v20.

La intención no es crear otro dashboard de vanidad. Esta capa convierte señales de caja, inventario, sucursal, alertas y datos conectados en acciones concretas con responsable, evidencia, prioridad y vencimiento operativo.

## Archivos principales

- `src/lib/prisma-app/prisma-mobile-action-inbox.ts`: motor puro de priorización.
- `src/components/prisma-app/PrismaMobileActionInbox.tsx`: interfaz móvil premium.
- `app/api/mobile/action-inbox/route.ts`: endpoint no-store para inspección externa.
- `tools/verify_prisma_app_mobile_21_owner_action_inbox.mjs`: gate local.

## Criterios de salida

- La App móvil muestra la bandeja después del Centro de Mando.
- Cada acción visible incluye responsable, evidencia, prioridad y vencimiento práctico.
- No aparecen referencias visibles a demo, mock, TODO ni fixture sintético.
- El endpoint `/api/mobile/action-inbox` responde con contrato `PRISMA_APP_MOBILE_21_OWNER_ACTION_INBOX`.
- `pnpm run verify:action-inbox` pasa desde `products/mobile/app`.

## Riesgo controlado

No toca Tablet, PC, shared-kernel ni contratos de sincronización. Consume el snapshot móvil existente y lo ordena para decisión rápida.
