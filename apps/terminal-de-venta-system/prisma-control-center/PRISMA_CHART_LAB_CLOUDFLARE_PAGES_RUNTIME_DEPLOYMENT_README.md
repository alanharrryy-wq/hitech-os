# PRISMA Chart Lab Cloudflare Pages Runtime & Deployment README

> Operational README for PRISMA Chart Lab, local runtime, Cloudflare Pages deployment, Wrangler authentication, public URLs, local URLs, build hygiene, no-leak verification, and the final deployment incident recovery performed on 2026-05-19.

---

## 0. Document Status

| Field | Value |
|---|---|
| Project | PRISMA / HITECH OS |
| Vertical | Commerce |
| Component | Chart Lab |
| Public Cloudflare Pages Project | `prisma-chart-lab` |
| Main Public URL | `https://prisma-chart-lab.pages.dev/` |
| Last Known Successful Deployment URL | `https://fa654ed9.prisma-chart-lab.pages.dev` |
| Local Runtime URL | `http://127.0.0.1:3000` |
| Deployment Model | Cloudflare Pages static export |
| Tunnel Dependency | None for Chart Lab |
| Current Status | Build clean, no-leak clean, Wrangler installed, OAuth login working, manual Pages deploy succeeded |

---

## 1. Executive Summary

PRISMA currently has two different runtime families:

| Family | Components | Deployment / Runtime Model |
|---|---|---|
| Static cloud-native | Chart Lab | Next.js static export to Cloudflare Pages |
| Live operational runtime | Tablet, PC, Mobile, EIT, Forms, Control Center | Next.js/Node runtime exposed locally or through Cloudflare Tunnel |

The important architectural point is:

> **Chart Lab does not deploy through Cloudflare Tunnel. Chart Lab deploys as a static Cloudflare Pages project.**

This explains why Chart Lab can update through a static build and `wrangler pages deploy`, while other PRISMA services depend on live localhost processes, ports, cloudflared, and origin health.

---

## 2. Local Machine Paths

### Repository Root

```txt
F:\repos\hitech-os\apps\terminal-de-venta-system
```

### Chart Lab App Root

```txt
F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app
```

### Static Build Output Published to Cloudflare Pages

```txt
F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\out
```

### Main Public Runtime Snapshot Source

```txt
F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\src\prisma-charts\prisma-chart-runtime.snapshot.json
```

### Related Chart Runtime Source Files

```txt
F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\src\prisma-charts\chart-runtime-data.ts
F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\src\prisma-charts\chart-lab-control-model.ts
F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\src\prisma-charts\chart-lab-registry.tsx
F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\src\prisma-charts\chart-lab-types.ts
```

### Backup Created During Snapshot Sanitization

```txt
F:\descargasf\PRISMA_CHART_LAB_PUBLIC_SNAPSHOT_SANITIZE_BACKUP_20260519_155707.zip
```

---

## 3. Local URLs

| Component | Local URL |
|---|---|
| Chart Lab | `http://127.0.0.1:3000` |
| EIT / Web | `http://127.0.0.1:3110/` |
| Tablet | `http://127.0.0.1:3120/` |
| PC | `http://127.0.0.1:3130/` |
| Mobile | `http://127.0.0.1:3140/` |
| Control Center | `http://127.0.0.1:3150/` |
| Control Center Health | `http://127.0.0.1:3150/api/health` |

For another device on the same LAN, such as the SKYEGG K11 tablet, replace `127.0.0.1` with the PC LAN IP.

Example:

```txt
http://192.168.1.50:3000
```

---

## 4. Public Cloudflare URLs

| Component | Public URL | Platform |
|---|---|---|
| Chart Lab | `https://prisma-chart-lab.pages.dev/` | Cloudflare Pages |
| Last successful Chart Lab deployment | `https://fa654ed9.prisma-chart-lab.pages.dev` | Cloudflare Pages deployment URL |
| EIT / Web | `https://eit.hitechrts.com/` | Cloudflare Tunnel |
| Tablet | `https://tablet.hitechrts.com/` | Cloudflare Tunnel / runtime mapping |
| PC | `https://pc.hitechrts.com/` | Cloudflare Tunnel / runtime mapping |
| Mobile | `https://prisma.hitechrts.com/` | Cloudflare Tunnel / runtime mapping |
| Mobile Install | `https://prisma.hitechrts.com/prisma-app/install?from=whatsapp` | Cloudflare Tunnel / runtime mapping |
| Control Center | `https://control.hitechrts.com/` | Cloudflare Tunnel / runtime mapping |

