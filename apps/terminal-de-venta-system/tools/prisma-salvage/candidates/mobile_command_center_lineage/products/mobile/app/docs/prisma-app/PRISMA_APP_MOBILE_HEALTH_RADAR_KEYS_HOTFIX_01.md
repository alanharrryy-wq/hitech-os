# PRISMA App Mobile - Health Radar keys hotfix 01

## Objetivo
Corregir el warning de React por llaves duplicadas en `PrismaMobileHealthRadar.tsx`.

## Cambio
- Reemplaza el componente con una version que usa llaves compuestas por seccion, item, valor e indice.
- Evita usar labels visibles como `tablet: OK` como key.
- Agrega estilos de radar operativo para que la seccion se lea como producto terminado.

## Alcance
Solo App movil. No toca Tablet POS, PC Backoffice ni shared-kernel.
