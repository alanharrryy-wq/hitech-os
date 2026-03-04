# Keystone on Cloudflare Workers (OpenNext)

This document defines the deployment flow for `apps/keystone` on Cloudflare Workers using OpenNext.

## 1) Workers vs Tunnel (short)

- Workers: deployment target for production/preview runtime (`wrangler deploy`).
- Tunnel: local exposure mechanism only; not required for standard Keystone local development.

## 2) Local Scene Studio (unchanged)

Run from `apps/keystone`:

```bash
pnpm keystone:scene:studio
```

This keeps hot reload and now auto-falls back from `3100` to the first free port in `3101..3199`.

## 3) Install dependencies

From repository root:

```bash
pnpm -C apps/keystone install
```

## 4) OpenNext build

From repository root:

```bash
pnpm -C apps/keystone cf:build
```

This generates the Worker output in `.open-next/`.

## 5) Local Cloudflare preview runtime

From repository root:

```bash
pnpm -C apps/keystone cf:preview
```

This runs the Worker locally with the `preview` environment.

On Windows, the wrapper script sets `TEMP/TMP/TMPDIR` to `apps/keystone/.wrangler/tmp` to reduce temp-file ENOENT failures.

## 6) Deploy to Cloudflare

From repository root:

```bash
pnpm -C apps/keystone cf:deploy
```

Environment-specific deploys:

```bash
pnpm -C apps/keystone cf:deploy:preview
pnpm -C apps/keystone cf:deploy:prod
```

## 7) Environment variable strategy

Never commit secrets in git. Use Wrangler secrets and per-environment vars.

### Non-secret vars (in `wrangler.jsonc`)

- Base vars go under top-level `vars`.
- Preview vars go under `env.preview.vars`.
- Production vars go under `env.production.vars`.

### Secrets (dashboard or CLI)

Preview:

```bash
pnpm -C apps/keystone exec wrangler secret put API_TOKEN --env preview
```

Production:

```bash
pnpm -C apps/keystone exec wrangler secret put API_TOKEN --env production
```

## 8) Cloudflare Workers Builds (GitHub) minimal guide

1. In Cloudflare dashboard, create/import the Worker project from GitHub.
2. Set the root directory to `apps/keystone`.
3. Build command:

```bash
pnpm install --frozen-lockfile && pnpm cf:build
```

4. Deploy command:

```bash
pnpm cf:deploy
```

5. Configure environment vars/secrets per environment (`preview`, `production`) in dashboard.
6. Enable branch previews for pull requests and map production branch explicitly.

## 9) Production route / custom domain guidance

Add `routes` / `custom_domain` entries in `apps/keystone/wrangler.jsonc` under `env.production` once domain ownership is ready.
Do not hardcode DNS provider credentials or secrets in the repository.

## 10) Troubleshooting

- `cf:build` passes but `cf:preview` fails on Windows with `ENOENT` under `.wrangler/tmp`:
  use WSL for local Worker preview (`pnpm -C apps/keystone cf:preview` in WSL shell).
- `keystone:scene:studio` fails with `EADDRINUSE :3100`:
  script now auto-selects next free port and prints the final URL.
- `keystone:scene:studio` reports `.next/dev/lock` already in use:
  another Next.js dev instance is already running for this app; reuse the existing URL or stop the old process.
- Worker runtime errors about missing Node APIs:
  ensure `nodejs_compat` is present in `wrangler.jsonc`.
- Cloudflare rejects old runtime compatibility:
  keep `compatibility_date` at or above `2024-09-23`.

## 11) Vercel decommission note

`vercel.json` is currently frozen (`git.deploymentEnabled=false`). Keep it until Cloudflare deployments are validated in preview + production.
