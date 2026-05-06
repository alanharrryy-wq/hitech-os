# PRISMA Visual OS - QA, Preset Studio y Release Gate 00L/00M/00N

**Paquete:** PRISMA_VISUAL_QA_RELEASE_GATE_00L_00M_00N_20260503_v01

## Scope

Este paquete instala el segundo frente paralelo de PRISMA Visual OS para Chat B:

- 00L - Cross Surface Visual QA.
- 00M - Preset Studio / Variant Packs.
- 00N - Visual Release Gate.

No toca Tablet POS profundo, checkout Tablet, Core runtime, shared-kernel, shared/contracts ni `shared/TWIN_CHAT_SHARED_CONTEXT_6.1.json`.

## Dependencia bloqueante de Chat A

Antes de aplicar deben existir:

```text
config/prisma-visual-os/prisma-visual-controls.active.json
styles/prisma-visual-os/prisma-visual-layers.css
styles/prisma-visual-os/prisma-visual-controls.generated.css
docs/design/PRISMA_VISUAL_OS_00D_00E_CONTRACT.md
```

Si faltan, el instalador reporta `BLOCKED_DEPENDENCY`, no escribe cambios y permite verificacion parcial. Es la version tecnica de no abrir la cortina si todavia falta la llave del local.

## Intencion por bloque

### 00L
Matriz estatica para confirmar que Tablet, PC y Mobile obedecen el mismo sistema visual sin perder su funcion.

### 00M
Variant packs oficiales: Black Premium, Light Operational, Dual Balance, PC Dense Backoffice y Mobile Owner Pulse.

### 00N
Compuerta de release visual con estados `READY`, `BLOCKED_DEPENDENCY` y `FAIL`.

## Comandos despues de instalar

```powershell
node tools/prisma-visual-os/verify_prisma_visual_qa_release_gate_00l_00m_00n.mjs --root F:epos\hitech-ospps	erminal-de-venta-system --allow-partial
node tools/prisma-visual-os/run_prisma_visual_cross_surface_qa_00l.mjs --root F:epos\hitech-ospps	erminal-de-venta-system --out F:\descargasf --allow-partial
node tools/prisma-visual-os/print_prisma_visual_variant_packs_00m.mjs --root F:epos\hitech-ospps	erminal-de-venta-system --out F:\descargasf
node tools/prisma-visual-os/gate_prisma_visual_release_00n.mjs --root F:epos\hitech-ospps	erminal-de-venta-system --out F:\descargasf --allow-partial
```
