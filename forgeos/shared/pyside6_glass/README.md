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

template = GlassPanelTemplate(title="My Tool")
template.slots.hero_slot.addWidget(my_header_widget)
template.slots.main_slot.addWidget(my_main_widget)
template.slots.side_slot.addWidget(my_side_widget)
```

## Migration policy

- Adapters in each tool compose slots and wire behavior.
- Tool adapters must not redefine shared radii/palette/backdrop/chrome.
- Any visual change to invariants must happen here first.

