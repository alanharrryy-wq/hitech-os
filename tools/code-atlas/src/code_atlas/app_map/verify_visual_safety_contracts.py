# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, json, tempfile, zipfile
from pathlib import Path
try:
    from .runner import run_app_map
except Exception:
    from runner import run_app_map  # type: ignore

def main(argv=None) -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--json-out', default=None); args=ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)/'repo'; app=root/'apps/terminal-de-venta-system/products/tablet/app/app/tablet-lab/components'; app.mkdir(parents=True)
        (app/'Card.tsx').write_text("export function Card(){return <div className='outerShell' ref={cardRef}><div className='glassShell'><div className='spacingOnly'><button className='addButton' onClick={go}>Add</button></div></div></div>}", encoding='utf-8')
        (app/'Card.module.css').write_text('.outerShell{position:relative;z-index:2;overflow:hidden}.glassShell{backdrop-filter:blur(var(--tabctl7-glass-blur));box-shadow:var(--tabctl3-button-glow)}.spacingOnly{padding:12px;gap:8px}.addButton:hover{box-shadow:var(--tabctl7-button-glow)}:root{--tabctl3-button-glow:0 0 12px cyan;--tabctl7-button-glow:var(--tabctl3-button-glow);--tabctl7-glass-blur:12px}', encoding='utf-8')
        out=Path(td)/'out'; zpath=Path(run_app_map(str(root), target_app='tablet', output_root=str(out)))
        assert zpath.exists()
        with zipfile.ZipFile(zpath) as z:
            names=set(z.namelist())
            required=['app_map_atlas/21_CONTAINER_PURPOSE_MAP.json','app_map_atlas/22_WRAPPER_COLLAPSE_PLAN.json','app_map_atlas/23_VISUAL_DIFF_PROBE.json','app_map_atlas/24_ZERO_MEANS_ZERO_REAL_GATE.json','app_map_atlas/25_LEGACY_COMPAT_BRIDGE.json','app_map_atlas/26_DO_NOT_TOUCH_MAP.json','app_map_atlas/27_VISUAL_SAFETY_SUMMARY.json']
            for name in required: assert name in names, name
            summary=json.loads(z.read('app_map_atlas/27_VISUAL_SAFETY_SUMMARY.json'))
            assert summary['containerPurposeRows'] > 0
            assert summary['zeroMeansZeroRows'] > 0
            assert summary['legacyCompatRows'] > 0
    result={'ok':True,'status':'PASS_APP_MAP_VISUAL_SAFETY_VERIFY'}
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True); Path(args.json_out).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print('PASS_APP_MAP_VISUAL_SAFETY_VERIFY')
    return 0
if __name__ == '__main__': raise SystemExit(main())
