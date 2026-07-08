# -*- coding: utf-8 -*-
from __future__ import annotations
import json, tempfile
from pathlib import Path
try:
    from .target_readiness import append_target_readiness, CONTROL_FAMILIES
except Exception:
    from target_readiness import append_target_readiness, CONTROL_FAMILIES  # type: ignore

def main():
    with tempfile.TemporaryDirectory() as td:
        atlas=Path(td)
        append_target_readiness(atlas, Path(td), [], [{'surfaceId':'tablet'}], [], [{'surface':'tablet','componentFile':'products/tablet/app/app/tablet-lab/components/ProductCard.tsx','componentId':'ProductCard'}], [{'surface':'tablet','selector':'.addButton:hover','definedIn':'products/tablet/app/app/tablet-lab/ProductCard.module.css','states':':hover'}], [], [])
        req=['29_PRESET_TARGET_ELIGIBILITY_MATRIX.json','30_CONTROL_APPLICABILITY_MATRIX_PLUS.json','31_TARGET_STATE_CONTROL_JOIN.json','32_PRESET_TARGET_SUMMARY.json','33_RUNTIME_PROBE_DEFERRED_MAMASTROPHIC.md']
        missing=[x for x in req if not (atlas/x).exists()]
        if missing: raise SystemExit('missing outputs '+','.join(missing))
        if len(CONTROL_FAMILIES) < 30: raise SystemExit('control matrix too small')
        rows=json.loads((atlas/'29_PRESET_TARGET_ELIGIBILITY_MATRIX.json').read_text(encoding='utf-8'))
        if not any(r.get('eligible') and r.get('kind')=='button' and r.get('state')=='hover' for r in rows): raise SystemExit('missing eligible button hover target')
        print('PASS_APP_MAP_TARGET_READINESS_VERIFIER')
if __name__=='__main__': main()
