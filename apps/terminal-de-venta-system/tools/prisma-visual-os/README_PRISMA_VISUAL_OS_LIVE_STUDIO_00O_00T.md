# PRISMA Visual OS / Live Studio Pro — README operativo canon

**Fecha de corte:** 2026-05-04  
**Proyecto:** PRISMA POS / Terminal de Venta System  
**Raíz repo:** `F:\repos\hitech-os`  
**Raíz sistema:** `F:\repos\hitech-os\apps\terminal-de-venta-system`  
**Tablet app:** `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app`  
**Logs y reportes:** `F:\descargasf`  
**Estado canon:** `00T safe-no-layout + 00U doctor + 00V touch-only`

---

## 1. Resumen ejecutivo

PRISMA Visual OS ya tiene una cabina operativa viva para controlar y diagnosticar la experiencia visual del POS sin convertir el checkout en feria de neón.

Estado actual confirmado:

- `/visual-os` responde.
- `/visual-os/pro` responde.
- `/visual-os/realtime` responde.
- `/pos` responde.
- El servidor realtime `4177` responde.
- El POS mantiene `COBRAR` visible.
- El POS mantiene CTA táctil con señal `Tocar`.
- `00T` pasa como **safe-no-layout**.
- `00U` instala un doctor permanente en repo.
- `00V` deja cerrado el gate touch-only `04H`.

La regla madre queda así:

> Visual OS puede escuchar, diagnosticar y emitir controles.  
> POS puede recibir estado vivo.  
> POS no acepta CSS live que mueva layout, tape cobro o cambie geometría operativa.

Dicho a pie de banqueta: sí a luces con dimmer; no a mover el mostrador mientras el cajero cobra.

---

## 2. Estado canon por bloque

| Bloque | Nombre | Estado actual |
|---|---|---|
| `00R/00S` | Studio Pro + QA | OK |
| `00T` | POS live binding | OK en modo `safe-no-layout` |
| `00U` | Show POS Doctor | OK, instalado en repo |
| `00V` | Touch-only POS fix | OK, `04H` pasa |
| `/pos` | Ruta POS | OK, `200`, `COBRAR` y `Tocar` visibles |
| Realtime | `4177` | OK |

---

## 3. Arquitectura operativa actual

```text
Visual OS Studio Pro
  -> emite payload prisma.visual.controls
    -> realtime server 4177
      -> POS live binding 00T escucha /events
        -> documentElement recibe variables y dataset
          -> POS conserva layout operativo
```

El binding POS es deliberadamente conservador.

Puede:

```text
- abrir EventSource contra /events
- filtrar surface tablet_pos
- recibir payload prisma.visual.controls
- escribir CSS variables --prisma-live-*
- escribir dataset de estado
- mostrar badge diagnóstico discreto
```

No puede:

```text
- aplicar scale() al workspace POS
- aplicar backdrop-filter live al workspace POS
- mover grids o paneles de checkout
- tapar COBRAR
- exigir Visual OS para vender
- exigir PC para vender
```

---

## 4. Reglas de seguridad visual para POS

### Permitido

```text
color
border-color moderado
box-shadow moderado en componentes explícitos
badge diagnóstico
variables CSS disponibles
payload neutral de diagnóstico
```

### Prohibido en binding live POS

```text
scale()
transform agresivo
backdrop-filter sobre workspace
inset negativo grande
outline-offset grande
selectores genéricos section/article/aside/form/button/input
posWorkspace[data-prisma-pos-live="00T"] con mapeo visual fuerte
.posLiveBadge definido en CSS global agresivo
```

La UI POS es primero terminal de venta. El Visual OS no manda sobre el layout operativo.

---

## 5. Rutas principales

### 5.1 Visual OS / Studio

```text
products/tablet/app/app/visual-os/page.tsx
products/tablet/app/app/visual-os/pro/page.tsx
products/tablet/app/app/visual-os/realtime/page.tsx
products/tablet/app/app/visual-os/PrismaStudioProQaClient.tsx
products/tablet/app/app/visual-os/PrismaVisualStudioClient.tsx
products/tablet/app/app/visual-os/prisma-studio-pro-qa.module.css
```

