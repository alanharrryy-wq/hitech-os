# Keystone Cloudflare Deployment Hardening Report

Date: 2026-03-04
Scope: `apps/keystone/**` only

## What Changed and Why

1. Added Windows-safe Cloudflare preview wrapper.
   Reason: reduce native Windows temp-file `ENOENT` failures in `cf:preview` and provide deterministic operator guidance.

2. Added deterministic Studio dev launcher with port fallback.
   Reason: when `3100` is busy, select first free port in ascending order (`3101..3199`) and print a clear startup banner.

3. Standardized Cloudflare deploy scripts.
   Reason: make deploy flow explicit for default, preview, and production targets.

4. Expanded deployment documentation.
   Reason: provide a complete operator path for local dev, OpenNext build, preview/deploy, secrets mapping, and troubleshooting.

## Files Added / Modified

- Added: `apps/keystone/scripts/scene-studio-dev.mjs`
- Added: `apps/keystone/scripts/cf-windows-safe.mjs`
- Added: `apps/keystone/docs/FINAL_REPORT.md`
- Modified: `apps/keystone/package.json`
- Modified: `apps/keystone/docs/CLOUDFLARE_DEPLOY.md`
- Existing and retained:
  - `apps/keystone/open-next.config.ts`
  - `apps/keystone/wrangler.jsonc`
  - `apps/keystone/.gitignore`

## Commands to Run

From repository root:

```bash
pnpm -C apps/keystone install
pnpm -C apps/keystone keystone:scene:studio
pnpm -C apps/keystone cf:build
pnpm -C apps/keystone cf:preview
pnpm -C apps/keystone cf:deploy
pnpm -C apps/keystone cf:deploy:preview
pnpm -C apps/keystone cf:deploy:prod
```

Secrets:

```bash
pnpm -C apps/keystone exec wrangler secret put API_TOKEN --env preview
pnpm -C apps/keystone exec wrangler secret put API_TOKEN --env production
```

## Lightweight Validation Executed

Executed:

- `pnpm -C apps/keystone install` -> PASS
- `pnpm -C apps/keystone build` -> PASS
- `pnpm -C apps/keystone cf:build` -> PASS

Additional runtime checks:

- `pnpm -C apps/keystone cf:preview` -> FAIL on native Windows due Wrangler/OpenNext `ENOENT`; wrapper now prints WSL recommendation and docs link.
- `pnpm -C apps/keystone keystone:scene:studio` -> port fallback behavior confirmed (`3100` busy -> `3101` selected). If `.next/dev/lock` is held, script now prints a clear recovery hint.

## Known Limitations

1. Native Windows preview for OpenNext/Wrangler can still fail with `ENOENT` in `.wrangler/tmp` even with temp override.
   Recommended path: run `cf:preview` from WSL.

2. Next.js dev lock (`.next/dev/lock`) allows a single active dev instance per app directory.
   If lock is active, reuse existing process URL or stop old process before relaunch.
