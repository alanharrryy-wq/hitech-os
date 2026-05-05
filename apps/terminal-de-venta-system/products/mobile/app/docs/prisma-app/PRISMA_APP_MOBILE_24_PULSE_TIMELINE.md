# PRISMA App Mobile 24 - Pulse Timeline

## Objetivo

Agregar una línea de pulso operativo móvil que ordena señales del día por fase: apertura, operación, pico, seguimiento y cierre.

## Alcance

- Nuevo endpoint `/api/mobile/pulse-timeline`.
- Nuevo motor puro `buildPrismaMobilePulseTimeline`.
- Nuevo componente `PrismaMobilePulseTimeline`.
- Integración visual debajo de la bitácora de decisiones.
- Verificador `verify:pulse-timeline`.

## Criterios de salida

- El timeline usa snapshot móvil conectado.
- Reutiliza Centro de Mando, Bandeja del Dueño y Bitácora de Decisiones.
- No toca Tablet, PC ni shared-kernel.
- No introduce copy demo ni referencias a código inconcluso.

## Uso

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app" run verify:pulse-timeline
```
