# MIRROR_INPUTS

Mirror-input helpers provide a lightweight state pattern where one input reflects to one or more listeners.
This is tooling output only and not wired into product UI by default.

## Module

- `tools/hos/ui/mirror_state.py`

## Generated Helper

- `mirror-store.ts` with:
  - `createMirrorStore`
  - `getState`
  - `setValue`
  - `patch`
  - `subscribe`

## Usage

```powershell
python tools/hos/ui/mirror_state.py
python tools/hos/ui/mirror_state.py --with-demo
```

Default output path:

- `tools/_local/ui_scaffold/mirror/`

## Determinism Notes

- Helper file content is static and reproducible.
- Generated file formatting uses normalized LF newlines.

