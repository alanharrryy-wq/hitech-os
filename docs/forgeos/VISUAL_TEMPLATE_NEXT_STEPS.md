# ForgeOS Visual Template Next Steps

## Status

- Root authority bundle is installed at repo root.
- Root-quality gate is green using `Run-ForgeOS.ps1 quality-gate`.
- Reusable visual template incubation package is available at:
  - `forgeos/shared/pyside6_glass/`

## Objective

Homologate PySide6 visuals across tools without copying style logic per app.

## Canonical starter package

- `forgeos/shared/pyside6_glass/contracts.py`
- `forgeos/shared/pyside6_glass/theme.py`
- `forgeos/shared/pyside6_glass/backdrop.py`
- `forgeos/shared/pyside6_glass/scene.py`
- `forgeos/shared/pyside6_glass/chrome.py`
- `forgeos/shared/pyside6_glass/controls.py`
- `forgeos/shared/pyside6_glass/template.py`

## Round plan

1. R1 (code-atlas parity)
- Replace local visual builders with imports from the shared package.
- Keep behavior and layout stable (no product redesign).
- Gate: startup + selector/progress flow + no corner leaks.

2. R2 (deltaforge adapter)
- Introduce shared shell/chrome/cards into canonical window/dialog path.
- Keep domain/application untouched.
- Gate: startup smoke + no layer violations.

3. R3 (repo_analizer adapter)
- Apply shared shell in host surfaces, keep plugin runtime behavior.
- Gate: `dev_self_test` and engine_guardian validation green.

## Constraints

- No new external dependencies.
- No business-logic movement between layers.
- No duplicated visual systems after adoption in each target.
- Any change to frozen visual radii/tokens must start in the shared package.

## Progress snapshot

- R1 started and bridged in `apps/code-atlas/code-atlas.py` (scene/theme/controls).
- R2 started in `apps/deltaforge`:
  - `ui/window/main_window.py` mounts the shared glass scene wrapper.
  - `ui/theme/stylesheet.py` composes shared base stylesheet + local overrides.
  - `ui/primitives/confirm_dialog.py` and `ui/primitives/busy_dialog.py` now render through the shared glass scene.
  - `ui/dialogs/confirm_dialog.py` no longer uses `QMessageBox`; it routes through the canonical glass confirm dialog.
  - `ui/dialogs/busy_dialog.py` is now a shim to the canonical primitive implementation.
  - `ui/dialogs/rollback_dialog.py` adopts the shared shell/cards/button language.
- R3 started in `tools/graphviz/repo_analizer`:
  - `app/gui_qt/shell/central_workspace.py` now mounts a shared `QFrame#Shell` via `build_glass_dialog_scene`.
  - `app/gui_qt/skins.py` now composes shared glass stylesheet base + local skin stylesheet overrides.
- Shared template hardened in `forgeos/shared/pyside6_glass/template.py`:
  - configurable header/status/actions and visibility toggles.
  - stable `slots` contract preserved with additional `cards/actions` handles for adapters.
