# Keystone Live Preview Launcher (Pitch Runtime)

## File
- `F:\repos\hitech-os\tools\keystone_live_preview.bat`

## What it does
- Auto-detects repo root from script location (`..\` from `tools`).
- Runs preflight checks:
  - `node -v`
  - `pnpm -v`
- Installs dependencies only when needed (`node_modules` heuristic).
- Launches the Keystone app in a new terminal with:
  - `pnpm -C <REPO_ROOT> keystone:scene:studio`
- Waits 3 seconds and opens the **Pitch runtime** URL in the default browser.
- Prefers opening:
  - `http://127.0.0.1:3100/pitch?debug=1`
- Falls back across ports `3100`, `3101`, and `3000`, and across `127.0.0.1` / `localhost`.
- Writes a timestamped log to:
  - `<REPO_ROOT>\tools\logs\keystone_live_preview\YYYYMMDD_HHMMSS_keystone_live_preview.log`

## How to run
From any directory:

```bat
F:\repos\hitech-os\tools\keystone_live_preview.bat
```

or run it while your current directory is already `F:\repos\hitech-os\tools`:

```bat
keystone_live_preview.bat
```

## Configure Pitch URL
Open `keystone_live_preview.bat` and change this line near the top:

```bat
set "PITCH_URL=http://127.0.0.1:3100/pitch?debug=1"
```

## Notes
- The script still launches `keystone:scene:studio` because that command boots the app environment you were already using.
- The browser target is now **Pitch**, not `/dev/scene-studio`.
- The script does not run Playwright.
- The script does not run smoke tests.
- The script does not update visual baselines.
