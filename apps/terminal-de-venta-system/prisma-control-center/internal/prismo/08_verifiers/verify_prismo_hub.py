from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

required = [
    ROOT / "00_index" / "PRISMO_INDEX.md",
    ROOT / "00_index" / "PRISMO_FILE_MAP.json",
    ROOT / "00_index" / "PRISMO_RUNTIME_LAYERS.md",
    ROOT / "07_memory" / "MEMORY_TYPES.md",
    ROOT / "09_codex" / "CODEX_PROMPT_DELTA_PRISMO_HUB.md",
]

for path in required:
    if not path.exists():
        errors.append(f"missing:{path}")

if (ROOT / "00_index" / "PRISMO_FILE_MAP.json").exists():
    data = json.loads((ROOT / "00_index" / "PRISMO_FILE_MAP.json").read_text(encoding="utf-8", errors="replace"))
    files = data.get("files", [])
    cats = {f.get("category") for f in files}
    if "01_learning_core_runtime" not in cats:
        errors.append("missing learning_core_runtime category")
    if "04_theater_web_runtime" not in cats:
        errors.append("missing theater_web_runtime category")
    if not any("prismo_ai_bridge.py" in f.get("relative_path", "") for f in files):
        errors.append("missing prismo_ai_bridge.py in file map")

texts = []
for path in required:
    if path.exists() and path.suffix.lower() in {".md", ".txt", ".json"}:
        texts.append((path, path.read_text(encoding="utf-8", errors="replace")))

for path, text in texts:
    low = text.lower()
    if "4 dependent dropdown" in low or "fourth dropdown" in low and "no fourth" not in low:
        errors.append(f"bad fourth dropdown wording:{path}")
    if "intent.scene" in text and "no `intent.scene`" not in text and "no intent.scene" not in low:
        errors.append(f"bad intent.scene wording:{path}")
    for phrase in ["coming soon", "preview only", "safe mode"]:
        if phrase in low:
            bad_lines = []
            for line in low.splitlines():
                if phrase not in line:
                    continue

                allowed_context = (
                    "no " in line
                    or "not " in line
                    or "do not" in line
                    or "must not" in line
                    or "forbidden" in line
                    or "ban" in line
                    or "absent" in line
                    or "remove" in line
                    or "without" in line
                    or ("visible" in line and ("no" in line or "not" in line or "absent" in line))
                )

                if not allowed_context:
                    bad_lines.append(line.strip())

            if bad_lines:
                errors.append(f"forbidden visible label wording:{phrase}:{path}:{bad_lines[:3]}")

prompt = (ROOT / "09_codex" / "CODEX_PROMPT_DELTA_PRISMO_HUB.md").read_text(encoding="utf-8", errors="replace")
for must in [
    "3 dependent dropdowns",
    "Auto Render Ensemble",
    "Theater Query",
    "procedural memory",
    "no Playwright",
    "no screenshots",
    "no opaque glass downgrade",
]:
    if must.lower() not in prompt.lower():
        errors.append(f"prompt missing:{must}")

print(json.dumps({"ok": not errors, "errors": errors, "hub": str(ROOT)}, indent=2, ensure_ascii=False))
if errors:
    sys.exit(1)
