from __future__ import annotations
import hashlib,json
from pathlib import Path
def _h(p):
    h=hashlib.sha256();
    with p.open('rb') as f:
        for c in iter(lambda:f.read(65536),b''): h.update(c)
    return h.hexdigest()
def compute_plugin_registry_fingerprint(base_dir:Path)->str|None:
    base_dir=Path(base_dir).resolve(); plugins=base_dir/'capatch_plugins'; reg=plugins/'_plugin_registry.json'
    if reg.exists():
        try: return _h(reg)
        except Exception: return None
    if not plugins.exists(): return None
    root=plugins/'active' if (plugins/'active').exists() and any((plugins/'active').glob('*.py')) else plugins
    rows=[]
    for p in sorted(root.glob('*.py')):
        if p.name.startswith('_') or 'template' in p.name.lower(): continue
        try: rows.append({'relative_path':p.resolve().relative_to(base_dir).as_posix(),'sha256':_h(p),'size':p.stat().st_size})
        except Exception: pass
    return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest() if rows else None