### 5.2 Realtime

```text
products/tablet/app/src/visual-os/realtime/prisma-realtime-client.ts
tools/prisma-visual-os/live-preview-server-00q.mjs
```

### 5.3 POS live binding y checkout

```text
products/tablet/app/components/pos/pos-live-binding.tsx
products/tablet/app/components/pos/pos-screen.tsx
products/tablet/app/components/pos/pos-ticket-panel.tsx
products/tablet/app/components/pos/pos.module.css
```

### 5.4 Verificadores principales

```text
tools/prisma-visual-os/verify_prisma_visual_os_studio_pro_qa_00r_00s.mjs
tools/prisma-visual-os/verify_prisma_visual_os_pos_live_binding_00t.mjs
tools/prisma-visual-os/verify_prisma_show_pos_doctor_00u.mjs
tools/prisma-visual-os/verify_prisma_visual_os_readme_status_00w.mjs
products/tablet/app/tools/verify_pos_touch_only_actions_04h.mjs
products/tablet/app/tools/verify_prisma_tablet_pos_light_operational_00q.mjs
products/tablet/app/tools/verify_prisma_tablet_pos_real_checkout_flow_00r.mjs
products/tablet/app/tools/verify_prisma_tablet_pos_checkout_shift_autofix_00s.mjs
products/tablet/app/tools/verify_pos_golden_flow_hold_carts_04g.mjs
```

---

## 6. Doctor permanente 00U

El doctor vive en:

```text
tools/prisma-visual-os/doctor_prisma_show_pos_scan_00u.py
tools/prisma-visual-os/run_prisma_show_pos_doctor_00u.cmd
tools/prisma-visual-os/verify_prisma_show_pos_doctor_00u.mjs
```

Comando recomendado:

```powershell
F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma-visual-os\run_prisma_show_pos_doctor_00u.cmd
```

Salidas:

```text
F:\descargasf\prisma_show_pos_doctor_00u_YYMMDD_HHMM.log
F:\descargasf\prisma_show_pos_doctor_00u_YYMMDD_HHMM.json
```

El doctor debe usarse antes y después de cualquier paquete Visual OS que toque POS, realtime, Studio o checkout.

---

## 7. Gates mínimos antes de cerrar una ronda

Desde:

```powershell
cd F:\repos\hitech-os\apps\terminal-de-venta-system
```

Ejecutar:

```powershell
node tools\prisma-visual-os\verify_prisma_visual_os_pos_live_binding_00t.mjs
node tools\prisma-visual-os\verify_prisma_show_pos_doctor_00u.mjs
node tools\prisma-visual-os\verify_prisma_visual_os_readme_status_00w.mjs
node products\tablet\app\tools\verify_pos_touch_only_actions_04h.mjs
```

Validaciones runtime esperadas:

```text
GET http://127.0.0.1:3120/pos = 200
GET http://127.0.0.1:3120/visual-os/pro = 200
GET http://127.0.0.1:3120/visual-os/realtime = 200
GET http://127.0.0.1:4177/health = 200
/pos contiene COBRAR
/pos contiene Tocar
/pos no muestra Build Error
/pos no muestra Internal Server Error
```

---

## 8. Comandos operativos

### Levantar realtime

```powershell
cd F:\repos\hitech-os\apps\terminal-de-venta-system
node tools\prisma-visual-os\live-preview-server-00q.mjs --port 4177
```

