# PRISMA Visual OS 00T - POS Live Binding

## Objetivo

Conectar el Studio Pro + QA con la pantalla real `/pos` para que Tablet POS escuche el broadcast SSE y aplique variables visuales en vivo sin editar CSS manual.

## Qué instala

- `products/tablet/app/components/pos/pos-live-binding.tsx`
- `products/tablet/app/components/pos/pos-screen.tsx`
- `products/tablet/app/components/pos/pos.module.css`
- `tools/prisma-visual-os/verify_prisma_visual_os_pos_live_binding_00t.mjs`

## Cómo funciona

1. `PosLiveBinding` se monta dentro de `PosScreen`.
2. Se conecta al servidor realtime en `http://127.0.0.1:4177` usando `EventSource`.
3. Sólo acepta payloads con `surface = tablet_pos`.
4. Aplica `cssVars` sobre `document.documentElement` usando el runtime existente.
5. `pos.module.css` traduce esas variables a glass, blur, glow, neón, profundidad, contraste y acción visual dentro de `/pos`.

## Guardrails

- No toca `packages/shared-kernel/*`.
- No toca `shared/contracts/*`.
- No toca `shared/TWIN_CHAT_SHARED_CONTEXT_6.1.json`.
- Si el servidor realtime no está arriba, `/pos` sigue funcionando con fallback visual.

## Verificación

```powershell
cd F:epos\hitech-ospps	erminal-de-venta-system
node tools\prisma-visual-oserify_prisma_visual_os_pos_live_binding_00t.mjs
```

## Prueba manual

1. Arrancar realtime:

```powershell
node tools\prisma-visual-os\live-preview-server-00q.mjs --port 4177
```

2. Abrir Studio:

```text
http://127.0.0.1:3120/visual-os/pro
```

3. Abrir POS:

```text
http://127.0.0.1:3120/pos
```

4. Mover sliders en Studio. `/pos` debe cambiar blur, glow, glass, shadow, radius y contraste en vivo.
