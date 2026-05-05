# PRISMA Visual OS README Status 00W

## Objetivo

Actualizar la documentación operativa de Visual OS para reflejar el estado canon actual:

- `00T` = POS live binding seguro sin layout mapping.
- `00U` = doctor permanente dentro del repo.
- `00V` = touch-only POS fix aplicado y verificado.
- `00W` = README operativo actualizado y verificable.

## Alcance

Este paquete sólo toca documentación y agrega un verificador documental.

No modifica:

- `/pos` runtime.
- `pos-live-binding.tsx`.
- `pos-screen.tsx`.
- `pos-ticket-panel.tsx`.
- `pos.module.css`.
- servidor realtime.
- Studio Pro.

## Archivos

```text
tools/prisma-visual-os/README_PRISMA_VISUAL_OS_LIVE_STUDIO_00O_00T.md
tools/prisma-visual-os/verify_prisma_visual_os_readme_status_00w.mjs
docs/design/PRISMA_VISUAL_OS_README_STATUS_00W.md
docs/qa/PRISMA_VISUAL_OS_README_STATUS_00W_ACCEPTANCE.md
```

## Regla

La documentación no debe volver a afirmar que `00T` está pendiente cuando ya fue corregido como `safe-no-layout`.

## Validación

```powershell
cd F:\repos\hitech-os\apps\terminal-de-venta-system
node tools\prisma-visual-os\verify_prisma_visual_os_readme_status_00w.mjs
```
