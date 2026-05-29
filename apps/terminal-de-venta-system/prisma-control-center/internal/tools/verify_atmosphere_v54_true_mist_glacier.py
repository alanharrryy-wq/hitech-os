from pathlib import Path
import sys
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"<REPO_ROOT>\apps\terminal-de-venta-system\prisma-control-center")
web = root / "internal" / "web"
index = web / "index.html"
required = [
    web / "prisma_cc_atmosphere_v54_true_mist_glacier.css",
    web / "prisma_cc_atmosphere_v54_true_mist_glacier.js",
    web / "vendor" / "pixi.min.js",
    web / "vendor" / "gsap.min.js",
]
text = index.read_text(encoding="utf-8", errors="ignore") if index.exists() else ""
checks = {
    "index_exists": index.exists(),
    "css_linked": "prisma_cc_atmosphere_v54_true_mist_glacier.css" in text,
    "js_linked": "prisma_cc_atmosphere_v54_true_mist_glacier.js" in text,
    "old_probe_unlinked": "prisma_cc_atmosphere_v53_probe.js" not in text and "prisma_cc_atmosphere_v53_probe.css" not in text,
}
for p in required:
    checks[str(p.name if p.parent.name != "vendor" else "vendor/" + p.name)] = p.exists()
for k, v in checks.items():
    print(("PASS" if v else "FAIL"), k)
if not all(checks.values()):
    raise SystemExit(1)
