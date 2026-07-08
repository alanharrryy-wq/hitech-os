from __future__ import annotations
import json, tempfile, zipfile
from pathlib import Path
from .runner import run_app_map

def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)/'repo'
        (root/'apps/terminal-de-venta-system/products/tablet/app/app/tablet-lab').mkdir(parents=True)
        (root/'apps/terminal-de-venta-system/products/tablet/app/app/tablet-lab/page.tsx').write_text("export default function Page(){return <button className='labButton'>Ok</button>}", encoding='utf-8')
        (root/'apps/terminal-de-venta-system/products/tablet/app/app/tablet-lab/style.module.css').write_text(":root{--tabctl7-button-glow: 0 0 10px cyan}.labButton:hover{box-shadow:var(--tabctl7-button-glow)}", encoding='utf-8')
        out=Path(td)/'out'
        z=Path(run_app_map(str(root), target_app='tablet', output_root=str(out)))
        assert z.exists() and z.stat().st_size > 0
        with zipfile.ZipFile(z) as zipf:
            names=set(zipf.namelist())
            assert 'app_map_atlas/01_SURFACE_REGISTRY.json' in names
            data=json.loads(zipf.read('app_map_atlas/APP_MAP_SUMMARY.json'))
            assert data['ok'] is True
    print('PASS_APP_MAP_VERIFY')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
