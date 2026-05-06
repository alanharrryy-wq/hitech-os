# PRISMA Black-Box i02 R4 OutputRouter

## Purpose

This iteration adds a conservative output routing layer to the local PRISMA black-box tooling.
It creates the canonical `F:\Black-box` layout, adds integrated `organize`, `cleanup`, and
`archive` commands to `black_box.py`, and normalizes loose runtime outputs at process exit.

## Installed files

- `tools/black-box/black_box_output_router.py`
- `tools/black-box/README_i02_r4_output_router.md`
- guarded hook inside `tools/black-box/black_box.py`

## Commands

```powershell
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py" organize --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --out "F:\Black-box"
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py" cleanup --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --out "F:\Black-box"
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py" archive --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --out "F:\Black-box" --older-than-days 30
```

## Non-goals

This iteration does not instrument Tablet, PC, Mobile, DB, schema, shared-kernel, or contracts.
It does not delete evidence. Cleanup is intentionally non-destructive.
