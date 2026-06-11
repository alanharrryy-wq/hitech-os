# arr14 overlay install

This package fixes the installer strategy. It no longer renames or moves the full target folder.

Why: Windows can return WinError 32 when the folder is open as the current PowerShell location or held by another process. The installer now:

- validates source before touching target;
- backs up replaced files individually to `F:\Trash-old`;
- copies complete package files into the existing folder;
- moves stale files to `F:\Trash-old`;
- writes `F:\descargasf\plawshot_latest_rollback.json`;
- supports rollback without moving the whole target folder.

Runtime policy remains: no start, no kill, no DB, no deploy, no permanent delete.
