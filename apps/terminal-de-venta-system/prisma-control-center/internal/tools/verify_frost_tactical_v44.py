from pathlib import Path
import sys
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
idx = root/'internal'/'web'/'index.html'
css = root/'internal'/'web'/'prisma_frost_tactical_v44_actual_visual_fix.css'
checks = []
checks.append(('index_exists', idx.exists()))
checks.append(('css_exists', css.exists()))
html = idx.read_text(encoding='utf-8', errors='ignore') if idx.exists() else ''
checks.append(('link_present', 'prisma_frost_tactical_v44_actual_visual_fix.css' in html))
checks.append(('link_after_v43', html.rfind('prisma_frost_tactical_v44_actual_visual_fix.css') > html.rfind('prisma_frost_tactical_v43.css')))
css_text = css.read_text(encoding='utf-8', errors='ignore') if css.exists() else ''
for token in ['.prismo-shell','body::before','--cc44-neon-cyan','rectangles']:
    if token == 'rectangles':
        checks.append(('flatten_prismo_present', '.prismoConsoleSurface' in css_text and '.prismo-response-card' in css_text))
    else:
        checks.append((f'css_token_{token}', token in css_text))
failed = False
for name, ok in checks:
    print(('PASS' if ok else 'FAIL'), name)
    failed = failed or not ok
sys.exit(1 if failed else 0)
