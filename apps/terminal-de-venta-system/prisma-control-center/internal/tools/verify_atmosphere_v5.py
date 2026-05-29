from pathlib import Path
import sys, json
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"<REPO_ROOT>\apps\terminal-de-venta-system\prisma-control-center")
web = root / "internal" / "web"
index = web / "index.html"
checks = {}
checks["index_exists"] = index.exists()
text = index.read_text(encoding="utf-8", errors="ignore") if index.exists() else ""
for rel in [
    "vendor/pixi.min.js",
    "vendor/gsap.min.js",
    "prisma_cc_atmosphere_v5.css",
    "prisma_cc_atmosphere_v5.js",
]:
    checks[f"file:{rel}"] = (web / rel).exists()
    checks[f"index_mentions:{rel}"] = rel in text
css = (web / "prisma_cc_atmosphere_v5.css").read_text(encoding="utf-8", errors="ignore") if (web / "prisma_cc_atmosphere_v5.css").exists() else ""
js = (web / "prisma_cc_atmosphere_v5.js").read_text(encoding="utf-8", errors="ignore") if (web / "prisma_cc_atmosphere_v5.js").exists() else ""
checks["canvas_behind_ui_css"] = "#prisma-atmosphere-v5" in css and "z-index:0" in css and "pointer-events:none" in css
checks["exact_tactical_pseudolayers_disabled"] = 'body[data-theme="tactical"]::before' in css and 'body[data-theme="tactical"]::after' in css
checks["pixi_guardrail_js"] = "background atmosphere" in js and "pointer-events:none" in js
checks["gsap_drift_js"] = "window.gsap.to" in js
checks["motion_adapter_js"] = "installMotionAdapter" in js
ok = all(checks.values())
for k,v in checks.items():
    print(("PASS" if v else "FAIL"), k)
print(json.dumps({"ok": ok, "root": str(root)}, ensure_ascii=False))
sys.exit(0 if ok else 1)
