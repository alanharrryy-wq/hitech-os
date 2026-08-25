# PRISMA Mobile Interface Canon v1

**Capability:** `mobile.interface_specification_canon`  
**Authority status:** normative Mobile interface specification, source-ready candidate  
**Baseline:** `main@0916227707aa65b673195d554297bf8f8565d356`  
**Fresh Authority Mesh:** run `32877668997`, artifact `9574572977`, SHA-256 `24e2cf613ae89b9880daafc33c79b128f36e791ea276190753f3b0e5a18512a9`, request digest `3718395826e74e834ebde7e53874c673d1850ab724e953ef99b1343e4490a9c7`  
**Mutation scope of this iteration:** documentation and specification retirement only. No Mobile product source, API, runtime, PWA, data, sync, security, licensing or verifier mutation.

## 1. Purpose

This document is the single normative source for **which customer-facing interfaces and primary navigation belong to PRISMA Mobile**.

It resolves the historical accumulation of `PRISMA_APP_MOBILE_*` iteration documents that described different Mobile information architectures at different moments. Those documents remain historical evidence where needed, but they no longer compete with this canon.

This canon does **not** certify runtime behavior. It defines product/interface intent and the current source-aligned baseline that future Mobile work must preserve or deliberately change under a fresh governed task.

## 2. Authority order

When Mobile interface documents disagree, use this order:

1. `PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json` for capability state, anti-rework status and next gate.
2. This document plus `PRISMA_MOBILE_INTERFACE_CANON.contract.json` for normative Mobile interface/product intent.
3. Current verified Mobile source and focused current verifiers for implementation conformance evidence.
4. `docs/atlas/ATLAS_MOBILE.md` and other Atlas maps as implementation/discovery maps.
5. Historical `PRISMA_APP_MOBILE_*` iteration documents, acceptance notes and visual adders as historical evidence only.
6. Analysis manifests, snapshots and salvage copies as non-authoritative evidence.

**Runtime/source existence does not invent product authority by itself.** Likewise, an old acceptance document does not force a dormant component back into the current interface.

## 3. Product role

PRISMA Mobile is a **supervision and decision surface**.

- **Tablet sells and must remain operational independently.**
- **PC governs/backoffice when present.**
- **Mobile supervises, summarizes, alerts and exposes evidence for fast owner/supervisor decisions.**
- Mobile must not become a second POS or a full PC backoffice by accumulation.
- A Mobile failure must not imply Tablet cannot sell.
- Read-only projection contracts remain read-only unless a separate capability explicitly authorizes mutation.

## 4. Canonical primary surface

The canonical primary customer surface is:

`/prisma-app`

`PrismaMobileDashboard` owns the shell, loading/error boundary, brand context and delegates the primary information architecture to `PrismaMobilePremiumNavigator`.

### Canonical primary navigation

The top-level Mobile navigation is exactly seven sections, in this order:

| ID | Label | Canonical responsibility |
|---|---|---|
| `inicio` | Inicio | Fast business pulse and the most important owner-facing summary. |
| `ventas` | Ventas | Visible sales activity and commercial rhythm. |
| `operacion` | Operación | Operational state across Mobile, Tablet, PC and sync signals without turning Mobile into backoffice. |
| `licencias` | Licencias | License, device and customer-setup visibility relevant to the Mobile companion. |
| `alertas` | Alertas | Actionable exceptions and attention signals. |
| `stock` | Stock | Operational inventory watchlist, critical/replenishment/normal states and evidence-backed stock signals. |
| `sistema` | Sistema | Data/source readiness, refresh/cache controls and system-level Mobile health information. |

This seven-section order is the canonical primary IA until a future governed interface change explicitly replaces it.

## 5. What is not a top-level section

Historical iterations used additional top-level concepts. They are explicitly retired as competing primary-navigation authority:

