# orchestrator_bridge

Wave 6 implementation for the `orchestrator_bridge` plugin package.

## Scope of this wave
This package keeps the bridge runner, parser, persistence, tests, and host integration from Waves 1-5 and adds a premium UI/UX finish on top:
- visual design tokens embedded in the plugin for a sober, high-contrast dock theme,
- animated status header with subtle process motion while the external runner is active,
- execution timeline panel for high-signal events and operator feedback,
- refined result affordances for copying, opening the ZIP, and opening the containing folder,
- consistent button, field, hover, focus, pressed, and disabled states,
- responsive two-row dock layout that remains bridge-only and non-blocking.

What it still does not do:
- no motor business logic,
- no run or round orchestration logic inside the plugin,
- no lock or idempotency logic from the engine,
- no new dependencies,
- no host-core modifications outside the plugin package and runtime artifacts under `tools\_local`.

## Files
- `plugin.py`: async bridge runner, parser integration, persistence, premium dock UI, and microinteractions.
- `plugin.json`: host manifest updated for Wave 6.
- `bridge_config.json`: plugin runtime configuration defaults.
- `README.md`: operational notes for this wave.
- `PREMIUM_UI_DESIGN_NOTES_OLA6.md`: design tokens, state language, motion rules, and extension notes.
- `MANIFIESTO_DE_LOTE_OLA6.md`: lot manifest and validation commands.
- `tests/`: stdlib-only tests and fixtures from Wave 5 kept compatible.

## Tests
Run from the plugin package directory:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

## Safe host registration
`plugin.py` keeps the same safe host registration strategy:
- `register_safe_dock`
- `register_safe_toolbar_action`
- `register_safe_menu_action`
