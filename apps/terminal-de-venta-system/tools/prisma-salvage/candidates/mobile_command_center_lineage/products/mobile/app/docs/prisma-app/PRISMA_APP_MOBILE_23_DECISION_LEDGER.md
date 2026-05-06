# PRISMA App Mobile 23 - Decision Ledger

## Objetivo
Agregar una bitácora móvil de decisiones para que el dueño vea qué señales se convirtieron en acciones, con evidencia, responsable sugerido, vencimiento operativo y texto auditable para cierre.

## Alcance
- Endpoint `/api/mobile/decision-ledger`.
- Builder puro `buildPrismaMobileDecisionLedger`.
- Componente `PrismaMobileDecisionLedger` integrado al dashboard móvil.
- Gate `verify:decision-ledger`.

## Criterio de salida
- La bitácora se deriva de Centro de Mando, Bandeja del Dueño y Brief Diario.
- No toca Tablet, PC ni `shared-kernel`.
- No introduce copy de estado inconcluso.
- Mantiene endpoint `no-store` y lectura dinámica.

## Uso operativo
La bitácora sirve para cierre, seguimiento del encargado y evidencia ligera de por qué se sugirió una acción.