---

## 5. Chart Lab Architecture

Chart Lab is a Next.js app that is exported to static files for Cloudflare Pages.

### Runtime Flow

```txt
Source files
  ↓
Next.js build
  ↓
Static export
  ↓
out/
  ↓
wrangler pages deploy
  ↓
Cloudflare Pages
  ↓
https://prisma-chart-lab.pages.dev/
```

### Local Development Flow

```txt
pnpm dev
  ↓
next dev --hostname 127.0.0.1 -p 3000
  ↓
http://127.0.0.1:3000
```

### Production-like Local Flow

```txt
pnpm start
  ↓
next start --hostname 127.0.0.1 -p 3000
  ↓
http://127.0.0.1:3000
```

---

## 6. Important Chart Lab Files

| File | Purpose |
|---|---|
| `products/chart-lab/app/package.json` | Chart Lab scripts and dependencies |
| `products/chart-lab/app/next.config.mjs` | Next.js static export configuration |
| `products/chart-lab/app/wrangler.jsonc` | Cloudflare Pages configuration |
| `products/chart-lab/app/deploy/cloudflare-pages.json` | Cloudflare Pages deploy metadata |
| `products/chart-lab/app/scripts/run-chart-lab-cf-build.mjs` | Cloudflare static build wrapper |
| `products/chart-lab/app/scripts/deploy-cloudflare-pages.mjs` | Non-interactive deploy wrapper |
| `products/chart-lab/app/scripts/verify-chart-lab-cloudflare.mjs` | Cloudflare package verification |
| `products/chart-lab/app/scripts/verify-chart-lab-no-leaks.mjs` | Public output leak scanner |
| `products/chart-lab/app/scripts/doctor-chart-lab-tunnel.ps1` | Tunnel diagnostic helper, not required for Pages deploy |
| `products/chart-lab/app/scripts/run-chart-lab-tunnel.ps1` | Optional tunnel helper, not the main Pages path |

---

## 7. Cloudflare Pages Configuration

### Project Name

```txt
prisma-chart-lab
```

### Wrangler Config File

```txt
products/chart-lab/app/wrangler.jsonc
```

### Key Settings

```json
{
  "name": "prisma-chart-lab",
  "pages_build_output_dir": "out"
}
```

### Published Directory

```txt
products/chart-lab/app/out
```

---

## 8. Required Local Tooling

| Tool | Required For | Current Observed Status |
|---|---|---|
| PowerShell 7.x | Running the operational commands | `PowerShell 7.6.1` observed |
| Node.js | Next.js, Wrangler, scripts | `Node.js v25.6.0` observed |
| pnpm | Monorepo package manager | `pnpm v9.15.9` observed |
| Next.js | Chart Lab build/runtime | `Next.js 16.1.6` observed |
| Wrangler | Cloudflare Pages deploy | repaired and verified as `wrangler 4.93.0` |
| Cloudflare OAuth | Direct manual deploy | working |
| `CLOUDFLARE_API_TOKEN` | Non-interactive wrapper deploy | still required for `chart-lab:cf:deploy` wrapper |

---

## 9. Main Commands

### Set Common Variables

```powershell
$Root = "F:\repos\hitech-os\apps\terminal-de-venta-system"
$App  = Join-Path $Root "products\chart-lab\app"
```

### Build Chart Lab for Cloudflare Pages

```powershell
pnpm -C $Root chart-lab:cf:build
```

### Verify Cloudflare Package

```powershell
pnpm -C $Root chart-lab:cf:verify
```

### Direct Deploy Using Wrangler OAuth

```powershell
pnpm -C $App exec wrangler pages deploy out --project-name=prisma-chart-lab --branch=main
```

