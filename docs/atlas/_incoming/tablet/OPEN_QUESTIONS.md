# OPEN QUESTIONS - Tablet Ronda 2

1. **Shared Kernel real:** confirmar implementación y contratos de `shared/twin-kernel` y aliases `@shared-kernel/*` en el monorepo completo.
2. **Licensing real:** confirmar comportamiento de `shared/licensing`; Tablet sólo consume/adapta estados y features.
3. **Shared UI/Visual OS:** confirmar disponibilidad de `shared-ui/prisma`, `styles/prisma-visual-os` y `config/prisma-visual-os` fuera del ZIP.
4. **Assets PNG:** confirmar presencia física, licencia y uso final de los assets declarados en `analysis/tablet_public_asset_manifest.json`.
5. **Ticket detail I03A:** resolver o confirmar contrato exacto esperado por `verify_tablet_i03a_ticket_detail.mjs` para llamada directa a `/api/pos/sales/detail`.
6. **SaleId codificado:** resolver o confirmar requisito de `encodeURIComponent(saleId)` en la lista de tickets.
7. **Offline outbox T04:** resolver o confirmar cómo debe renderizarse outbox en `components/offline/offline-export-audit-screen.tsx` para pasar `T04-008`.
8. **Release readiness:** ejecutar `verify:05-release` completo después de cerrar I03A/T04.
9. **Build/typecheck completo:** ejecutar en entorno con dependencias externas instaladas y presentes.
10. **Sync PC:** confirmar quién ingiere/reconcilia eventos de Tablet en PC/backoffice; no se declara ownership desde Tablet.
11. **Política de promoción:** confirmar cuándo el coordinador puede mover staging a `products/tablet/app/docs/atlas/`.
12. **Schema final:** confirmar si `atlas.tablet.json` debe validarse contra `templates/prisma-atlas.schema.json` u otro schema del coordinador antes de promoción.
