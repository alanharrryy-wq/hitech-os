# PRISMA Visual OS - Cross Surface Bindings 00J / 00K

**Paquete:** `PRISMA_CROSS_SURFACE_BINDINGS_00J_00K_20260503_v01`  
**Frente:** Chat B  
**Superficies:** PC Backoffice + PRISMA App Mobile

## Alcance

- **00J PC Backoffice Binding:** activa `PC_DENSE_ADMIN`, backoffice denso, legible y administrativo.
- **00K Mobile Pulse Binding:** activa `MOBILE_PULSE`, supervisor rápido, táctil y orientado a alertas.

## Dependencia de Chat A

Requiere:

- `config/prisma-visual-os/prisma-visual-controls.active.json`
- `styles/prisma-visual-os/prisma-visual-layers.css`
- `styles/prisma-visual-os/prisma-visual-controls.generated.css`
- `docs/design/PRISMA_VISUAL_OS_00D_00E_CONTRACT.md`

Si faltan, el instalador reporta `BLOCKED_DEPENDENCY` y no aplica cambios destructivos.

## No toca

- `products/tablet/app/*`
- `packages/shared-kernel/*`
- `shared/contracts/*`
- `shared/TWIN_CHAT_SHARED_CONTEXT_6.1.json`
- checkout, POS profundo ni runtime Core

## Validación

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app run verify:visual-os-pc-binding-00j
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app run verify:visual-os-mobile-pulse-00k
python F:\descargasf\install_prisma_cross_surface_bindings_00j_00k_20260503_v01.py --zip-path F:\descargasf\PRISMA_CROSS_SURFACE_BINDINGS_00J_00K_20260503_v01.zip --target-root F:\repos\hitech-os\apps\terminal-de-venta-system --verify
```
