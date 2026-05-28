from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
idx = root / "internal" / "web" / "index.html"
css = root / "internal" / "web" / "prisma_cc_atmosphere_v54.css"
js = root / "internal" / "web" / "prisma_cc_atmosphere_v54.js"

ok = True
checks = {
    "index_exists": idx.exists(),
    "css_exists": css.exists(),
    "js_exists": js.exists(),
    "index_links_css": idx.exists() and "prisma_cc_atmosphere_v54.css" in idx.read_text(encoding="utf-8", errors="ignore"),
    "index_links_js": idx.exists() and "prisma_cc_atmosphere_v54.js" in idx.read_text(encoding="utf-8", errors="ignore"),
}

for k, v in checks.items():
    print(("PASS" if v else "FAIL"), k)
    ok = ok and v

raise SystemExit(0 if ok else 1)
