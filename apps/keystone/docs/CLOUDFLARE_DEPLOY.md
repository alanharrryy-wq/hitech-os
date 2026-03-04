# Keystone on Cloudflare Workers (OpenNext)

This document defines the deployment flow for `apps/keystone` on Cloudflare Workers using OpenNext.

## 1) Local Scene Studio (unchanged)

Run from `apps/keystone`:

```bash
pnpm keystone:scene:studio
```

This keeps the local hot-reload workflow (`next dev -p 3100`) intact.

## 2) Install dependencies

From repository root:

```bash
pnpm -C apps/keystone install
```

## 3) OpenNext build

From repository root:

```bash
pnpm -C apps/keystone cf:build
```

This generates the Worker output in `.open-next/`.

## 4) Local Cloudflare preview runtime

From repository root:

```bash
pnpm -C apps/keystone cf:preview
```

This runs the Worker locally with the `preview` environment.

Note: OpenNext/Wrangler local preview may fail on native Windows in some setups.
If that happens, run this step from WSL for reliable behavior.

## 5) Deploy to Cloudflare

From repository root:

```bash
pnpm -C apps/keystone cf:deploy
```

This deploys using the `production` environment from `wrangler.jsonc`.

## 6) Environment variable strategy

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

## 7) Cloudflare Workers Builds (GitHub) minimal guide

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

## 8) Troubleshooting

- `cf:build` passes but `cf:preview` fails on Windows with `ENOENT` under `.wrangler/tmp`:
  use WSL for local Worker preview.
- `keystone:scene:studio` fails with `EADDRINUSE :3100`:
  another local dev process is already running on port `3100`.

## 9) Vercel decommission note

`vercel.json` is currently frozen (`git.deploymentEnabled=false`). Keep it until Cloudflare deployments are validated in preview + production.
