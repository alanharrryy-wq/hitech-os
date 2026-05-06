# Tablet Twin Runtime Kernel

La app tablet consume `tabletTwinCapabilityRegistry`, `tabletTwinCapabilities`, `tabletTwinCapabilityScorecard` y `tabletModuleTwinReadiness` desde `src/composition/twin-capabilities.ts`.

Tablet no debe volverse mini-PC. Tablet ejecuta rápido, captura eventos y conserva contexto offline cuando el contrato lo permite.

## Uso esperado

- Checkout y ventas: revisar ownsWrites y eventos requeridos antes de persistir.
- Stock rápido: no escribir ledger global sin capability autorizada.
- Sync: mostrar eventos pendientes usando el catálogo compartido.

## Gate mínimo

Una acción tablet nueva que produce evento debe aparecer en allowedEvents de su surface binding. Si no, es botón pirata con CSS bonito.
