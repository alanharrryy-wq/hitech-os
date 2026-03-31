# DeltaForge

DeltaForge Console is a session-based PySide6 workstation for controlled declarative file operations.

## Run

```powershell
cd F:\repos\hitech-os\apps\deltaforge
python .\deltaforge_app.py
```

## Current shell capabilities

- Session tabs (new/clone/close) with isolated state
- Scope loading from files/folders
- Ops document load/save and inline editing
- Validate / Plan / Apply / Rollback / Refresh wired to a mock engine adapter
- Per-session plan+diff preview, right-side detail pane, and bottom execution surface tabs
- Internal event bus with required event contracts
- File watcher marks sessions stale on filesystem changes
- Centralized DeltaForge theme/tokens + reusable UI primitives
