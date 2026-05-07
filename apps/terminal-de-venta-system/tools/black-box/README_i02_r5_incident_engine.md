# PRISMA black-box i02 R5 Incident Engine

This iteration adds local incident management for PRISMA black-box without touching Tablet, PC, Mobile, DB, schema, contracts, or shared-kernel files.

## What it owns

- `F:\Black-box\incidents\active\...`
- `F:\Black-box\incidents\resolved\...`
- `F:\Black-box\runtime\incident_index.json`
- `F:\Black-box\runtime\last_incident.json`
- `F:\Black-box\reports\black_box_i02_r5_incident_engine_scan_*.json|md`
- `F:\Black-box\evidence\black_box_i02_r5_incident_engine_*`

## Commands

```powershell
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py" incidents scan --root "F:\repos\hitech-os\apps\terminal-de-venta-system" --out "F:\Black-box" --allow-blocked
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py" incidents list --out "F:\Black-box" --state active
python "F:\repos\hitech-os\apps\terminal-de-venta-system\tools\black-box\black_box.py" incidents last --out "F:\Black-box"
```

## Contract

- Fingerprints dedupe repeated active conditions.
- Active incidents append `timeline.jsonl`.
- Healthy scans can auto-resolve incidents owned by this engine.
- Incident records are JSON plus Markdown summary for human review.