### Direct Deploy With Dirty Git Warning Silenced

```powershell
pnpm -C $App exec wrangler pages deploy out --project-name=prisma-chart-lab --branch=main --commit-dirty=true
```

### Wrapper Deploy Requiring API Token

```powershell
$env:CLOUDFLARE_API_TOKEN = "<cloudflare-pages-token>"
pnpm -C $Root chart-lab:cf:deploy
```

Never commit or paste the real token into chat, docs, logs, screenshots, or the repo.

---

## 10. What Happened During the Incident

### Symptom

Local Chart Lab updated correctly, but Cloudflare Pages did not show the new version.

### Root Causes Found

1. `out/` was stale.
2. Cloudflare Pages serves `out/`, not live local source files.
3. The no-leak scanner blocked deploy because public output contained local machine paths.
4. Wrangler was installed in a broken state due to missing `miniflare`.
5. Wrangler OAuth login was not available until Wrangler was repaired.
6. The scripted deploy wrapper requires `CLOUDFLARE_API_TOKEN` even after OAuth login.
7. Direct `wrangler pages deploy` works with OAuth and successfully deployed.

---

## 11. Stale `out/` Diagnosis

The first issue was that the static output was older than the source files.

Observed result:

```txt
OUT ESTA VIEJO. Rebuilding...
```

This means local development was reading current source, while Cloudflare Pages was still serving static files generated earlier.

### Check Source vs Output Age

```powershell
$Root = "F:\repos\hitech-os\apps\terminal-de-venta-system"
$App = Join-Path $Root "products\chart-lab\app"

$OutIndex = Join-Path $App "out\index.html"
$LatestSource = Get-ChildItem `
  (Join-Path $App "src"), `
  (Join-Path $App "app"), `
  (Join-Path $App "public"), `
  (Join-Path $App "package.json"), `
  (Join-Path $App "next.config.mjs"), `
  (Join-Path $App "wrangler.jsonc") `
  -Recurse -File -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

$OutItem = Get-Item -LiteralPath $OutIndex -ErrorAction SilentlyContinue

Write-Host "Latest source: $($LatestSource.FullName)" -ForegroundColor Yellow
Write-Host "Latest source time: $($LatestSource.LastWriteTime)" -ForegroundColor Yellow
Write-Host "Out index: $OutIndex" -ForegroundColor Yellow
Write-Host "Out index time: $($OutItem.LastWriteTime)" -ForegroundColor Yellow

if ($LatestSource.LastWriteTime -gt $OutItem.LastWriteTime) {
  Write-Host "OUT ESTA VIEJO. Rebuilding..." -ForegroundColor Red
} else {
  Write-Host "OUT parece al dia." -ForegroundColor Green
}
```

Note: when using this diagnostic, ignore `.next/dev` as a meaningful source candidate if it appears. `.next/dev` is generated runtime material, not authored source.

---

## 12. Build Result

The Cloudflare static export build completed successfully.

Observed build highlights:

```txt
Next.js 16.1.6
Creating an optimized production build ...
Compiled successfully
Generating static pages
Route (app)
┌ ○ /
└ ○ /_not-found

