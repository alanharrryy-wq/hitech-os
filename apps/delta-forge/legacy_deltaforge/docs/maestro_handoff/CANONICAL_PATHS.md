# DeltaForge · Canonical Paths

Este documento elimina ambigüedad de ownership por concepto.

## Canonical paths (obligatorio)
| Concepto | Ruta canónica |
|---|---|
| Main window | `ui/window/main_window.py` |
| Command bar | `ui/widgets/command_bar.py` |
| Session tabs | `ui/widgets/session_tabs.py` |
| Settings store | `infrastructure/settings_store.py` |
| Chip primitive | `ui/primitives/chip.py` |
| Section card primitive | `ui/primitives/section_card.py` |
| Separator primitive | `ui/primitives/hairline_separator.py` |

## Duplicate ownership resolution
| Duplicado | Decisión | Estado final |
|---|---|---|
| `ui/panes/session_tabs.py` vs `ui/widgets/session_tabs.py` | `ui/widgets/session_tabs.py` canónico | `ui/panes/session_tabs.py` = shim-only |
| `ui/panes/command_bar.py` vs `ui/widgets/command_bar.py` | `ui/widgets/command_bar.py` canónico | `ui/panes/command_bar.py` = shim-only |
| `infrastructure/persistence/settings_store.py` vs `infrastructure/settings_store.py` | `infrastructure/settings_store.py` canónico | `infrastructure/persistence/settings_store.py` = shim-only |
| `ui/primitives/chip.py` vs `ui/primitives/chips.py` | `ui/primitives/chip.py` canónico | `ui/primitives/chips.py` = shim-only |
| `ui/primitives/section_card.py` vs `ui/primitives/cards.py` | `ui/primitives/section_card.py` canónico | `ui/primitives/cards.py` = shim-only |
| `ui/primitives/hairline_separator.py` vs `ui/primitives/separators.py` | `ui/primitives/hairline_separator.py` canónico | `ui/primitives/separators.py` = shim-only |
| `ui/window/main_window.py` vs `ui/window/main_window_alt.py` | `ui/window/main_window.py` canónico | `ui/window/main_window_alt.py` = shim-only |

## Legacy / shim policy (enforceable)
1. Archivos legacy solo pueden ser shims temporales.
2. Un shim solo puede re-exportar o forwardear a la ruta canónica.
3. Ningún shim puede introducir comportamiento nuevo.
4. Ningún import nuevo puede apuntar a rutas legacy.
5. Implementación real solo vive en la ruta canónica.
6. Si un shim requiere lógica, se reabre gate y se migra esa lógica al canónico.

## Enforcement checks
```powershell
rg -n "main_window_alt|ui\.panes\.command_bar|ui\.panes\.session_tabs|ui\.primitives\.chips|ui\.primitives\.cards|ui\.primitives\.separators|infrastructure\.persistence\.settings_store" F:\repos\hitech-os\apps\deltaforge
rg -n "from ui\.window import DeltaForgeMainWindow" F:\repos\hitech-os\apps\deltaforge\bootstrap
```

Si aparece un import nuevo a legacy path, el merge se bloquea.
