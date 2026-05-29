from pathlib import Path
import sys
root = Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
idx = root/'internal'/'web'/'index.html'
css = root/'internal'/'web'/'prisma_frost_tactical_v43.css'
text = idx.read_text(encoding='utf-8', errors='ignore') if idx.exists() else ''
checks = {
    'index_exists': idx.exists(),
    'css_exists': css.exists(),
    'link_present': 'prisma_frost_tactical_v43.css' in text,
}
for k,v in checks.items():
    print(('PASS' if v else 'FAIL'), k)
if not all(checks.values()):
    sys.exit(1)
