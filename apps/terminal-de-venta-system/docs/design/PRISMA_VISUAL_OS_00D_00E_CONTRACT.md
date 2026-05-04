# PRISMA Visual OS 00D/00E Contract

**Paquete:** `PRISMA_VISUAL_OS_CORE_00D_00E_20260503_v01`  
**Dueño:** Chat A  
**Raíz destino:** `F:\repos\hitech-os\apps\terminal-de-venta-system`

## Decisión

Este paquete convierte el Visual OS de PRISMA en un sistema con dos piezas reales:

1. **00D Visual Layers System:** define las capas oficiales donde vive cada efecto visual.
2. **00E Visual Controls Runtime:** define el archivo activo de perillas y genera CSS consumible por Tablet, PC y Mobile.

No rediseña pantallas. No toca negocio. No toca `packages/shared-kernel` ni contratos twin.

## Contrato público para otros chats

Otros frentes pueden depender de estos archivos:

```text
config/prisma-visual-os/prisma-visual-controls.active.json
styles/prisma-visual-os/prisma-visual-layers.css
styles/prisma-visual-os/prisma-visual-controls.generated.css
docs/design/PRISMA_VISUAL_OS_00D_00E_CONTRACT.md
```

Si estos archivos no existen, los paquetes posteriores deben declararse `BLOCKED_DEPENDENCY` y no aplicar cambios destructivos.

## Capas oficiales

| Layer | Uso | Regla |
|---|---|---|
| `background` | fondo, textura, viñeta | no compite con texto |
| `atmosphere` | glow, bloom, haze | no lava contenido |
| `shell` | sidebar, header, marco | no roba prioridad al flujo |
| `surface` | cards, paneles | separa sin ensuciar |
| `content` | texto, precios, datos | gana sobre decoración |
| `action` | botones y CTA | COBRAR domina |
| `state` | error, warning, offline, stock | visible sin drama barato |
| `focus` | hover, active, focus ring | claro para touch/teclado |
| `overlay` | modales, drawers, payment | prioridad temporal |
| `debug` | guías visuales | apagado por defecto |

## Runtime

El archivo activo es:

```text
config/prisma-visual-os/prisma-visual-controls.active.json
```

El CSS generado es:

```text
styles/prisma-visual-os/prisma-visual-controls.generated.css
```

Comando desde la raíz del proyecto:

```powershell
node tools/prisma-visual-os/generate_prisma_visual_os_controls_00e.mjs
node tools/prisma-visual-os/verify_prisma_visual_os_core_00d_00e.mjs
```

## Guardrails

- Tablet POS mantiene target táctil mínimo.
- Checkout y POS no pueden bajar peso de acción.
- Contraste operativo gana sobre glow premium.
- Debug layers no se activa por defecto.
