from __future__ import annotations
import json, py_compile, re, sys, threading, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / 'internal' / 'web'
PYROOT = ROOT / 'internal' / 'py'
checks=[]
def add(name, ok, detail=''):
    checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

def main():
    index = WEB / 'index.html'
    css = WEB / 'prisma_frost_tactical.css'
    js = WEB / 'prisma_frost_tactical.js'
    img = WEB / 'assets' / 'simon-spring-zmMrlEHsFQY-unsplash.jpg'
    for p in [index, css, js, img]:
        add('exists:' + str(p.relative_to(ROOT)), p.exists(), str(p))
    html = index.read_text(encoding='utf-8', errors='replace') if index.exists() else ''
    css_text = css.read_text(encoding='utf-8', errors='replace') if css.exists() else ''
    js_text = js.read_text(encoding='utf-8', errors='replace') if js.exists() else ''
    add('index-links-frost-css-v4', '/prisma_frost_tactical.css?v=frost-tactical-v4-background-panel-system' in html)
    add('index-links-frost-js-v4', '/prisma_frost_tactical.js?v=frost-tactical-v4-background-panel-system' in html)
    add('index-preloads-background', '/assets/simon-spring-zmMrlEHsFQY-unsplash.jpg' in html)
    add('tactical-label-v4', 'Tactical Frost V4' in html and 'Tactical Frost V4' in js_text)
    add('css-targets-tactical-only', 'body[data-theme="tactical"]' in css_text)
    add('css-uses-local-background', "url('/assets/simon-spring-zmMrlEHsFQY-unsplash.jpg')" in css_text)
    add('v4-marker-present', 'PRISMA FROST TACTICAL V4' in css_text and 'BACKGROUND REPAIR + PREMIUM PANEL SYSTEM' in css_text)
    add('background-no-grid-v4', 'display:none; visibility:hidden' in css_text and 'v40QuickRail' in css_text and 'background-size:auto' in css_text)
    add('background-glacier-motion', '@keyframes frostV4Glacier' in css_text and '118s' in css_text)
    add('double-glass-panels', 'double glass' in css_text.lower() and 'inset 0 0 0 1px rgba(255,255,255,.055)' in css_text)
    add('optical-rim-hero', '--frost-v4-edge-hero' in css_text and 'drop-shadow(0 0 1px rgba(239,250,255,.34))' in css_text)
    add('shadow-executive-floating', '--frost-v4-shadow-executive' in css_text and '--frost-v4-shadow-floating' in css_text)
    add('glow-insight-violet-gauss', '--frost-v4-glow-insight' in css_text and '174,153,255' in css_text and '0 0 44px' in css_text)
    add('motion-silk-present', 'transition:transform .24s cubic-bezier(.2,.8,.2,1)' in css_text)
    add('custom-theme-combo', 'prisma-theme-combo' in css_text and 'function buildThemeCombo' in js_text)
    add('remove-quick-rail-js', 'function removeThemeRail' in js_text and 'PRISMA quick controls' in js_text)
    external_hits = re.findall(r'https?://', css_text + js_text)
    add('no-new-external-urls-in-frost-files', not external_hits, external_hits)
    add('image-size-ok', img.exists() and img.stat().st_size > 100_000, img.stat().st_size if img.exists() else 0)
    compile_fail=[]
    out = ROOT / 'internal' / '_verify_pycache'
    out.mkdir(exist_ok=True)
    for p in sorted(PYROOT.glob('*.py')):
        try:
            py_compile.compile(str(p), cfile=str(out / (p.stem + '.pyc')), doraise=True)
        except Exception as exc:
            compile_fail.append({'path': str(p), 'error': str(exc)})
    add('python-compile', not compile_fail, compile_fail)
    # Visual smoke: start local panel handler without requiring operational health PASS.
    try:
        sys.path.insert(0, str(PYROOT))
        from panel_3150 import PanelHandler
        from config_loader import CONTROL_CENTER_PORT
        from http.server import ThreadingHTTPServer
        server = ThreadingHTTPServer(('127.0.0.1', CONTROL_CENTER_PORT), PanelHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        time.sleep(.35)
        try:
            html_resp = urllib.request.urlopen(f'http://127.0.0.1:{CONTROL_CENTER_PORT}/', timeout=5)
            html_text = html_resp.read(320000).decode('utf-8', errors='ignore')
            css_resp = urllib.request.urlopen(f'http://127.0.0.1:{CONTROL_CENTER_PORT}/prisma_frost_tactical.css?v=frost-tactical-v4-background-panel-system', timeout=5)
            css_served = css_resp.read(400000).decode('utf-8', errors='ignore')
            health_resp = urllib.request.urlopen(f'http://127.0.0.1:{CONTROL_CENTER_PORT}/api/health', timeout=5)
            add('panel-static-smoke-v4', html_resp.status == 200 and css_resp.status == 200 and health_resp.status == 200 and 'CONTROL CENTER PRISMA' in html_text and 'PRISMA FROST TACTICAL V4' in css_served, {'htmlStatus': html_resp.status, 'cssStatus': css_resp.status, 'healthStatusCode': health_resp.status})
        finally:
            server.shutdown(); server.server_close()
    except Exception as exc:
        add('panel-static-smoke-v4', False, str(exc))
    ok = all(c['ok'] for c in checks)
    result = {'ok': ok, 'status': 'PASS' if ok else 'FAIL', 'checks': checks}
    (ROOT/'VERIFY_FROST_TACTICAL_V4_RESULT.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if ok else 2
if __name__ == '__main__':
    raise SystemExit(main())
