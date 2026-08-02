# Atlasfin canonical visual control

Atlasfin is the single canonical visual-control cabin. The cabin projects governed facts; it does not replace UIMAP, UI Bridge, RIFAT, active owners, or their generators as sources of truth.

## Pilot boundary

The first and only pilot is Tablet POS → Cobrar:

`SURF.tb.pos → ROUTE.tb.pos → OWN.tb.pos_ticket_panel → ZONE.tb.pos.payment → SLOT.tb.pos.payment.cobrar → TB-POS-PAY-COBRAR-BTN-01 → .cobrarReferenceButton → LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE → products.tablet.app.components.pos.pos.module.css.cobrarreferencebutton → BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1 → REC.button.primary`

The projection is built by `generator/build_canonical_visual_control.py` from an immutable certified UIMAP batch and the existing Code Atlas UI Bridge. It records the deterministic source-only plan without applying it.

## Truthful readiness

- Source-only planning: `READY_FOR_SOURCE_ONLY_PLANNING`.
- UI Bridge plan: `PLAN_READY_FOR_REVIEW` with application disabled.
- Runtime mutation: forbidden.
- Product application: forbidden.
- Visual/runtime evidence: `BLOCKED_BY_MISSING_MAMASTROPHIC_EVIDENCE`.
- Coverage freshness: `BLOCKED_BY_STALE_RUNTIME_EVIDENCE` when the recorded coverage CSS hash differs from the current certified UIMAP target hash.

Source proof must never be promoted to runtime certification. A future authorized application cycle must collect before evidence, pass gates, apply only the exact reviewed patch, collect after evidence, and restore only that patch if any gate fails.

## Rendering contract

The browser loads the pilot payload only after the operator opens the control. Operation cards are paginated four at a time and searched through generated scalar `searchText`; the UI does not stringify every record and never renders the full plan at startup.

## Parallel prototype retirement

The B-governor prototype is preserved as historical evidence but is not active authority. Only its presentation ideas—provenance, hierarchy, risks, gates, history, and rollback—were adapted. No projection or runtime file was copied.