- `Hoy` is absorbed by **Inicio**.
- `Caja` remains an operational/data capability but is **not** a canonical top-level Mobile section.
- `Inventario` is represented by **Stock** in the primary IA.
- `Reportes` is not a canonical top-level Mobile section. Report/brief capabilities may exist as secondary evidence or contextual output.
- `MultiSucursal` is not a canonical top-level Mobile section. Context/scope selection is a separate concern and must not become navigation merely because multi-context code exists.
- `Resumen` is absorbed by **Inicio**.
- `Sync` is represented as operational/system evidence, not a dedicated canonical top-level section.
- `Mando` is not a canonical top-level tab.
- `Command Center`, `Action Inbox`, `Daily Brief`, `Decision Ledger`, `Pulse Timeline` and `Health Radar` are not mandatory top-level or always-mounted sections in this canon.

## 6. Auxiliary lifecycle routes

These routes are part of the Mobile product but **not** part of the seven-tab primary navigation:

| Route | Role |
|---|---|
| `/prisma-app/setup` | Customer Setup / Setup Code / Mobile device-claim entry. |
| `/prisma-app/install` | PWA/mobile install surface. |
| `/prisma-app/offline` | PWA offline shell/lifecycle surface. |

The existence of `/prisma-app/offline` does not by itself certify offline operational data support.

## 7. Separate preview / specialist surface

`/prisma-command` is a separate Mobile owner/chart preview surface. It is **not** a primary `/prisma-app` tab and does not change the seven-section canon.

It may expose six compact chart modules when its chart flags/preview contract allows it. Any promotion from preview/specialist route into primary Mobile navigation requires a new governed interface decision.

## 8. Dormant or secondary capability modules

The repository may contain and export these components and their API/builders:

- `PrismaMobileCommandCenter`
- `PrismaMobileActionInbox`
- `PrismaMobileDailyBrief`
- `PrismaMobileDecisionLedger`
- `PrismaMobilePulseTimeline`
- `PrismaMobileHealthRadar`
- `PrismaMobileMultiContextSwitcher`

Their existence is preserved as implementation/capability evidence. **Existence does not mean they must currently be mounted in `PrismaMobileDashboard` or `PrismaMobilePremiumNavigator`.**

For this canon baseline:

- The six historical "mando" components are secondary/dormant capability modules unless a current source owner mounts them under a separately authorized change.
- `PrismaMobileMultiContextSwitcher` is a dormant optional visual capability. Its historical "first viewport" acceptance statement is superseded.
- No component is to be re-mounted solely to satisfy an obsolete iteration document.

## 9. Truth, freshness and no-fake-green rules

Every Mobile interface change must preserve these principles:

1. Do not present missing, stale, partial, timed-out, denied or contradictory data as healthy.
2. Preserve source/freshness/readiness evidence where the current data plane exposes it.
3. Loading and error states are product states, not visual defects to hide.
4. A PWA shell, cached shell or route existence is not proof of live operational data.
5. A component existing in source is not proof that it is customer-visible.
6. A historical verifier or screenshot is not proof of current mounting.
7. Mobile cannot claim a mutation capability from a read-only projection contract.
8. Tablet independence remains a hard product boundary.

## 10. Interface retirement and migration map

Historical documents are retired by **tombstone, not silent deletion**. Their byte-exact pre-canon text is preserved under `archive/interface-history/` when this canon directly supersedes their interface/mounting claims.

