from pathlib import Path
BAD=['safe mode','preview only','coming soon','próximamente','future placeholder']
ROOT=Path(__file__).resolve().parents[1]
VISIBLE_ROOTS=[ROOT/'src-candidates'/'components', ROOT/'src-candidates'/'styles']
hits=[]
for root in VISIBLE_ROOTS:
    if not root.exists():
        continue
    for p in root.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.tsx','.ts','.css'}:
            s=p.read_text(encoding='utf-8', errors='ignore').lower()
            for b in BAD:
                if b in s:
                    hits.append((str(p.relative_to(ROOT)),b))
print({'ok': not hits, 'hits': hits[:20], 'checked_roots':[str(r.relative_to(ROOT)) for r in VISIBLE_ROOTS]})
raise SystemExit(0 if not hits else 1)
