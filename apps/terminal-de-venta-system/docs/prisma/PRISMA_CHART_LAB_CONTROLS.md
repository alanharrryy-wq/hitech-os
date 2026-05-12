# PRISMA Chart Lab Controls

Runtime controls are schema-driven at:

`F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\src\prisma-charts\chart-lab-control-model.ts`

The reusable deck is:

`F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\src\components\ChartControlDeck.tsx`

## Required Causal Flow Controls

- severity filter
- confidence floor
- ribbon width
- ribbon opacity
- labels on/off
- animation on/off
- detail level
- stage focus
- layout density
- evidence mode

## Global Controls

Every governed chart has data scenario, theme preset, label, animation, and visual intensity controls. Chart-specific controls add real data/option transforms where useful.

## Verification

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:verify:controls
```
