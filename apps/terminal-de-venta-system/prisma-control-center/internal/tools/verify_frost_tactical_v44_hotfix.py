from pathlib import Path
import sys
root = Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
idx = root/'internal'/'web'/'index.html'
css = root/'internal'/'web'/'prisma_frost_tactical_v44_hotfix.css'
html = idx.read_text(encoding='utf-8', errors='ignore') if idx.exists() else ''
css_text = css.read_text(encoding='utf-8', errors='ignore') if css.exists() else ''
checks = {
    'index_exists': idx.exists(),
    'css_exists': css.exists(),
    'link_present': 'prisma_frost_tactical_v44_hotfix.css' in html,
    'background_grid_kill': 'body::before{display:none' in css_text,
    'blue_gray_text': '--p44-text:#d7e6f5' in css_text,
    'neon_tokens': '--p44-glow-blue' in css_text and '--p44-glow-violet' in css_text,
    'nested_flatten': 'Nested panels' in css_text,
}
for k,v in checks.items():
    print(('PASS' if v else 'FAIL'), k)
if not all(checks.values()):
    sys.exit(1)