| Compatibility path | Canon status | Why |
|---|---|---|
| `docs/PRISMA_APP_MOBILE_02_SECTIONS.md` | `SUPERSEDED_PRIMARY_IA` | Historical Hoy/Ventas/Caja/Inventario/Alertas/Reportes/MultiSucursal model. |
| `docs/prisma-app/PRISMA_APP_MOBILE_20_COMMAND_CENTER.md` | `HISTORICAL_CAPABILITY_EVIDENCE` | Command Center capability remains; old mandatory mounting statement is not normative. |
| `docs/prisma-app/PRISMA_APP_MOBILE_21_OWNER_ACTION_INBOX.md` | `HISTORICAL_CAPABILITY_EVIDENCE` | Action Inbox capability remains; old sequence/mounting statement is not normative. |
| `docs/prisma-app/PRISMA_APP_MOBILE_22_DAILY_BRIEF.md` | `HISTORICAL_CAPABILITY_EVIDENCE` | Daily Brief capability remains; old dashboard placement is not normative. |
| `docs/prisma-app/PRISMA_APP_MOBILE_23_DECISION_LEDGER.md` | `HISTORICAL_CAPABILITY_EVIDENCE` | Decision Ledger capability remains; old dashboard integration claim is not normative. |
| `docs/prisma-app/PRISMA_APP_MOBILE_24_PULSE_TIMELINE.md` | `HISTORICAL_CAPABILITY_EVIDENCE` | Pulse Timeline capability remains; old visual placement is not normative. |
| `docs/prisma-app/PRISMA_APP_MOBILE_25_HEALTH_RADAR.md` | `HISTORICAL_CAPABILITY_EVIDENCE` | Health Radar capability remains; it is not a required primary section. |
| `docs/prisma-app/PRISMA_APP_MOBILE_27_PREMIUM_NAVIGATION.md` | `SUPERSEDED_PRIMARY_IA` | Its Resumen/Caja/Alertas/Inventario/Sync navigation predates the restored seven-section IA. |
| `docs/prisma-app/PRISMA_APP_MOBILE_33_MANDO_ACCEPTANCE.md` | `SUPERSEDED_MOUNTING_ACCEPTANCE` | Its six-surface always-mounted expectation conflicts with current source ownership. |
| `docs/prisma-app/PRISMA_APP_MOBILE_41_MULTI_CONTEXT_SWITCHER_RENDER_GRADE.md` | `SUPERSEDED_MOUNTING_ACCEPTANCE` | Its first-viewport mounting claim is not current canon. |
| `docs/atlas/ATLAS_MOBILE.md` | `IMPLEMENTATION_MAP_KEEP` | Discovery/ownership map, not normative product-interface authority. |
| `docs/prisma-app/PRISMA_APP_MOBILE_39_PREMIUM_POLISH.md` | `VISUAL_EVIDENCE_KEEP` | Visual/polish evidence only; does not define primary IA. |
| `docs/PRISMA_MOBILE_FUTURE_EDIT_MAP.md` | `OWNER_MAP_KEEP` | Change-location/owner map, not normative primary IA. |

A separate repository-level historical copy of `docs/mobile/README_PRISMA_APP_MOBILE_02_SECTIONS.md` is likewise tombstoned and preserved in its adjacent archive.

## 11. Verifier dependency caveat

Several legacy Mobile verifiers still encode historical mounting/version expectations from iterations 20-25, 33 and 41. This canon **does not modify those verifiers**, because the current Factory Ledger gate authorizes documentation-only consolidation.

Therefore:

- legacy verifiers remain preserved as evidence,
- their historical mounting assertions must not be treated as current product authority,
- any verifier reconciliation is a **separate future governed quality/tooling task** after this canon is merged,
- no one should re-mount dormant UI merely to make a stale verifier green.

This is an explicit no-fake-green boundary.

## 12. Change rule

Any future request to add, remove, rename, reorder or promote a Mobile interface must:

1. read the Factory Ledger and this canon,
2. obtain a fresh exact-task Authority Mesh,
3. declare whether the change affects the seven-section primary IA, an auxiliary route, a preview route or a secondary capability,
4. identify the owner component and affected data/security contracts,
5. update this canon and contract in the same governed change,
6. preserve rollback/evidence,
7. never use a historical document as a prose override.

## 13. What this canon proves and does not prove

### Proves

- One normative Mobile interface specification now exists.
- The primary `/prisma-app` IA is defined as seven ordered sections.
- Historical competing IA/mounting documents have an explicit migration status.
- Dormant component existence is separated from customer-visible mounting authority.

### Does not prove

- Runtime visual certification.
- Hosted production behavior.
- Offline operational data certification.
- Current `check:all` success.
- Verifier alignment.
- Any new Mobile mutation capability.
- Any Tablet or PC change.

Those are separate evidence gates.
