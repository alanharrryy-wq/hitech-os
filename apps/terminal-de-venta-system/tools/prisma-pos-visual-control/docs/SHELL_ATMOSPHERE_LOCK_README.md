# PRISMA POS Visual Shell Atmosphere Lock 01

Installs the final shell atmosphere pass for Tablet `/pos` after the Visual Control Plane and Surface Lock.

## Scope

- Shell cinematic background, haze, bloom, vignette and subtle texture.
- Sidebar glass, active nav glow and PRISMA brand presence.
- Header glass and content separation.
- POS surface bridge so catalog, ticket and COBRAR stay above the background.

## Forbidden scope

- No backend changes.
- No PC or Mobile changes.
- No shared-ui or shared-kernel writes.
- No `prisma-dark-pos-reference` writes.
- No sale contract changes.

## Tuning examples

```powershell
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma-pos-visual-control\tune_prisma_pos_visual.py" --preset cinematic_dark --apply
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma-pos-visual-control\tune_prisma_pos_visual.py" --set pos.shell.bloom.opacity=0.14 --apply
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma-pos-visual-control\tune_prisma_pos_visual.py" --scale shell=0.82 --apply
```
