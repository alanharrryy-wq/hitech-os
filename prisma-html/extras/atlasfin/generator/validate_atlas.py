from __future__ import annotations
import json, sys
from html.parser import HTMLParser
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
issues = []
pages = ["index.html", "a-fundamentos.html", "b-materiales.html", "c-acciones.html", "d-entrada-texto.html", "e-seleccion-filtros.html", "f-navegacion.html", "g-tablas.html", "h-listas.html", "i-paneles-cards.html", "j-expansion.html", "k-estados-feedback.html", "l-carga-progreso.html", "m-overlays.html", "n-operativos.html", "o-patrones-pantalla.html", "p-movimiento.html", "q-responsive-accesibilidad.html", "r-contenido.html", "s-analitica.html", "t-archivos-medios.html", "u-calendario.html", "v-comercio-pagos.html", "w-identidad-seguridad.html", "x-sistema-diagnostico.html", "y-i18n-impresion-offline.html", "z-gobierno.html"]
letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
new_letters = ["N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y"]
page_map = {"A": "a-fundamentos.html", "B": "b-materiales.html", "C": "c-acciones.html", "D": "d-entrada-texto.html", "E": "e-seleccion-filtros.html", "F": "f-navegacion.html", "G": "g-tablas.html", "H": "h-listas.html", "I": "i-paneles-cards.html", "J": "j-expansion.html", "K": "k-estados-feedback.html", "L": "l-carga-progreso.html", "M": "m-overlays.html", "N": "n-operativos.html", "O": "o-patrones-pantalla.html", "P": "p-movimiento.html", "Q": "q-responsive-accesibilidad.html", "R": "r-contenido.html", "S": "s-analitica.html", "T": "t-archivos-medios.html", "U": "u-calendario.html", "V": "v-comercio-pagos.html", "W": "w-identidad-seguridad.html", "X": "x-sistema-diagnostico.html", "Y": "y-i18n-impresion-offline.html", "Z": "z-gobierno.html"}

required = pages + [
    "assets/css/atlas.css",
    "assets/js/atlas.js",
    "assets/data/atlas.manifest.json",
    "assets/data/atlas.manifest.js",
    "assets/data/atlas.tokens.json",
    "governance/AUTHORITY_MESH.json",
    "governance/LAYERS_MAP.json",
    "governance/ATLAS_COMPLETION_CONTRACT.json",
]

for rel in required:
    if not (root / rel).is_file():
        issues.append({"code":"MISSING","path":rel})

manifest = json.loads((root / "assets/data/atlas.manifest.json").read_text(encoding="utf-8"))
css = (root / "assets/css/atlas.css").read_text(encoding="utf-8", errors="replace")
js = (root / "assets/js/atlas.js").read_text(encoding="utf-8", errors="replace")

if manifest.get("total_items") != 418:
    issues.append({"code":"TOTAL_ITEMS","actual":manifest.get("total_items")})
if len(manifest.get("sections", [])) != 26:
    issues.append({"code":"SECTION_COUNT","actual":len(manifest.get("sections", []))})
if manifest.get("public_page_count") != 27:
    issues.append({"code":"PAGE_COUNT","actual":manifest.get("public_page_count")})
if manifest.get("implemented_sections") != letters:
    issues.append({"code":"IMPLEMENTED_SECTIONS"})
if manifest.get("completion_contract", {}).get("id") != "ATLAS.COMPLETE.NY":
    issues.append({"code":"COMPLETION_ID"})

section_items = {
    section["letter"]: [item["id"] for item in section["items"]]
    for section in manifest["sections"]
}

for letter in new_letters:
    page = page_map[letter]
    text = (root / page).read_text(encoding="utf-8", errors="replace")
    for item_id in section_items[letter]:
        if item_id not in text:
            issues.append({"code":"ITEM_CARD_MISSING","page":page,"item_id":item_id})

markers = {
    "n-operativos.html":["data-cash-input","data-single-choice"],
    "o-patrones-pantalla.html":["data-pattern-tabs","data-screen-demo"],
    "p-movimiento.html":["data-motion-range","data-motion-lab"],
    "q-responsive-accesibilidad.html":["data-viewport-demo",'role="switch"'],
    "r-contenido.html":["data-copy-source","data-copy-button"],
    "s-analitica.html":["data-chart-point","atlas-donut-demo"],
    "t-archivos-medios.html":["data-drop-zone","data-file-input"],
    "u-calendario.html":["data-calendar-demo","data-countdown"],
    "v-comercio-pagos.html":["atlas-payment-cards","atlas-receipt-demo"],
    "w-identidad-seguridad.html":["data-mfa-otp","data-signin-form"],
    "x-sistema-diagnostico.html":["data-run-diagnostics","data-log-viewer"],
    "y-i18n-impresion-offline.html":["data-locale","data-reconnect"],
}
for page, wanted in markers.items():
    text=(root/page).read_text(encoding="utf-8",errors="replace")
    for marker in wanted:
        if marker not in text:
            issues.append({"code":"PAGE_MARKER","page":page,"marker":marker})

for marker in [
    "PRISMA VISUAL FAMILY ATLAS · COMPLETE N-Y",
    "content-visibility: auto",
    "contain-intrinsic-size: auto 680px",
    ".atlas-line-chart",
    ".atlas-drop-demo",
    "@media print",
]:
    if marker not in css:
        issues.append({"code":"CSS_MARKER","marker":marker})

for marker in [
    "PRISMA Atlas Complete N-Y",
    "selectSingle",
    "formatLocale",
    "data-run-diagnostics",
]:
    if marker not in js:
        issues.append({"code":"JS_MARKER","marker":marker})

if "!important" in css:
    issues.append({"code":"IMPORTANT_FORBIDDEN"})
if ".atlas-energy-ring {" in css or 'ring.className = "atlas-energy-ring"' in js:
    issues.append({"code":"CLICK_PARTICLE_REGRESSION"})

class Parser(HTMLParser):
    pass
for page in pages:
    try:
        Parser().feed((root/page).read_text(encoding="utf-8",errors="replace"))
    except Exception as error:
        issues.append({"code":"HTML_PARSE","page":page,"error":str(error)})

report={
    "status":"PASS" if not issues else "FAIL",
    "pages":len(pages),
    "sections":len(manifest.get("sections",[])),
    "elements":manifest.get("total_items"),
    "implemented_sections":manifest.get("implemented_sections"),
    "new_sections":new_letters,
    "new_items_documented":sum(len(section_items[x]) for x in new_letters),
    "important_rules":0,
    "new_important_rules":0,
    "issues":issues,
}
(root/"reports/VALIDATION_REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if report["status"]=="PASS" else 2)