[PRISMA Chart Lab] PASS: Cloudflare static export build complete
```

This proves the app can export as static content.

---

## 13. No-Leak Scanner Failure

After the first rebuild, verification failed with:

```txt
[PRISMA Chart Lab] FAIL: no-leak scanner failed for current out directory
```

### Meaning

The static output contained data that should not be published publicly.

### Main Leak Type

Local machine paths and local database evidence were found in public JavaScript output.

Examples of unsafe content class:

```txt
F:\repos\...
tablet-pos.db
databasePaths
sqlite-runtime
local DB evidence
```

### Why This Matters

Even if not a password, local absolute paths and DB names expose internal machine layout and operational evidence. That should not be shipped to Cloudflare Pages.

---

## 14. Snapshot Sanitization

The public snapshot source was sanitized.

### Files Checked

```txt
products\chart-lab\app\src\prisma-charts\prisma-chart-runtime.snapshot.json
products\chart-lab\app\src\prisma-charts\chart-runtime-data.ts
products\chart-lab\app\src\prisma-charts\chart-lab-control-model.ts
```

### Result

```txt
PATCHED: prisma-chart-runtime.snapshot.json
SIN CAMBIOS: chart-runtime-data.ts
SIN CAMBIOS: chart-lab-control-model.ts
```

### Backup Created

```txt
F:\descargasf\PRISMA_CHART_LAB_PUBLIC_SNAPSHOT_SANITIZE_BACKUP_20260519_155707.zip
```

### Sanitization Goal

Replace or remove:

```txt
F:\repos\...
C:\...
tablet-pos.db
.sqlite
.db
databasePaths with absolute local paths
evidence arrays containing local machine paths
```

with public-safe placeholders:

```txt
PRISMA_LOCAL_PATH_REDACTED
local-sqlite-snapshot
public-safe-runtime-snapshot
```

---

## 15. Clean Verification Result

After sanitization and rebuild, verification passed:

```txt
[PRISMA Chart Lab] PASS: no-leak scanner passed for current out directory
[PRISMA Chart Lab] PASS: Cloudflare verification complete
```

The remaining warnings were not blockers:

```txt
WARN: wrangler is not installed yet; run pnpm install
WARN: wrangler auth unavailable; deploy will require wrangler login or token
```

Those warnings were later resolved by repairing Wrangler.

---

## 16. Wrangler Failure and Repair

### Initial Wrangler Failure

Wrangler failed before login could open the browser.

Observed failure:

```txt
Cannot find module:
F:\repos\hitech-os\apps\terminal-de-venta-system\node_modules\.pnpm\wrangler@4.90.0\node_modules\miniflare\dist\src\index.js
```

### Meaning

Wrangler was installed in a broken or incomplete state. The missing package was `miniflare`, which Wrangler needs.

### Repair Commands Used

```powershell
$ErrorActionPreference = "Stop"

$Root = "F:\repos\hitech-os\apps\terminal-de-venta-system"
$App  = Join-Path $Root "products\chart-lab\app"

$WranglerBroken = Join-Path $Root "node_modules\.pnpm\wrangler@4.90.0"

if (Test-Path $WranglerBroken) {
  Remove-Item -LiteralPath $WranglerBroken -Recurse -Force
}

Get-ChildItem (Join-Path $Root "node_modules\.pnpm") -Filter "miniflare*" -Directory -ErrorAction SilentlyContinue |
  Remove-Item -Recurse -Force

pnpm store prune
pnpm -C $Root install --force
pnpm -C $App add -D wrangler@latest
pnpm -C $App exec wrangler --version
```

### Successful Repair Result

```txt
wrangler 4.93.0
```

---

## 17. Wrangler OAuth Login

After Wrangler was repaired, OAuth login worked.

### Command

```powershell
pnpm -C $App exec wrangler login
```

### Result

```txt
Attempting to login via OAuth...
Opening a link in your default browser...
Successfully logged in.
```

### Verify Login

```powershell
pnpm -C $App exec wrangler whoami
```

### Observed State

Wrangler reported an OAuth token associated with the Cloudflare account email used on the local machine.

Do not store OAuth tokens or API tokens in this README.

---

## 18. Why `chart-lab:cf:deploy` Still Failed

Even after OAuth login succeeded, this command still failed:

```powershell
pnpm -C $Root chart-lab:cf:deploy
```

because the project deploy wrapper requires a token:

```txt
[PRISMA Chart Lab] FAIL: Cloudflare Pages deploy blocked:
CLOUDFLARE_API_TOKEN is required for non-interactive Pages deploy.
```

### Meaning

There are two deploy modes:

| Mode | Command | Auth |
|---|---|---|
| Wrapper deploy | `pnpm -C $Root chart-lab:cf:deploy` | Requires `CLOUDFLARE_API_TOKEN` |
| Direct Wrangler deploy | `pnpm -C $App exec wrangler pages deploy ...` | Works with OAuth login |

The direct Wrangler deploy was used successfully.

---

## 19. Final Successful Deploy

### Command

```powershell
$Root = "F:\repos\hitech-os\apps\terminal-de-venta-system"
$App  = Join-Path $Root "products\chart-lab\app"

