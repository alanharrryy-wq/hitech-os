# Dispatcher Changes

## 2026-02-27 — Dispatch Window Hardening + Operator Toolkit

### What changed

- Hardened `ahk_template.ahk` fallback behavior so each `new_hwnd_timeout` path logs both:
  - `fallback_title_scan`
  - `fallback_recent_code_window`
- Added guarded action signaling for keystroke action logs:
  - `open_codex_sidebar`
  - `paste_prompt`
  - `submit_prompt`
    now emit final `|true`.
- Added AHK-side result dedupe in `WriteResult` to prevent duplicate result lines per worker.
- Added optional strict result enforcement via `HOS_STRICT`:
  - when enabled, requires exactly one result line for `A_core`, `B_tooling`, `C_features`, `D_validation`.
- Added deterministic Pester suite for dispatch hardening invariants.
- Added wrapper script to generate/verify hardening test assets and run Pester.
- Added operator HowTo with auto/manual/strict workflows and troubleshooting.

### Why

- Prevent regressions where dispatcher stops after `new_hwnd_timeout` without executing/logging fallback selection logic.
- Guarantee observable guarded input flow in logs.
- Enforce stable, unambiguous worker result logging.
- Give operators a deterministic validation workflow with run pinning and strict mode.
