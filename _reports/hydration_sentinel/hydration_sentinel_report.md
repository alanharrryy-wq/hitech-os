# Hydration Sentinel Report

- Repo root: `F:\repos\hitech-os`
- Files scanned: **4969**
- Files skipped: **13752**
- Total findings: **5710**
- Baseline ignored: **0**
- Tool version: **2.0.0**

## Findings by category

- `browser_api_in_non_client`: 5359
- `client_boundary_hint`: 42
- `hydration_keyword`: 205
- `server_to_client_import_hint`: 32
- `suppress_hydration_warning`: 72

## Findings by severity

- `info`: 205
- `low`: 5391
- `medium`: 114

## Recommendations

- **HIGH** Aislar browser APIs fuera de client files -> Se detectaron window/document/localStorage/sessionStorage en archivos sin 'use client'.
- **MEDIUM** Limitar suppressHydrationWarning -> Prefiere root cause local antes que silenciar hydration mismatch a lo bruto.
- **MEDIUM** Aplicar client-only boundary estrecho en tooling interno con mutación externa -> Ideal para debug panels, HUDs y dev surfaces propensas a mutación pre-hydration.
- **LOW** Revisar imports server-ish hacia client files -> En Next puede ser válido, pero revisa serialización de props, bundle cost y boundary clarity.

## Likely internal tooling paths

- `apps/keystone/app/dev/_luxury/tools/clipboard.ts`
- `apps/keystone/app/dev/_luxury/tools/localStorageSafe.ts`
- `apps/keystone/app/dev/_luxury/tools/presetExport.ts`
- `apps/keystone/app/dev/kpi-supermarket/page.tsx`
- `apps/keystone/app/dev/layout.tsx`
- `apps/keystone/app/dev/scene-studio/floating-window-drag-policy.ts`
- `apps/keystone/app/dev/scene-studio/window-manager/clamp.ts`
- `apps/keystone/app/dev/scene-studio/window-manager/storage.ts`
- `apps/keystone/app/dev/style-lab/page.tsx`
- `apps/keystone/components/pitch/debug/pitch-layer-dev-tools-client-only.tsx`
- `tools/_local/visual/_capture_tmp/capture_runner.cjs`
- `tools/codex/_triage/snapshots/SNAP_20260226_1/BEFORE/apps/web/src/App.tsx`
- `tools/codex/_triage/snapshots/SNAP_20260226_1/BEFORE/apps/web/src/main.tsx`

## Risky broad workaround paths

- None detected from current heuristics.

## Sample findings

- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_0be41d72._.js:2237` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_0be41d72._.js:2241` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_3658bb3b._.js:1156` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_3658bb3b._.js:1160` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_3f772795._.js:1225` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_3f772795._.js:1229` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_559a581c._.js:1703` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_559a581c._.js:1707` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_5ad6c21d._.js:1156` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_5ad6c21d._.js:1160` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_8bc44d0f._.js:1251` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_8bc44d0f._.js:1255` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_db424706._.js:1885` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_db424706._.js:1889` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_f774c6dd._.js:1916` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/_f774c6dd._.js:1920` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/packages_ui-kit_dist_f2efa1d9._.js:1156` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/server/chunks/ssr/packages_ui-kit_dist_f2efa1d9._.js:1160` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/static/chunks/_02e5cd39._.js:1303` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/static/chunks/_02e5cd39._.js:1307` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/static/chunks/_20a6e07c._.js:1855` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/static/chunks/_20a6e07c._.js:1859` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/static/chunks/_4d9b0830._.js:1229` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/static/chunks/_4d9b0830._.js:1233` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/static/chunks/_88020bd3._.js:1366` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/static/chunks/_88020bd3._.js:1370` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/static/chunks/_c829e70e._.js:1229` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/static/chunks/_c829e70e._.js:1233` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/static/chunks/_cf189c10._.js:2040` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
- **MEDIUM** `suppress_hydration_warning` in `apps/keystone/.next/dev/static/chunks/_cf189c10._.js:2044` -> `suppressHydrationWarning` | suppressHydrationWarning detectado. Úsalo solo como excepción local y con root cause documentado.