pnpm -C $App exec wrangler pages deploy out --project-name=prisma-chart-lab --branch=main
```

### Result

```txt
Success! Uploaded 25 files (26 already uploaded)
Deployment complete!
```

### Deployment URL

```txt
https://fa654ed9.prisma-chart-lab.pages.dev
```

---

## 20. Git Dirty Warning

During deploy, Wrangler warned:

```txt
Warning: Your working directory is a git repo and has uncommitted changes
```

This does not block deployment.

### Options

#### Recommended

Commit the relevant changes before deploy:

```powershell
git status
git add products/chart-lab/app
git commit -m "Sanitize Chart Lab public snapshot and refresh Cloudflare Pages build"
```

#### For manual deploys only

Silence the warning:

```powershell
pnpm -C $App exec wrangler pages deploy out --project-name=prisma-chart-lab --branch=main --commit-dirty=true
```

---

## 21. Production URL vs Deployment URL

Cloudflare returned:

```txt
https://fa654ed9.prisma-chart-lab.pages.dev
```

This is a deployment-specific URL.

The main project URL remains:

```txt
https://prisma-chart-lab.pages.dev/
```

If deploying to `--branch=main` and Cloudflare Pages production branch is `main`, the main URL should update to the latest production deployment.

If it does not:

1. Open the deployment-specific URL.
2. Open the main URL in incognito.
3. Hard refresh with `Ctrl + F5`.
4. Verify Cloudflare Pages project production branch.
5. Confirm the deployment branch is `main`.

---

## 22. Full Golden Path: Build, Verify, Deploy

Use this when Chart Lab changes and must be published.

```powershell
$ErrorActionPreference = "Stop"

$Root = "F:\repos\hitech-os\apps\terminal-de-venta-system"
$App  = Join-Path $Root "products\chart-lab\app"

Write-Host "=== Build Chart Lab static export ===" -ForegroundColor Cyan
pnpm -C $Root chart-lab:cf:build

Write-Host "=== Verify Chart Lab Cloudflare package ===" -ForegroundColor Cyan
pnpm -C $Root chart-lab:cf:verify

Write-Host "=== Verify Wrangler ===" -ForegroundColor Cyan
pnpm -C $App exec wrangler --version

Write-Host "=== Verify Cloudflare auth ===" -ForegroundColor Cyan
pnpm -C $App exec wrangler whoami

Write-Host "=== Deploy Chart Lab to Cloudflare Pages ===" -ForegroundColor Cyan
pnpm -C $App exec wrangler pages deploy out --project-name=prisma-chart-lab --branch=main
```

---

## 23. Token-Based Wrapper Deploy

Use this only if you intentionally want the project wrapper deploy path.

```powershell
$Root = "F:\repos\hitech-os\apps\terminal-de-venta-system"

$env:CLOUDFLARE_API_TOKEN = "<cloudflare-pages-token>"

