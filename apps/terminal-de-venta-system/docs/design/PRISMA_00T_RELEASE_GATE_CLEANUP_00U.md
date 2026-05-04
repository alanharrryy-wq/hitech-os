# PRISMA 00T Release Gate Cleanup 00U

## Objetivo

Cerrar los puntos fragiles detectados por `prisma_show_pos_scan_260504_1149.json` antes de empaquetar `PRISMA_VISUAL_OS_POS_LIVE_BINDING_SAFE_00T_v02`.

## Decision

00T queda canonizado como **live listener no-layout**:

- POS puede escuchar Visual OS.
- POS puede recibir payloads `prisma.visual.controls` para `tablet_pos`.
- POS puede exponer un badge pasivo 00T.
- POS no debe aplicar CSS live que mueva layout, escala, paneles, ticket, carrito o boton COBRAR.

## Cambios

1. Reemplaza `pos-live-binding.tsx` por una version segura:
   - `new EventSource("http://127.0.0.1:4177/events")`
   - filtro `payload.surface !== "tablet_pos"`
   - `setProperty` solo para variables `--prisma-live-*`
   - badge inline con `pointerEvents: "none"`

2. Limpia `pos.module.css` de bloques 00T agresivos:
   - elimina `PRISMA Visual OS 00T - POS Live Binding`
   - elimina `PRISMA 00T POS500 SAFE LIVE POS MAPPING`
   - elimina `PRISMA 00T AUTOPILOT HARD GLOBAL POS MAPPING`
   - elimina `PRISMA 00T HARD LIVE POS MAPPING`
   - elimina `FORCE VISIBLE LIVE POS MAPPING`
   - conserva/agrega `PRISMA 00T SAFE NO-LAYOUT LIVE MARKER`

3. Corrige verificadores:
   - `verify_prisma_visual_os_pos_live_binding_00t.mjs` acepta el binding SSE real.
   - `verify_pos_golden_flow_hold_carts_04g.mjs` detecta correctamente `products/tablet/app`.
   - `verify_pos_touch_only_actions_04h.mjs` detecta correctamente `products/tablet/app`.

## Validacion critica

El instalador doctor ejecuta:

- validacion de zip y checksums
- backup previo
- verificacion estatica de binding, CSS y verificadores
- `node tools/prisma-visual-os/verify_prisma_visual_os_pos_live_binding_00t.mjs`
- pruebas HTTP de `/pos`, `/visual-os/pro`, `/visual-os/realtime`
- health de realtime `http://127.0.0.1:4177/health`
- broadcast neutral no-layout

## No objetivos

- No mete efectos visuales nuevos.
- No cambia layout POS.
- No toca shared-kernel.
- No toca contratos PC/Tablet.
- No arregla bugs funcionales no relacionados con release gate 00T.
