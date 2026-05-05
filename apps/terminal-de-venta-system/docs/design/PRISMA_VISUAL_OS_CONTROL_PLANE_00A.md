
# PRISMA Visual Operating System - Control Plane 00A

**Paquete:** `PRISMA_VISUAL_OS_CONTROL_PLANE_00A_20260503_v01`  
**Estado:** Foundation / governance, sin mutación visual obligatoria  
**Raíz destino:** `F:\repos\hitech-os\apps\terminal-de-venta-system`  
**Propósito:** convertir la evolución visual de PRISMA en sistema gobernado.

## 1. Decisión

PRISMA no se debe refinar pantalla por pantalla. A partir de este paquete, el refinamiento visual debe pasar por:

1. **Perillas maestras**: pocas, potentes, con rangos cerrados.
2. **Presets oficiales**: Black, Light, Dual y variantes por superficie.
3. **Recetas de componente**: cada familia visual consume las mismas reglas.
4. **Score operativo**: una pantalla no pasa sólo por verse fina; pasa si conserva lectura, jerarquía y velocidad.
5. **Evidencia**: cada futura inyección visual debe dejar reporte y, cuando aplique, captura.

## 2. Lo que este paquete NO hace

- No toca `pos.module.css`.
- No toca `prisma-tablet-shell.module.css`.
- No modifica rutas Next.
- No toca backend.
- No cambia shared-kernel.
- No aplica el preset final de la referencia todavía.

Esto es intencional. Primero se instala el tablero de control; después se mueve la maquinaria. Así se evita el clásico ritual humano de “ajusto 14 sombras a ojo y luego no sé qué rompí”.

## 3. Perillas maestras 00A

| Perilla | Función | Motivo operativo |
|---|---|---|
| `brand_tone` | Regula premium / operativo / híbrido | Evita que cada pantalla tenga personalidad de primo distinto |
| `surface_density` | Regula compactación | Tablet requiere touch; PC requiere densidad |
| `operational_contrast` | Regula lectura | Prioriza caja, total, stock y errores |
| `depth_glass` | Regula blur, glass, sombras | Mantiene lujo sin ahogar contenido |
| `commercial_emphasis` | Decide foco: producto, carrito, acción, datos | El POS debe guiar la venta |
| `motion_temper` | Controla movimiento | Animación útil, no gelatina visual |
| `touch_safety` | Tamaños mínimos de interacción | Reduce error de toque |
| `data_legibility` | Fuerza de números y metadata | Stock, precio y total no se esconden |
| `critical_action_weight` | Peso visual de acciones finales | COBRAR y decisiones críticas mandan |
| `ambient_noise` | Textura, niebla, viñeta | Fondo acompaña, no compite |
| `state_signal_strength` | Estados de error/sync/offline | Ningún flujo queda mudo |
| `surface_separation` | Distancia visual entre capas | Evita sopa de vidrio encima de vidrio |

## 4. Presets oficiales

- `BLACK_PREMIUM`: impacto oscuro, glass profundo, oro cálido, drama controlado.
- `LIGHT_OPERATIONAL`: claridad para soporte, WhatsApp, tutorial y uso de día.
- `DUAL_BALANCE`: mezcla comercial con operación seria.
- `POS_TOUCH_REFERENCE`: Tablet POS, énfasis en producto-carrito-cobro.
- `PC_DENSE_ADMIN`: backoffice, tablas, KPI, filtros y gobierno.
- `MOBILE_PULSE`: lectura rápida desde celular, alertas, resumen y foco ejecutivo.

## 5. Reglas de adopción

### 5.1 Tablet `/pos`

La primera adopción visual real debe tocar, en orden:

1. shell / escena,
2. buscador,
3. card de producto,
4. carrito,
5. botón cobrar,
6. estados.

### 5.2 PC

PC debe adoptar tokens con más densidad y menos teatralidad. PC gobierna; no necesita parecer sala VIP de nave espacial para editar un proveedor.

### 5.3 Mobile

Mobile debe conservar la idea de pulso rápido: poco texto, señales claras, acciones de supervisión.

## 6. Score operativo

Cada futura entrega visual debe calificarse en:

- `premium_fit`
- `clarity`
- `task_speed`
- `hierarchy`
- `consistency`
- `touch_safety`
- `state_visibility`
- `risk`

Una pantalla queda bloqueada si baja claridad o seguridad táctil por perseguir brillo. PRISMA no necesita vape shop con inventario; necesita herramienta de negocio con presencia.

## 7. Archivos instalados

- `products/shared-ui/prisma/visual-os/prisma-visual-os.controls.json`
- `products/shared-ui/prisma/visual-os/prisma-visual-os.presets.json`
- `products/shared-ui/prisma/visual-os/prisma-visual-os.recipes.json`
- `products/shared-ui/prisma/visual-os/prisma-visual-os.scorecard.json`
- `products/shared-ui/prisma/visual-os/prisma-visual-os.tokens.css`
- `products/shared-ui/prisma/visual-os/README.md`
- `tools/prisma-visual-os/verify_prisma_visual_os_control_plane_00a.mjs`
- `tools/prisma-visual-os/score_prisma_visual_os_00a.mjs`
- `tools/prisma-visual-os/README.md`
- `docs/design/PRISMA_VISUAL_OS_CONTROL_PLANE_00A.md`
- `manifests/PRISMA_VISUAL_OS_CONTROL_PLANE_00A.manifest.json`

## 8. Criterio de salida

00A se considera correcto si:

- todos los JSON parsean,
- no hay controles duplicados,
- todos los presets referencian controles existentes,
- todas las recetas usan controles existentes,
- el CSS contract contiene las variables oficiales,
- el score runner genera reporte,
- no se toca código de venta, backend ni shared-kernel.