pnpm -C $Root chart-lab:cf:deploy
```

### Token Rules

- Do not commit tokens.
- Do not paste tokens into chat.
- Do not save tokens in README files.
- Prefer a scoped Cloudflare token with Pages deploy permissions.
- Clear the variable after use if needed:

```powershell
Remove-Item Env:CLOUDFLARE_API_TOKEN -ErrorAction SilentlyContinue
```

---

## 24. Processes Involved

### Build-Time Processes

| Process / Tool | Role |
|---|---|
| `pnpm` | Runs workspace scripts |
| `node` | Executes build and verification scripts |
| `next build --webpack` | Builds Chart Lab static output |
| `scripts/run-chart-lab-cf-build.mjs` | Wraps the Cloudflare static build |
| `scripts/verify-chart-lab-cloudflare.mjs` | Checks Cloudflare deployment readiness |
| `scripts/verify-chart-lab-no-leaks.mjs` | Scans `out/` for unsafe public leaks |
| `wrangler` | Deploys `out/` to Cloudflare Pages |

### Install-Time / Repair Processes

| Process / Tool | Role |
|---|---|
| `pnpm store prune` | Clears stale/corrupt pnpm package store metadata |
| `pnpm install --force` | Reinstalls workspace dependencies |
| `pnpm add -D wrangler@latest` | Ensures local Wrangler is installed |
| `workerd postinstall` | Installs Cloudflare workerd binary dependency |
| `esbuild postinstall` | Installs esbuild binary dependency |

### Cloudflare Runtime Processes

| Process / Tool | Role |
|---|---|
| Cloudflare Pages | Serves static Chart Lab output |
| Wrangler OAuth | Authenticates local deploys |
| `wrangler pages deploy` | Uploads static assets to Pages |
| Cloudflare CDN | Serves deployed static files globally |

### Not Required for Chart Lab Pages Deploy

| Tool | Why Not Required |
|---|---|
| `cloudflared` | Chart Lab Pages deploy does not use Tunnel |
| Live Next.js server | Pages serves static `out/` files |
| Local SQLite | Public Chart Lab output must not expose local DB paths |
| Prisma Client runtime | Chart Lab Pages build is static and public-safe |

---

## 25. Cloudflare Tunnel vs Cloudflare Pages

### Chart Lab

```txt
Cloudflare Pages
Static export
No live origin
No cloudflared tunnel
No localhost dependency after deploy
```

### EIT / Forms / Tablet / PC / Mobile / Control

```txt
Cloudflare Tunnel
cloudflared
localhost:<port>
live Next.js/Node process
origin must be running
```

### Runtime Mapping Previously Observed

```txt
engine.hitechrts.com -> localhost:3100
forms.hitechrts.com  -> localhost:3200
eit.hitechrts.com    -> localhost:3110
```

A `502` in Tunnel systems usually means Cloudflare can reach the tunnel but the local origin is down, not built, crashed, or not listening.

---

## 26. Troubleshooting Matrix

| Symptom | Likely Cause | Fix |
|---|---|---|
| Local changes visible, Cloudflare unchanged | `out/` stale or wrong branch deployed | Run `chart-lab:cf:build`, verify, deploy branch `main` |
| `no-leak scanner failed` | Public output contains local paths or DB evidence | Sanitize snapshot source, rebuild, verify |
| `wrangler not authenticated` | No OAuth/token available | Run `wrangler login` or set `CLOUDFLARE_API_TOKEN` |
| Login does not open browser | Wrangler failed before OAuth | Fix Wrangler installation |
| `Cannot find module miniflare` | Broken Wrangler/pnpm install | Remove broken pnpm packages, prune store, reinstall, add Wrangler |
| `CLOUDFLARE_API_TOKEN is required` | Script wrapper requires token | Use token or deploy directly with OAuth |
| `git repo has uncommitted changes` | Working tree dirty | Commit changes or pass `--commit-dirty=true` |
| Deployment URL works but main URL old | Production branch mismatch or cache | Check Pages production branch, hard refresh, deploy branch `main` |
| Cloudflare Tunnel URL returns 502 | Local origin down | Start local runtime and verify port |

---

## 27. Safe Snapshot Policy

Chart Lab public builds must never expose:

```txt
F:\...
C:\...
Users\
repos\
*.db
*.sqlite
tablet-pos.db
canonical DB paths
PC DB paths
local filesystem evidence
tokens
passwords
private keys
.env content
```

Allowed public-safe replacements:

```txt
PRISMA_LOCAL_PATH_REDACTED
local-sqlite-snapshot
public-safe-runtime-snapshot
sourceMode: sqlite-runtime
dataStatus: partial/adapter-ready
```

Operational metadata can be public if it does not expose machine-specific paths, secrets, client data, or private infrastructure.

---

## 28. Recommended Future Improvements

### 1. Make Public Snapshot Sanitization a First-Class Build Step

The build should generate a public-safe snapshot automatically instead of patching source manually.

Recommended direction:

```txt
private runtime snapshot
  ↓ sanitizer
public-safe snapshot
  ↓ build
