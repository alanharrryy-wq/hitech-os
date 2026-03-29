# UI_SCAFFOLDING

Tooling-only scaffolding for UI component generation.
No automatic app redesign is performed.

## Modules

- `tools/hos/ui/scaffold_component.py`
- `tools/hos/ui/controls/generate_controls.py`
- `tools/hos/ui/controls/templates/*`

## Generated Structure

For a component named `StatusCard`:

- `StatusCard.tsx`
- `StatusCard.styles.css`
- `StatusCard.stories.tsx`
- `StatusCard.test.tsx`
- `index.ts`

## Commands

```powershell
python tools/hos/ui/scaffold_component.py --name StatusCard
python tools/hos/ui/controls/generate_controls.py --kind toggle --name OpsToggle
python tools/hos/ui/controls/generate_controls.py --kind slider --name ThroughputSlider
python tools/hos/ui/controls/generate_controls.py --kind dropdown --name ProfileDropdown
```

Outputs default to `tools/_local/ui_scaffold/...` unless `--out-dir` is provided.

## Design Rules in Templates

- Token-friendly CSS variables.
- Deterministic story/test placeholders.
- No mutation of existing app components.

