# Pilot 20 · Liquid Glass Director Cut · Fix7

Fecha: `2026-06-01 18:38:50`

## Objetivo

Fix7 deja de pelear contra el skin global de botones como borracho en taquería. Cambia la ruta a una composición con Radix + OGL:

- `@radix-ui/react-dialog`
- `@radix-ui/react-dropdown-menu`
- `@radix-ui/react-scroll-area`
- `@radix-ui/react-select`
- `@radix-ui/react-tabs`
- `@radix-ui/react-tooltip`
- `@radix-ui/react-slot`
- `@vanilla-extract/css`
- `ogl`

## Cambios visuales

- Fondo fijo real.
- Scroll interno con Radix ScrollArea.
- Selector de familia con Radix Select.
- Familia activa con Radix Tabs, sin `<button>` para los pills.
- Ayuda contextual con Radix Tooltip.
- Acciones semánticas compuestas con Radix Slot.
- Aura OGL ligera y con reduced motion.
- CSS module limpio, sin Fix2/Fix3/Fix4/Fix5/Fix6 acumulados.

## Familias

- **Aurora Night** · `aurora-night` · exists: `True` · accent `#ff7aa8` · ring `#aaf7ff`
- **Alpine Crystal** · `alpine-crystal` · exists: `True` · accent `#c9f5ff` · ring `#ffffff`
- **Ocean Vapor** · `ocean-vapor` · exists: `True` · accent `#7bdcff` · ring `#a9ffe2`
- **Fog Forest** · `fog-forest` · exists: `True` · accent `#b8ffd9` · ring `#caffee`

## Reglas

- POS: no touch
- Checkout: no touch
- Tablet productiva: no touch
- DB: no touch
- Deploy: no touch
- `package.json` y `pnpm-lock.yaml`: no touch

## Ruta

`/referencia-visual/liquid-glass`

## Verifier

```powershell
Set-Location 'F:/repos/hitech-os/apps/terminal-de-venta-system'
node products/pc/app/scripts/verify-liquid-glass-director-cut.mjs
```

## Fix8 · Radix Tabs Trigger Scope

Fecha: `2026-06-01 18:43:34`

Motivo: Radix `Tabs.Trigger` usa internamente `RovingFocusGroupItem` y debe vivir dentro de `Tabs.List`. El CTA de las cards estaba fuera de `Tabs.List`, dentro de `familyBoard`, provocando runtime error.

Cambio aplicado:

- Se conserva `Tabs.Trigger` sólo en el selector principal de familias.
- El CTA `Usar familia` dentro de cada card ahora es un `span` con `role="button"`, `tabIndex=0`, `onClick` y soporte de teclado Enter/Espacio.
- Se evita `<button>` para no caer otra vez en el skin global azul de PC Backoffice.
- No se toca POS, Checkout, Tablet productiva, DB, deploy, package.json ni lockfile.