out/
```

### 2. Separate Private and Public Runtime Evidence

Keep local operational evidence in private logs and only expose curated public state.

Recommended files:

```txt
prisma-chart-runtime.snapshot.private.json
prisma-chart-runtime.snapshot.public.json
```

### 3. Make Deploy Wrapper Support OAuth Mode

Current wrapper blocks unless `CLOUDFLARE_API_TOKEN` exists.

Recommended enhancement:

```txt
If CLOUDFLARE_API_TOKEN exists:
  use non-interactive token deploy
Else:
  allow OAuth wrangler deploy when whoami passes
```

### 4. Add a Deploy Receipt File

After deploy, write a receipt such as:

```txt
F:\descargasf\PRISMA_CHART_LAB_DEPLOY_RECEIPT_<timestamp>.json
```

Suggested receipt fields:

```json
{
  "project": "prisma-chart-lab",
  "branch": "main",
  "deploymentUrl": "https://fa654ed9.prisma-chart-lab.pages.dev",
  "sourceRoot": "F:\\repos\\hitech-os\\apps\\terminal-de-venta-system",
  "appRoot": "F:\\repos\\hitech-os\\apps\\terminal-de-venta-system\\products\\chart-lab\\app",
  "outputDir": "out",
  "noLeakPassed": true,
  "deployedAt": "2026-05-19"
}
```

### 5. Commit the Sanitization and Deploy Tooling

Before handing off or repeating this on another machine, commit the intended source changes.

---

## 29. Current Verified State

| Check | Status |
|---|---|
| Public snapshot sanitized | PASS |
| Static export build | PASS |
| Cloudflare verification | PASS |
| No-leak scanner | PASS |
| Wrangler installation | PASS |
| Wrangler version | `4.93.0` |
| Wrangler OAuth login | PASS |
| `wrangler whoami` | PASS |
| Wrapper deploy with no token | FAIL by design |
| Direct Wrangler deploy | PASS |
| Last deployment URL | `https://fa654ed9.prisma-chart-lab.pages.dev` |

---

## 30. Minimal Operator Checklist

Before deploy:

```powershell
$Root = "F:\repos\hitech-os\apps\terminal-de-venta-system"
$App  = Join-Path $Root "products\chart-lab\app"

pnpm -C $Root chart-lab:cf:build
pnpm -C $Root chart-lab:cf:verify
pnpm -C $App exec wrangler whoami
pnpm -C $App exec wrangler pages deploy out --project-name=prisma-chart-lab --branch=main
```

After deploy:

1. Open the deployment URL printed by Wrangler.
2. Open `https://prisma-chart-lab.pages.dev/`.
3. Hard refresh with `Ctrl + F5`.
4. Confirm the expected chart/UI changes appear.
5. Save the deployment URL in release notes or a deploy receipt.
6. Commit source changes if the deployment represents a real release.

---

## 31. PRISMA Canonical Architecture Reminder

Chart Lab is a visualization and governance layer. It must not become a hard dependency for base operation.

Canonical rule:

```txt
Tablet operates and sells independently.
PC governs if present.
Mobile supervises.
Shared/Core records, validates contracts, and preserves evidence.
Control audits.
```

Chart Lab can observe, visualize, and help govern runtime state, but it must not make Tablet operation dependent on Cloudflare Pages, Cloudflare Tunnel, PC, Mobile, or internet.

---

## 32. Final Operational Conclusion

The Chart Lab Cloudflare issue was not one single bug. It was a pipeline chain:

```txt
local source changed
  ↓
out/ stale
  ↓
rebuild succeeded
  ↓
no-leak blocked unsafe output
  ↓
snapshot sanitized
  ↓
verify passed
  ↓
wrangler broken
  ↓
wrangler repaired
  ↓
OAuth login succeeded
  ↓
wrapper deploy required token
  ↓
direct wrangler deploy succeeded
```

Current best deploy command:

```powershell
$App = "F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app"
pnpm -C $App exec wrangler pages deploy out --project-name=prisma-chart-lab --branch=main
```

Current known successful deployment:

```txt
https://fa654ed9.prisma-chart-lab.pages.dev
```

Main public URL:

```txt
https://prisma-chart-lab.pages.dev/
```
