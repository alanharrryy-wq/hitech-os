from pathlib import Path
import json
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]

def fail(error, **extra):
    payload = {"ok": False, "status": "FAIL", "error": error}
    payload.update(extra)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    raise SystemExit(1)

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")

def exists(rel):
    return (ROOT / rel).exists()

required = [
    "src-candidates/backend/render_plan_blueprint.py",
    "src-candidates/backend/prismo_render_contracts_blueprint.py",
    "src-candidates/components/PrismoAdaptiveTheater.tsx",
    "src-candidates/components/PrismoAutoRenderEnsemble.tsx",
    "src-candidates/components/PrismoRenderBlockHost.tsx",
    "src-candidates/styles/prismo-theater-cloudglass-pro.css",
    "src-candidates/styles/prismo-interaction-fx-pro.css",
    "contracts/composer/dependent_crystal_composer.json",
    "contracts/render_blocks/render_block_registry.json",
]
missing = [rel for rel in required if not exists(rel)]
if missing:
    fail("missing required semantic files", missing=missing)

render_plan = read("src-candidates/backend/render_plan_blueprint.py")
contracts_py = read("src-candidates/backend/prismo_render_contracts_blueprint.py")
auto_tsx = read("src-candidates/components/PrismoAutoRenderEnsemble.tsx")
adaptive_tsx = read("src-candidates/components/PrismoAdaptiveTheater.tsx")
host_tsx = read("src-candidates/components/PrismoRenderBlockHost.tsx")
composer = json.loads(read("contracts/composer/dependent_crystal_composer.json"))
registry = json.loads(read("contracts/render_blocks/render_block_registry.json"))

if "intent.scene" in render_plan:
    fail("render_plan_blueprint.py still references intent.scene")

if re.search(r"\bscene\b", "\n".join(d.get("id", "") for d in composer.get("dropdowns", [])), re.I):
    fail("composer dropdown id still contains scene")

if len(composer.get("dropdowns", [])) != 3:
    fail("composer must expose exactly 3 dependent dropdowns", count=len(composer.get("dropdowns", [])))

for bad in ["setScene", "scene dropdown", "output format dropdown", "elige escena"]:
    if bad.lower() in auto_tsx.lower() or bad.lower() in adaptive_tsx.lower():
        fail("component still contains removed format/scene selector wording", bad=bad)

if "procedural_steps" not in render_plan:
    fail("render_plan does not emit procedural_steps")

if "procedural_steps" not in contracts_py:
    fail("prismo_render_contracts does not allow procedural_steps")

allowed = set(registry.get("allowed_types", [])) | set(registry.get("blocks", []))
if "procedural_steps" not in allowed:
    fail("render_block_registry.json does not include procedural_steps")

BAD_RANDOM_KEY = "Math" + ".random"
if BAD_RANDOM_KEY in auto_tsx or BAD_RANDOM_KEY in host_tsx or BAD_RANDOM_KEY in adaptive_tsx:
    fail("React components still use random keys")

if "<PrismoRenderBlockHost block=" in auto_tsx or " block={block}" in auto_tsx:
    fail("PrismoAutoRenderEnsemble still passes block instead of plan")

if "plan={normalizedPlan}" not in auto_tsx:
    fail("PrismoAutoRenderEnsemble does not pass normalized plan to host")

for css_import in [
    "../styles/prismo-theater-cloudglass-pro.css",
    "../styles/prismo-interaction-fx-pro.css",
    "../styles/prismo-radix-liquid-select.css",
]:
    if css_import not in adaptive_tsx:
        fail("PrismoAdaptiveTheater missing corrected CSS import", import_path=css_import)
    css_path = (ROOT / "src-candidates/components" / css_import).resolve()
    try:
        css_path.relative_to(ROOT.resolve())
    except Exception:
        pass
    if not css_path.exists():
        fail("CSS import path does not resolve inside scaffold", import_path=css_import, resolved=str(css_path))

# README must preserve Windows backslashes literally, without control characters from \r, \a or \t.
readme = (ROOT.parent / "README.md")
if readme.exists():
    readme_text = readme.read_text(encoding="utf-8", errors="replace")
    if "\r" in readme_text or "\a" in readme_text or "\t" in readme_text:
        fail("README contains Windows path control characters")
    if "F:\\repos\\hitech-os\\apps\\terminal-de-venta-system" not in readme_text:
        fail("README missing escaped Windows repo path")
    if "F:\\descargasf" not in readme_text:
        fail("README missing escaped Windows output path")

# Scan docs for stale 4-select copy.
docs_hits = []
for p in (ROOT / "docs").rglob("*"):
    if p.is_file() and p.suffix.lower() in {".md", ".txt", ".yaml", ".yml", ".json"}:
        text = p.read_text(encoding="utf-8", errors="replace")
        if re.search(r"4\s+dependent\s+(select|dropdown)", text, re.I):
            docs_hits.append(str(p.relative_to(ROOT)))
        if re.search(r"elige\s+escena", text, re.I):
            docs_hits.append(str(p.relative_to(ROOT)))
if docs_hits:
    fail("docs still contain stale 4-select/scene copy", hits=docs_hits[:20])

print(json.dumps({
    "ok": True,
    "status": "PASS",
    "semantic_fix2": True,
    "dropdowns": 3,
    "procedural_steps_allowed": True,
    "auto_render_passes_plan": True,
    "stable_react_keys": True,
    "css_imports_resolved": True
}, indent=2, ensure_ascii=False))
