# PRISMA Mobile Interface Canon Migration - 2026-08-25

**Status:** `AUTHORITY_CONVERGENCE_MIGRATION_NOTE`  
**Canonical destination:** `PRISMA_MOBILE_INTERFACE_CANON.md`

## Purpose

This migration removes competing PRISMA Mobile product-interface authorities and leaves one normative interface specification.

The user decision is explicit: the canonical Mobile interface specification is aspirational and **does not have to match the current Mobile code**. Current implementation differences are classified as implementation drift, not as authority to rewrite the product model.

This migration is documentation-only. It does not authorize or modify Mobile application source, APIs, data contracts, sync, licensing, authentication, runtime, PWA behavior, Tablet, PC, Shared UI, Shared Core, Chart Lab, or Control Center.

## Canonical destination

All product-interface intent now lives in:

`products/mobile/app/docs/prisma-app/PRISMA_MOBILE_INTERFACE_CANON.md`

The canonical primary product hierarchy is:

`Inicio / Pulso -> Ventas -> Caja -> Inventario -> Mando -> Sistema`

Mando owns Command Center, Action Inbox, Daily Brief, Decision Ledger, Pulse Timeline, Health Radar, and compact owner analytics. MultiSucursal becomes global context switching. Alerts become actionable signals. Reports become Daily Brief/contextual evidence. Sync, licensing, devices, setup, readiness, install, and diagnostics belong to Sistema.

## Deleted competing specification files

The following files are removed because their product/UI authority is superseded:

- `products/mobile/app/docs/PRISMA_APP_MOBILE_02_SECTIONS.md`
- `docs/mobile/README_PRISMA_APP_MOBILE_02_SECTIONS.md`
- `products/mobile/app/docs/prisma-app/PRISMA_APP_02_INFORMATION_ARCHITECTURE.md`
- `products/mobile/app/docs/prisma-app/PRISMA_APP_02_SCREEN_CONTRACTS.md`
- `products/mobile/app/docs/prisma-app/PRISMA_APP_MOBILE_18_ROADMAP.md`
- `products/mobile/app/docs/prisma-app/PRISMA_APP_MOBILE_30_INSTALL_LANDING_BLACK.md`
- `products/mobile/app/docs/prisma-app/PRISMA_APP_MOBILE_33_COMMAND_CENTER_OWNER_INBOX_FINAL.md`
- `products/mobile/app/docs/prisma-app/PRISMA_APP_MOBILE_33_MANDO_ACCEPTANCE.md`
- `products/mobile/app/docs/prisma-app/PRISMA_APP_MOBILE_34_DAILY_BRIEF_LEDGER_TIMELINE_FINAL.md`
- `products/mobile/app/docs/prisma-app/PRISMA_APP_MOBILE_35_HEALTH_RADAR_ALERTS_READINESS_FINAL.md`

## Compatibility pointers retained without normative content

Current `products/mobile/app/package.json` still runs technical verifiers whose scripts hard-code the existence of several iteration-era documentation paths. To keep this documentation-only cleanup from breaking active gates, these legacy files remain only as non-authoritative compatibility pointers:

- `PRISMA_APP_MOBILE_20_COMMAND_CENTER.md`
- `PRISMA_APP_MOBILE_21_OWNER_ACTION_INBOX.md`
- `PRISMA_APP_MOBILE_22_DAILY_BRIEF.md`
- `PRISMA_APP_MOBILE_23_DECISION_LEDGER.md`
- `PRISMA_APP_MOBILE_24_PULSE_TIMELINE.md`
- `PRISMA_APP_MOBILE_25_HEALTH_RADAR.md`
- `PRISMA_APP_MOBILE_27_PREMIUM_NAVIGATION.md`
- `PRISMA_APP_MOBILE_39_PREMIUM_POLISH.md`
- `PRISMA_APP_MOBILE_41_MULTI_CONTEXT_SWITCHER_RENDER_GRADE.md`

Those pointer files contain no independent IA, screen model, navigation model, or visual product direction. They cannot override the canon. A future verifier-path cleanup may remove them physically under a separately authorized tooling task.

## Documents intentionally preserved

The following classes are not competing product-interface specifications and remain intact:

- Mobile Atlas implementation inventory and machine Atlas;
- `PRISMA_MOBILE_FUTURE_EDIT_MAP.md` engineering ownership map;
- API/data-plane/security/signed-session contracts;
- PWA, Play Store, Cloudflare, install, offline, runtime and release documentation;
- verifier scripts, QA fixtures and regression corpora;
- maturity audits and evidence records;
- Factory Ledger, Authority Mesh, quality contracts and operational manuals;
- `prisma-salvage` candidates and historical evidence.

## Commercial documentation rule

Commercial material may describe product benefits but must not create a second navigation or interface authority. When commercial copy mentions old section names, the canonical product hierarchy in `PRISMA_MOBILE_INTERFACE_CANON.md` wins.

## Rollback

Git history is the historical recovery mechanism. This migration intentionally does not keep duplicate legacy specification bodies in the active tree. Compatibility pointers are retained only where current technical verification requires the path.

Rollback means reverting this governance change, not editing Mobile application code.

## No silent downgrade

This note exists to satisfy PRISMA document precedence: prior specifications are not silently erased. Their authority is explicitly migrated to the single canon, while Git history preserves historical context.
