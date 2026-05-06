from __future__ import annotations
import json
from pathlib import Path
root = Path.cwd()
checks = {
  "pos_repair_marker": (root/"components/pos/pos.module.css", "PRISMA_POS_LAYOUT_CONTAINMENT_REPAIR_260503_V01_BEGIN"),
  "pos_two_column_guard": (root/"components/pos/pos.module.css", "clamp(320px, 32vw, 430px)"),
  "pos_mobile_collapse": (root/"components/pos/pos.module.css", "@media (max-width: 1160px)"),
  "shell_repair_marker": (root/"components/tablet-shell/prisma-tablet-shell.module.css", "PRISMA_POS_LAYOUT_CONTAINMENT_REPAIR_260503_V01_BEGIN"),
  "shell_tablet_grid_guard": (root/"components/tablet-shell/prisma-tablet-shell.module.css", "clamp(88px, 13vw, 220px) minmax(0, 1fr)"),
  "shell_breakpoint_guard": (root/"components/tablet-shell/prisma-tablet-shell.module.css", "@media (max-width: 760px)"),
}
result = {"ok": True, "checks": {}}
for name, (file, needle) in checks.items():
    text = file.read_text(encoding="utf-8") if file.exists() else ""
    ok = needle in text
    result["checks"][name] = {"file": str(file.relative_to(root)) if file.exists() else str(file), "contains": ok}
    result["ok"] = result["ok"] and ok
for rel in ["components/pos/pos.module.css", "components/tablet-shell/prisma-tablet-shell.module.css"]:
    file = root/rel
    text = file.read_text(encoding="utf-8") if file.exists() else ""
    result["checks"][rel + ":alignment_lock_removed"] = {"contains_alignment_marker": "PRISMA_POS_VISUAL_DOM_ALIGNMENT_LOCK_260503" in text}
    if "PRISMA_POS_VISUAL_DOM_ALIGNMENT_LOCK_260503" in text:
        result["ok"] = False
print(json.dumps(result, indent=2, ensure_ascii=False))
if not result["ok"]:
    raise SystemExit(1)
