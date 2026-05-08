# ATLAS COORDINATOR VALIDATION REPORT

Fecha: 2026-05-08

Estado general: **APPROVED_FOR_ATLAS_DRAFT_INTEGRATION_WITH_WARNINGS**

## Resultado ejecutivo

- Los cuatro ZIPs entregaron el set completo de archivos esperados.
- Se consolidó un paquete final con rutas listas para repo.
- Se reemplazó `atlas.pc.json` por una versión normalizada de Coordinador para cumplir el schema canónico.
- No hay duplicados de `intentId` ni traslapes bloqueantes de ownership.
- Hay advertencias de release/verificación en Mobile y Tablet; son importantes, pero no bloquean la integración documental del atlas.

## Entregables por ZIP

| App | Esperados | Recibidos | Faltantes | Sobrantes |
|---|---:|---:|---|---|
| mobile | 10 | 10 | 0 | 0 |
| tablet | 10 | 10 | 0 | 0 |
| pc | 10 | 10 | 0 | 0 |
| shared | 12 | 12 | 0 | 0 |

## Validación de schema

| App | Estado | Nota |
|---|---|---|
| mobile | OK | OK |
| tablet | OK | OK |
| pc | OK | Original no canónico; normalizado por Coordinador. |
| shared | OK | OK |

## Cobertura consolidada

| App | Change intents | Surfaces | Functional engines | Visual systems | Interactions | Runtime | Verification | Shared deps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mobile | 19 | 19 | 10 | 4 | 6 | 4 | 18 | 10 |
| tablet | 8 | 5 | 13 | 4 | 4 | 3 | 7 | 6 |
| pc | 15 | 83 | 56 | 1 | 1 | 1 | 34 | 41 |
| shared | 8 | 4 | 6 | 2 | 3 | 3 | 5 | 2 |

## Advertencias principales

- **mobile / path-reference**: Some referenced paths not found in source inventories. docs/PRISMA_MOBILE_FUTURE_EDIT_MAP.md; docs/prisma-app/PRISMA_APP_MOBILE_27_PREMIUM_NAVIGATION.md; src/lib/prisma-app/mobile-data-plane/adapters unless changing source semantics; src/lib/prisma-app/prisma-mobile-daily-brief.ts unless changing generated content contract; docs/prisma-app/PRISMA_APP_MOBILE_20_COMMAND_CENTER.md; docs/prisma-app/PRISMA_APP_MOBILE_21_OWNER_ACTION_INBOX.md; Tablet/PC/shared core; docs/prisma-app/PRISMA_APP_MOBILE_22_DAILY_BRIEF.md; docs/prisma-app/PRISMA_APP_MOBILE_23_DECISION_LEDGER.md; docs/prisma-app/PRISMA_APP_MOBILE_24_PULSE_TIMELINE.md; PC/Tablet runtimes; docs/prisma-app/PRISMA_APP_MOBILE_25_HEALTH_RADAR.md ...
- **tablet / path-reference**: Some referenced paths not found in source inventories. PC/backoffice files fuera del carril Tablet; shared/twin-kernel runtime registry salvo contrato externo; R05-VERIFIER-RUN-tools/verify_tablet_i03a_ticket_detail.mjs; R05-VERIFIER-RUN-tools/verify_tablet_04_offline_export.mjs
- **pc / path-reference**: Some referenced paths not found in source inventories. prisma/schema.prisma global sin revisar Shared Core; prisma/schema.prisma global sin coordinar Shared Core; ../../../prisma/schema.prisma; Missing required file: ../../../shared/twin-kernel/src/types/module.ts; docs/modules/catalog.md; docs/modules/purchasing.md; docs/modules/receiving.md; docs/modules/replenishment.md; docs/modules/dashboard-kpi.md; docs/PC_SHELL_ZOOM_SCROLL_TRACE_03.md; docs/modules/stock.md; docs/modules/counts.md ...
- **shared / path-reference**: Some referenced paths not found in source inventories. docs/atlas/ATLAS_SHARED_CORE_CONTRACTS.md; pending-confirmation: pipeline that generates shared/tri-db/status.latest.json
- **mobile / verification**: Verifier/release caveats reported by worker. | verify:whatsapp-install-gate | fail | MISSING public/icons/prisma_ios_touch_icon_180.png | MISSING public/apple-touch-icon.png | MISSING public/apple-touch-icon-precomposed.png | | | verify:install-landing-black | fail | MISSING public/icons/prisma_ios_touch_icon_180.png | MISSING public/apple-touch-icon.png | MISSING public/apple-touch-icon-precomposed.png | | | verify:pwa | fail | [PWA FAIL] manifest icon path not found: /icons/prisma_playstore_icon_192.png | | | verify:playstore-readiness | fail | [PLAYSTORE FAIL] products/mobile/android root must exist |
- **tablet / verification**: Verifier/release caveats reported by worker. - Assets PNG marcados como pendientes de confirmar porque el snapshot sólo trae READMEs y manifiesto. | - Release actual: **BLOCKED** por `verify:i03a-ticket-detail` y `verify:04-offline`. | | validate_package | FAILED | - | | | verify_05_release | BLOCKED | R05-VERIFIER-RUN-tools/verify_tablet_i03a_ticket_detail.mjs, R05-VERIFIER-RUN-tools/verify_tablet_04_offline_export.mjs | | | verify_i03a_ticket_detail | FAIL | I03A-010 screen calls direct detail endpoint, I03A-016 list links to encoded saleId | | | verify_04_offline | FAIL | T04-008 screen renders outbox |
- **pc / verification**: Verifier/release caveats reported by worker. | Pendientes | Schema canónico, shared deps, tri-db externo y assets faltantes. | | El validador local del snapshot falla por dependencias externas ausentes (`shared/twin-kernel`, `shared/licensing`, etc.). El atlas lo documenta como pendiente, sin inventar build verde.

