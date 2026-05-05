from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
checks = {}
files = {
    "pos_css": ROOT / "components" / "pos" / "pos.module.css",
    "shell_css": ROOT / "components" / "tablet-shell" / "prisma-tablet-shell.module.css",
}
for key, path in files.items():
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    checks[key] = {
        "exists": path.exists(),
        "geometry_reset_marker": "PRISMA_POS_GEOMETRY_RESET_260503_V03_BEGIN" in text,
        "dom_binding_v02_removed": "PRISMA_POS_VISUAL_DOM_BINDING_LOCK_260503_V02_BEGIN" not in text,
        "layout_containment_v01_removed": "PRISMA_POS_LAYOUT_CONTAINMENT_REPAIR_260503_V01_BEGIN" not in text,
        "force_lock_removed": "PRISMA_POS_VISUAL_FORCE_LOCK_260503_BEGIN" not in text,
        "alignment_lock_removed": "PRISMA_POS_VISUAL_DOM_ALIGNMENT_LOCK_260503" not in text,
    }
ok = all(v for item in checks.values() for v in item.values())
print(json.dumps({"ok": ok, "checks": checks}, indent=2, ensure_ascii=False))
if not ok:
    raise SystemExit(1)
