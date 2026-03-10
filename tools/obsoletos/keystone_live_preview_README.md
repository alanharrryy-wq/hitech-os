# Keystone Live Preview Launcher

## File
- `F:\repos\hitech-os\tools\keystone_live_preview.bat`

## What it does
- Auto-detects repo root from script location (`..\` from `tools`).
- Runs preflight checks:
  - `node -v`
  - `pnpm -v`
- Installs dependencies only when needed (`node_modules` heuristic).
- Launches Studio in a new terminal with:
  - `pnpm -C <REPO_ROOT> keystone:scene:studio`
- Waits 3 seconds and opens Studio URL in default browser.
- Writes a timestamped log to:
  - `<REPO_ROOT>\tools\logs\keystone_live_preview\YYYYMMDD_HHMMSS_keystone_live_preview.log`
- Avoids duplicate Studio launch when a matching window title is already running.

## How to run
From any directory:

```bat
F:\repos\hitech-os\tools\keystone_live_preview.bat
```

or run it while your current directory is already `F:\repos\hitech-os\tools`:

```bat
keystone_live_preview.bat
```

## Configure Studio URL
Open `keystone_live_preview.bat` and change this line near the top:

```bat
set "STUDIO_URL=http://localhost:3000"
```

## Notes
- The script does not run Playwright.
- The script does not run smoke tests.
- The script does not update visual baselines.
