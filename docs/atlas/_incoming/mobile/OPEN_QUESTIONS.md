# Mobile Atlas Round 2 - Open Questions

## 1. PWA icon assets

The ZIP references several PNG assets that are not present in the Mobile snapshot. Confirm whether these assets exist elsewhere in the full monorepo or whether references should be changed in a future functional patch.

Pending paths:

- `public/icons/prisma_playstore_icon_192.png`
- `public/icons/prisma_playstore_icon_512.png`
- `public/apple-touch-icon.png`
- `public/apple-touch-icon-precomposed.png`
- `public/icons/prisma_ios_touch_icon_180.png`
- `public/icons/prisma_whatsapp_install_icon.png`

## 2. Source of truth for public asset manifest

The ZIP includes analysis files that appear to list assets not physically present in the extracted package. Confirm whether the analysis manifest came from a different repository state or whether the ZIP export omitted files.

## 3. Shared styles materialization

Mobile CSS references shared visual tokens/styles that are not owned by Mobile. Confirm the expected full-repo paths and whether atlas consumers should treat them as build-time dependencies only.

## 4. Android and Play Store tooling

Some scripts reference Android/Play Store tooling outside the Mobile app snapshot. Confirm whether those files belong to a separate Android package, a monorepo root toolchain, or a later release package.

## 5. Cloudflare/infra tooling

Some referenced infra scripts appear outside the Mobile app snapshot. Confirm ownership and whether Mobile release readiness depends on them.

## 6. Tablet and PC source contracts

Mobile data plane depends on Tablet and PC origins. Confirm final source contracts for:

- sales today
- cash current
- inventory watchlist
- alerts
- reports daily
- branches
- health/source states

## 7. Branch selection semantics

The presence of `/api/mobile/branches` suggests branch/sucursal awareness. Confirm whether Mobile allows branch selection, only displays branch context, or inherits branch from another source.

## 8. Production verification environment

Confirm which checks must run from the full repo versus which can run inside the extracted ZIP package. The ZIP is not guaranteed to be self-contained for build/release checks.

## 9. Final atlas destination

This delivery intentionally stages files under `docs/atlas/_incoming/mobile/`. Confirm the coordinator process that promotes these files to final atlas locations, if applicable.
