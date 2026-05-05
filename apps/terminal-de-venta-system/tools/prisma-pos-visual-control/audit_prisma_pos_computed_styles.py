#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, re
from pathlib import Path
from datetime import datetime

KEYS = ['background','backgroundColor','backdropFilter','border','boxShadow','opacity','color','transform','zIndex']
COMPONENTS = {
  'productCard': '.productCard, [data-prisma-component="ProductCard"]',
  'productImageStage': '.productImageStage, [data-prisma-component="ProductImageStage"]',
  'productPackshot': '[data-prisma-packshot-host] img, .productPackshot',
  'ticketPanel': '[data-prisma-component="CartPanel"]',
  'ticketLine': '[data-prisma-component="CartItemRow"]',
  'checkoutLink': '[data-prisma-component="CheckoutButton"]',
  'searchCard': '[data-prisma-component="SearchBar"]',
  'categoryRail': '.categoryRail',
  'sidebar': '[data-prisma-component="Sidebar"]',
  'header': '[data-prisma-component="TopBar"]',
  'mainContent': '#contenido-principal'
}

def static_probe(root: Path):
    css = root/'products/tablet/app/components/pos/pos.module.css'
    shell = root/'products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css'
    text = ''
    for p in [css, shell]:
        if p.exists(): text += p.read_text(encoding='utf-8', errors='replace') + '\n'
    return {'cssFilesPresent': [str(p) for p in [css,shell] if p.exists()], 'posCssVars': sorted(set(re.findall(r'--prisma-pos-[A-Za-z0-9_-]+', text))), 'hasBackdropFilter': 'backdrop-filter' in text, 'hasBoxShadow': 'box-shadow' in text, 'hasDataComponents': 'data-prisma-component' in ''.join(x.read_text(encoding='utf-8', errors='replace') for x in (root/'products/tablet/app/components/pos').glob('*.tsx'))}

def run_playwright(url: str):
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return {'ok': False, 'reason': f'Playwright unavailable: {exc}'}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width':1440,'height':1000})
            page.goto(url, wait_until='networkidle', timeout=20000)
            values = {}
            for name, selector in COMPONENTS.items():
                handle = page.query_selector(selector)
                if not handle:
                    values[name] = {'found': False, 'selector': selector}
                    continue
                values[name] = page.evaluate('''(el, keys) => { const s = getComputedStyle(el); const out = {found:true}; for (const k of keys) out[k] = s[k]; return out; }''', handle, KEYS)
                values[name]['selector'] = selector
            browser.close()
            return {'ok': True, 'components': values}
    except Exception as exc:
        return {'ok': False, 'reason': str(exc)}

def main():
    ap = argparse.ArgumentParser(description='Audit computed styles for PRISMA Tablet /pos. Falls back to static diagnostics without Playwright.')
    ap.add_argument('--url', default='http://127.0.0.1:3120/pos')
    ap.add_argument('--target-root', default='F:\\repos\\hitech-os\\apps\\terminal-de-venta-system')
    ap.add_argument('--output-dir', default='F:\\descargasf')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--markdown', action='store_true')
    args = ap.parse_args()
    root = Path(args.target_root)
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    result = {'generatedAt':datetime.now().isoformat(timespec='seconds'), 'url':args.url, 'targetRoot':str(root), 'static':static_probe(root), 'browser':run_playwright(args.url)}
    stamp=datetime.now().strftime('%y%m%d_%H%M')
    if args.json or not args.markdown:
        p=out/f'prisma_pos_computed_style_audit_{stamp}.json'
        p.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps(result,indent=2,ensure_ascii=False)); print(f'WROTE {p}')
    if args.markdown:
        p=out/f'prisma_pos_computed_style_audit_{stamp}.md'
        lines=['# PRISMA POS Computed Style Audit','',f'- URL: `{args.url}`',f'- Browser audit: **{result["browser"].get("ok")}**']
        if not result['browser'].get('ok'): lines.append(f'- Diagnostic: `{result["browser"].get("reason")}`')
        lines += ['', '## Static diagnostics', f'- CSS files present: {len(result["static"]["cssFilesPresent"])}', f'- POS CSS vars seen: {len(result["static"]["posCssVars"])}', f'- Has backdrop-filter: {result["static"]["hasBackdropFilter"]}', f'- Has box-shadow: {result["static"]["hasBoxShadow"]}']
        p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        print(f'WROTE {p}')
if __name__ == '__main__': main()