## Fixes aplicados por Coordinador

- `products/pc/app/docs/atlas/atlas.pc.json`: normalizado a `atlasId/app/root/version/changeIntents/...` sin perder rutas, módulos, repositorios, servicios, verifiers ni shared dependencies.

## Verificadores y release caveats

### mobile
- | verify:whatsapp-install-gate | fail | MISSING public/icons/prisma_ios_touch_icon_180.png | MISSING public/apple-touch-icon.png | MISSING public/apple-touch-icon-precomposed.png |
- | verify:install-landing-black | fail | MISSING public/icons/prisma_ios_touch_icon_180.png | MISSING public/apple-touch-icon.png | MISSING public/apple-touch-icon-precomposed.png |
- | verify:pwa | fail | [PWA FAIL] manifest icon path not found: /icons/prisma_playstore_icon_192.png |
- | verify:playstore-readiness | fail | [PLAYSTORE FAIL] products/mobile/android root must exist |

### tablet
- - Assets PNG marcados como pendientes de confirmar porque el snapshot sólo trae READMEs y manifiesto.
- - Release actual: **BLOCKED** por `verify:i03a-ticket-detail` y `verify:04-offline`.
- | validate_package | FAILED | - |
- | verify_05_release | BLOCKED | R05-VERIFIER-RUN-tools/verify_tablet_i03a_ticket_detail.mjs, R05-VERIFIER-RUN-tools/verify_tablet_04_offline_export.mjs |
- | verify_i03a_ticket_detail | FAIL | I03A-010 screen calls direct detail endpoint, I03A-016 list links to encoded saleId |
- | verify_04_offline | FAIL | T04-008 screen renders outbox |

### pc
- | Pendientes | Schema canónico, shared deps, tri-db externo y assets faltantes. |
- El validador local del snapshot falla por dependencias externas ausentes (`shared/twin-kernel`, `shared/licensing`, etc.). El atlas lo documenta como pendiente, sin inventar build verde.

## Archivos del paquete final

- `docs/atlas/ATLAS_MASTER_INDEX.md`
- `docs/atlas/ATLAS_SHARED_CORE.md`
- `docs/atlas/ATLAS_SHARED_CORE_CONTRACTS.md`
- `docs/atlas/ATLAS_SHARED_CORE_FUNCTIONAL_ENGINES.md`
- `docs/atlas/ATLAS_SHARED_CORE_RUNTIME_INFRA.md`
- `docs/atlas/ATLAS_SHARED_CORE_VISUAL_OS.md`
- `docs/atlas/atlas.registry.json`
- `docs/atlas/atlas.shared-core.json`
- `meta/COORDINATOR_ISSUE_LOG.csv`
- `meta/COORDINATOR_VALIDATION_SUMMARY.json`
- `products/mobile/app/docs/atlas/ATLAS_MOBILE.md`
- `products/mobile/app/docs/atlas/ATLAS_MOBILE_FUNCTIONAL_ENGINES.md`
- `products/mobile/app/docs/atlas/ATLAS_MOBILE_INTERACTION.md`
- `products/mobile/app/docs/atlas/ATLAS_MOBILE_RUNTIME_DELIVERY.md`
- `products/mobile/app/docs/atlas/ATLAS_MOBILE_VISUAL.md`
- `products/mobile/app/docs/atlas/atlas.mobile.json`
- `products/pc/app/docs/atlas/ATLAS_PC.md`
- `products/pc/app/docs/atlas/ATLAS_PC_FUNCTIONAL_ENGINES.md`
- `products/pc/app/docs/atlas/ATLAS_PC_INTERACTION.md`
- `products/pc/app/docs/atlas/ATLAS_PC_RUNTIME_DELIVERY.md`
- `products/pc/app/docs/atlas/ATLAS_PC_VISUAL.md`
- `products/pc/app/docs/atlas/atlas.pc.json`
- `products/tablet/app/docs/atlas/ATLAS_TABLET.md`
- `products/tablet/app/docs/atlas/ATLAS_TABLET_FUNCTIONAL_ENGINES.md`
- `products/tablet/app/docs/atlas/ATLAS_TABLET_INTERACTION.md`
- `products/tablet/app/docs/atlas/ATLAS_TABLET_RUNTIME_DELIVERY.md`
- `products/tablet/app/docs/atlas/ATLAS_TABLET_VISUAL.md`
- `products/tablet/app/docs/atlas/atlas.tablet.json`

## Dictamen

Integrar como **atlas documental consolidado**. No tratar esto como aprobación de release de producto hasta resolver los verificadores fallidos o dependencias externas ausentes que los mismos trabajadores documentaron.
