# PySide6 Glass Shared Template

Canonical reusable visual base extracted from the current code-atlas glass language.

## Purpose

Provide one reusable shell and primitive set so new tools can be assembled fast with the same UI language:

- clean shell
- hero card
- main/side cards
- footer/status surfaces
- shared backdrop/chrome/buttons/theme

## Frozen invariants

- `QFrame#Shell` radius: 28 (`progress`: 26)
- `QFrame#WindowChrome` radius: 12
- `QFrame[card="hero"]` radius: 22
- `QFrame[card="true"|"muted"|"footer"]` radius: 18
- silver-frost-cyan palette as default
- rounded clip on backdrop to avoid corner leaks

## Modules

- `contracts.py`: frozen shape contract.
- `theme.py`: palette + stylesheet builder.
- `backdrop.py`: animated frosted background.
- `scene.py`: stage/content/backdrop composer.
- `chrome.py`: frameless top chrome.
- `controls.py`: canonical button factory.
- `template.py`: reusable slot-based panel template.

## Usage sketch

```python
from forgeos.shared.pyside6_glass import GlassPanelTemplate

template = GlassPanelTemplate(
    title="My Tool",
    subtitle="Fast shell with reusable slots",
    include_default_actions=True,
)
template.slots.hero_slot.addWidget(my_header_widget)
template.slots.main_slot.addWidget(my_main_widget)
template.slots.side_slot.addWidget(my_side_widget)
template.set_status_text("Ready.")
template.bind_submit(run_pipeline)
```

## Template API highlights

- `slots`: stable composition layouts (`hero`, `main`, `side`, `footer`, `status`).
- `cards`: direct access to shell/card widgets for advanced composition.
- `actions`: optional default cancel/submit buttons.
- `set_title`, `set_subtitle`, `set_eyebrow`, `set_status_text`.
- `set_side_visible`, `set_footer_visible`, `set_status_visible`.
- `bind_cancel`, `bind_submit`, `set_submit_enabled`.
- `add_footer_action` to append custom actions.
- `clear_slot(slot_name)` to rebuild sections cleanly.

## Migration policy

- Adapters in each tool compose slots and wire behavior.
- Tool adapters must not redefine shared radii/palette/backdrop/chrome.
- Any visual change to invariants must happen here first.