### Levantar Tablet

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app dev
```

### URLs principales

```text
http://127.0.0.1:3120/visual-os
http://127.0.0.1:3120/visual-os/pro
http://127.0.0.1:3120/visual-os/realtime
http://127.0.0.1:3120/pos
http://127.0.0.1:4177/health
http://127.0.0.1:4177/state
```

---

## 9. Payload neutral seguro

Este payload sirve para probar realtime sin alterar layout:

```json
{
  "type": "prisma.visual.controls",
  "sourceClientId": "manual-readme-neutral-test",
  "surface": "tablet_pos",
  "recipeName": "POS_README_NEUTRAL_NO_LAYOUT",
  "liveEnabled": true,
  "debugLayers": false,
  "mode": "readme-neutral-no-layout",
  "cssVars": {
    "--prisma-live-glass": "0",
    "--prisma-live-blur": "0px",
    "--prisma-live-panel-alpha": "1",
    "--prisma-live-glow": "none",
    "--prisma-live-neon": "none",
    "--prisma-live-depth": "0",
    "--prisma-live-contrast": "0",
    "--prisma-live-density": "0",
    "--prisma-live-motion": "0",
    "--prisma-live-radius": "0px",
    "--prisma-live-shadow": "none",
    "--prisma-live-saturation": "100%",
    "--prisma-live-shine": "0",
    "--prisma-live-grain": "0",
    "--prisma-live-edge": "transparent"
  },
  "score": {
    "overall": 0,
    "verdict": "neutral_no_layout"
  }
}
```

---

## 10. Estados aceptados

### Estado saludable

```text
00T = VERIFY OK, mode safe-no-layout
00U = VERIFY OK
00V / 04H = ok true
00W = README status instalado y verificado
/pos = 200 + COBRAR + Tocar
realtime = 200
warnings = sólo logs históricos, no runtime activo
```

### Estado bloqueado

```text
/pos 500
Build Error
Internal Server Error
verify 00T falla
verify 04H falla
CSS live contiene bloque agresivo 00T
COBRAR no aparece
Tocar no aparece
realtime /health falla
```

---

## 11. Historial reciente canon

### 00T Safe No-Layout

Deja el POS con listener realtime vivo sin CSS destructivo sobre layout.

### 00U Doctor

Instala doctor permanente dentro de `tools/prisma-visual-os` y deja `F:\descargasf` sólo para logs/reportes.

### 00V Touch Only

Cierra el gate `04H`: POS marcado touch-only, sin keyboard bridge visible, CTA de checkout táctil, `COBRAR` y `Tocar` presentes.

### 00W README Status

Actualiza este README y agrega verificador documental para que la documentación ya no describa el estado viejo de 00T como pendiente.

---

## 12. Qué NO hacer

No volver a usar el bomb test como calibración real.

No reintroducir:

```css
.posWorkspace[data-prisma-pos-live="00T"] :global(section),
.posWorkspace[data-prisma-pos-live="00T"] :global(article),
.posWorkspace[data-prisma-pos-live="00T"] :global(aside),
.posWorkspace[data-prisma-pos-live="00T"] :global(form),
.posWorkspace[data-prisma-pos-live="00T"] :global(button)
```

No reintroducir:

```css
scale(...)
backdrop-filter: blur(...)
outline-offset: 8px
inset: -18px
box-shadow gigante en contenedor raíz
```

El show visual puede decorar. No puede secuestrar la operación.

---

## 13. Siguiente movimiento recomendado

Con `00T`, `00U`, `00V` y `00W` cerrados, el siguiente trabajo ya puede moverse a una de estas rutas:

1. Captura visual comparativa con doctor antes/después.
2. Pulido visual controlado sólo en componentes explícitos, no workspace root.
3. Consolidación de release POS Visual OS como base canon.
4. Empaquetar una ronda de QA visual con screenshots.

No avanzar a visual fuerte sin correr el doctor primero.

---

## 14. Conclusión

Visual OS ya no está en etapa “a ver si prende”. Prende.

El punto ahora es mantenerlo gobernado:

```text
Studio controla.
Realtime comunica.
00T escucha sin mover layout.
00U diagnostica.
00V asegura touch.
00W documenta el estado real.
POS vende.
```

Si alguien vuelve a meter CSS agresivo al POS, el doctor y los gates deben delatarlo antes de que el cajero termine vendiendo refrescos desde una pantalla convertida en antro de ciencia ficción.
