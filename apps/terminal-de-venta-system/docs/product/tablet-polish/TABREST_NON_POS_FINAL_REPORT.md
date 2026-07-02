# TABREST_NON_POS Final Report

Date: 2026-07-02
Status: PASS local static validation plus live `/sync` smoke

## Scope Completed

- Corrected the user-requested cobro prerequisite back to a light premium palette before continuing non-POS work.
- Corrected the CSS Modules pure-selector build error by routing the cobro overlay through a local CSS module class.
- Created the required initial inventory documents before non-POS source patches.
- Polished Tablet non-POS surfaces: Home, Shell/Nav, Shift, Sales export, Sales detail fallback, Offline/backup, Sync/pending, License copy, Settings export copy, Outbox support route, and Estado operativo candidate route.
- Reworked `/sync` after live Tablet/PC review: limited the initial queue, exposed PC connection state, moved the dock inline to avoid overlapping cards, and corrected partial PC dispatch reporting.
- Added TABREST-specific verifiers and package scripts.
- Did not start a dev server.
- Did not kill processes.
- Did not create ZIPs.
- Did not commit or push.

## Main Changes

- Home now presents a cleaner one-glance start surface with six primary access cards and no runtime/support panel.
- Shell uses `PRISMA Tablet` and labels `/sync` as `Pendientes`.
- Shift copy is professional, and open/close panels now carry active-state styling.
- Sales export and offline export are closed details by default.
- Sync foregrounds pending work first; account/device/catalog/support details are secondary disclosures.
- Sync now shows only an 8-item operational preview by default, offers `Ver todos`, and keeps Tablet/PC health visible in the hero.
- Sync no longer reports PC HTTP 202/207 as clean success; it surfaces partial delivery as an operator warning.
- The `/sync` dock is inline for this surface, so it no longer floats over the pending list.
- License removed the visible `Refresh remoto` wording and keeps readonly posture.
- `/events/outbox` copy is translated to pending/movement language.
- `/prisma-pulse` visible copy is renamed to `Estado operativo`.

## Validation

- `pnpm run verify:tablet-cobro-light-amounts-0207`: PASS.
- `pnpm run verify:tabrest-non-pos-0207`: PASS.
- `pnpm run verify:tabrest-sync-human-pending-0207`: PASS.
- `pnpm run verify:tablet-sync-dispatcher`: PASS.
- `pnpm exec tsc --noEmit`: PASS.
- `pnpm run verify:zero-important`: PASS.
- `git diff --check`: PASS.
- Owner map JSON parse: PASS.
- Live Tablet `/sync` at `http://127.0.0.1:3120/sync`: PASS in tablet and PC viewports.
- Live Tablet PC health `http://127.0.0.1:3120/api/pos/sync/health/pc`: PASS, PC online.
- Live PC health `http://127.0.0.1:3130/api/health`: PASS.
- Live dispatch partial semantics: PASS, Tablet now returns `ok:false`, `reason:"partial"`, `httpStatus:207` instead of clean success.

## Not Run

- A new dev server was not started; live checks used the already running Tablet/PC servers.
- Full Next production build is not green in this environment: direct `pnpm exec next build --webpack` got past the prior CSS selector failure and then failed on `EPERM: operation not permitted, scandir 'C:\Users\alanh\Configuración local'`.

## Classification

PASS for repo-native static, TypeScript, copy/navigation, zero-priority, sync dispatcher, and live `/sync` Tablet/PC smoke. Full production build remains blocked by the unrelated Windows `EPERM` scan issue above.
