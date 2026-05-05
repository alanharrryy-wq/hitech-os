# PRISMA Tablet POS Touch Only Actions 04H Fix 00V

## Objetivo

Cerrar el gate `verify_pos_touch_only_actions_04h.mjs` sin tocar Visual OS 00T, realtime ni layout live.

## Decisión

El POS conserva operación touch-first explícita:

- no usa `PosPaymentKeyboardBridge`;
- no muestra teclas de función como acción principal;
- marca `pos-screen.tsx` con `data-prisma-golden-flow="touch-only-actions-04h"` mediante marker oculto no intrusivo;
- mantiene el CTA de checkout como botón táctil visible;
- conserva `COBRAR` y agrega señal de acción táctil `Tocar`;
- mantiene recuperación de tickets guardados como acción explícita.

## Fuera de alcance

- No modifica `pos-live-binding.tsx`.
- No modifica `pos.module.css`.
- No modifica Visual OS 00T.
- No modifica el realtime server.
