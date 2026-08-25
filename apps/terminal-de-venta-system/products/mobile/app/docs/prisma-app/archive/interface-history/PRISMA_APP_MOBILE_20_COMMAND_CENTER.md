# PRISMA App Mobile 20 - Centro de Mando Operativo

## Objetivo

Convertir la pantalla móvil en una capa de decisión para dueño o supervisor: no solo ver métricas, sino saber qué atender primero cuando Tablet, PC, inventario, caja o datos conectados empiezan a enseñar los colmillos.

## Qué agrega

- `prisma-mobile-command-center.ts`: builder puro de riesgo, readiness, señales y cola de decisiones.
- `PrismaMobileCommandCenter.tsx`: componente visual premium integrado al dashboard.
- `/api/mobile/command-center`: endpoint no-store para consumir la misma decisión desde integraciones externas.
- `verify:command-center`: gate local sin dependencias de red.
- Escenarios QA de riesgo operativo para caja, inventario, sync, ventas y sucursal.

## Regla de arquitectura

La App móvil sigue sin reemplazar a Tablet ni PC:

- Tablet sigue vendiendo.
- PC sigue gobernando.
- App móvil resume, prioriza, alerta y orienta.

## Criterio de salida

Esta iteración se considera válida si:

1. El dashboard renderiza el Centro de Mando antes de las KPI cards.
2. El builder no usa `Date.now()` ni `Math.random()` durante render.
3. La API `/api/mobile/command-center` responde con `no-store`.
4. El paquete no reintroduce archivos demo, mock o fixtures heredados en runtime.
5. `pnpm run verify:command-center` pasa.

## Riesgo residual

No implementa permisos/auth ni ingestión real nueva desde Tablet/PC. Esta capa prioriza lo que ya llega por el data-plane actual. Meter sync nuevo aquí sería como ponerle turbo a una bicicleta sin revisar los frenos: divertido hasta que aparece una pared.
