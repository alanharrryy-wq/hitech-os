
from __future__ import annotations
import json
from pathlib import Path

REQUIRED = [
 '01_SURFACE_REGISTRY.json','02_ROUTE_COMPONENT_MAP.json','03_COMPONENT_OWNERSHIP_MAP.json','04_LAYER_ROLE_KIND_MAP.json','05_SELECTOR_GRAPH.json','06_SELECTOR_USAGE.csv','07_TOKEN_GRAPH.json','08_LEGACY_TOKEN_ALIAS_MAP.json','09_STATE_MATRIX.json','10_CONTROL_APPLICABILITY_MATRIX.json','11_PRESET_ELIGIBILITY_REGISTRY.json','12_POS_PROTECTION_MAP.json','13_ZERO_MEANS_ZERO_AUDIT.json','16_PRESET_PROMOTION_CONTRACT.md','17_CONTINUATION.md','TABLET_MAP_MANIFEST.json'
]
BLOCKED_SUFFIXES = {'.db','.sqlite','.sqlite3','.env'}

def verify(out_dir: str) -> dict:
    root = Path(out_dir)
    missing = [x for x in REQUIRED if not (root / x).exists()]
    json_errors = []
    for p in root.glob('*.json'):
        try: json.loads(p.read_text(encoding='utf-8'))
        except Exception as exc: json_errors.append({'path':p.name,'error':str(exc)})
    raw = [str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and (p.suffix.lower() in BLOCKED_SUFFIXES or p.name.lower().startswith('.env'))]
    manifest = {}
    mp = root / 'TABLET_MAP_MANIFEST.json'
    if mp.exists():
        manifest=json.loads(mp.read_text(encoding='utf-8'))
    ok = not missing and not json_errors and not raw and bool(manifest.get('selectorCount',0) >= 0)
    return {'ok': ok, 'status': 'PASS_TABLET_MAP_VERIFY' if ok else 'FAIL_TABLET_MAP_VERIFY', 'missing': missing, 'jsonErrors': json_errors, 'rawBlockedFiles': raw, 'manifest': manifest}

if __name__ == '__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('out_dir')
    ns=ap.parse_args()
    result=verify(ns.out_dir)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result.get('ok') else 1)
