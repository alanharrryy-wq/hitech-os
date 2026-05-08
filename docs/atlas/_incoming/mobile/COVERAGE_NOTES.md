# Mobile Atlas Round 2 - Coverage Notes

## 1. Coverage source

Coverage is based only on the contents of `ATLAS_CHAT_MOBILE.zip` and the already generated Round 2 atlas package.

No claims are made from files that were not present in the ZIP unless explicitly marked as pending confirmation.

## 2. Covered areas

The staged atlas covers:

- Mobile app scope and ownership boundaries.
- Visible routes confirmed in the snapshot.
- Mobile API routes confirmed in the snapshot.
- Mobile visual surfaces under `src/components/prisma-app`.
- Functional engines under `src/lib/prisma-app`.
- Mobile data plane and environment variables observed in the package.
- PWA/install/offline runtime concerns.
- Verification and rollback patterns.
- Known open questions and release risks.

## 3. Excluded areas

The staged atlas intentionally excludes:

- Tablet internals.
- PC internals.
- Shared Core internals.
- Shared UI implementation details outside the Mobile snapshot.
- Android implementation files outside the Mobile snapshot.
- Cloudflare/infra scripts outside the Mobile snapshot.
- Any route, file, or responsibility not confirmable from the ZIP.

## 4. Confidence levels

### High confidence

- Mobile route list present in the snapshot.
- Mobile API route list present in the snapshot.
- Component names under `src/components/prisma-app`.
- PWA PNG asset gap.
- Staging path requirement.
- JSON parseability requirement.

### Medium confidence

- Exact runtime ownership of some service worker/PWA behavior, because full repo context may include supporting files outside the ZIP.
- Verification availability in repo complete state, because some scripts reference paths outside the ZIP package.

### Low confidence / pending

- Final source of truth for Tablet/PC contracts.
- Whether missing PWA PNGs were omitted from export or intentionally removed.
- Whether Android/Play Store scripts belong to Mobile release ownership or a separate release coordinator.

## 5. Round 1 issues addressed

- The atlas no longer treats `analysis/*` manifests as absolute truth when they disagree with physical ZIP contents.
- Missing PWA PNGs are documented as an open question and release risk.
- Shared Core is not documented as Mobile-owned.
- The staged upload avoids final project paths.
- The JSON file is prepared as parseable canonical JSON.

## 6. Promotion guidance

Before promoting from `_incoming/mobile` to any final docs path:

1. Re-run JSON parse on `atlas.mobile.json`.
2. Confirm all file paths still match current repo state.
3. Resolve or explicitly accept PWA asset open questions.
4. Confirm whether docs should be copied, transformed, or merged into final atlas locations.
5. Do not auto-promote into `products/mobile/app/docs/atlas/` without coordinator approval.
