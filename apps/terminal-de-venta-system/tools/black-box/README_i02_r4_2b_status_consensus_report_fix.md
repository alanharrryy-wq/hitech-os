# PRISMA BLACK-BOX i02 R4.2b Status Consensus + Report Path Fix

This iteration patches `black_box.py status` through a guarded bootstrap. It does not rewrite app runtime code.

## What it fixes

1. Report path contract: if status prints `Report: ...`, the printed path is a real canonical report under `F:\Black-box\reports`.
2. Endpoint consensus: a single endpoint timeout is retried before it becomes a caveat.
3. Evidence: original status, endpoint attempts, and normalized output are written under `F:\Black-box\evidence` and `F:\Black-box\runtime`.

## What it does not touch

- Tablet POS app files
- PC Backoffice app files
- Mobile app files
- DB/schema/contracts/shared-kernel

## Commands

```powershell
python "F:\descargasf\install_black_box_i02_r4_2b_status_consensus_report_fix.py" --run --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system" --out-root "F:\Black-box"
python "F:\descargasf\install_black_box_i02_r4_2b_status_consensus_report_fix.py" --rollback --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system" --out-root "F:\Black-box"
```

After install:

```powershell
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py" status --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --out "F:\Black-box" --allow-blocked
```
