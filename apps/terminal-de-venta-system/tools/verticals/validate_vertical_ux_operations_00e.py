#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

REQUIRED_STATES = {'empty','loading','error','success','disabled','offline','pending_sync'}
FORBIDDEN = {'checkout','cart','sync','outbox','runtime','lookup','guardrails','SaleReturn','amountCents','restock','payload','API','endpoint','worker','ack','schema','queue'}


def fail(msg: str) -> None:
    raise SystemExit(msg)


def load(path: Path):
    if not path.exists():
        fail(f'Falta archivo: {path}')
    return json.loads(path.read_text(encoding='utf-8'))


def scan_visible(value) -> list[str]:
    hits = []
    if isinstance(value, dict):
        for k, v in value.items():
            if k in {'forbiddenVisibleTerms'}:
                continue
            hits.extend(scan_visible(v))
    elif isinstance(value, list):
        for item in value:
            hits.extend(scan_visible(item))
    elif isinstance(value, str):
        for term in FORBIDDEN:
            if term.lower() in value.lower():
                hits.append(term)
    return hits


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    registry = load(root / 'shared/verticals/ux/vertical-ux-operation.registry.v0.json')
    profiles = registry.get('profiles', [])
    if len(profiles) != 10:
        fail(f'Se esperaban 10 perfiles UX, llegaron {len(profiles)}')
    total_screens = 0
    total_flows = 0
    for entry in profiles:
        rel = entry.get('path')
        profile = load(root / rel)
        vid = profile.get('verticalId')
        if vid != entry.get('verticalId'):
            fail(f'verticalId inconsistente en {rel}')
        tablet = profile.get('tablet', {})
        pc = profile.get('pc', {})
        if not tablet.get('primaryEntry'):
            fail(f'{vid}: falta primaryEntry Tablet')
        if not tablet.get('navigation') or len(tablet['navigation']) < 5:
            fail(f'{vid}: navegación Tablet insuficiente')
        if not pc.get('navigation') or len(pc['navigation']) < 5:
            fail(f'{vid}: navegación PC insuficiente')
        if not tablet.get('blockedModules'):
            fail(f'{vid}: faltan bloqueos Tablet')
        screens = profile.get('screens', [])
        flows = profile.get('flows', [])
        if len(screens) < 5:
            fail(f'{vid}: pantallas insuficientes')
        if len(flows) < 4:
            fail(f'{vid}: flujos insuficientes')
        total_screens += len(screens)
        total_flows += len(flows)
        for screen in screens:
            states = set((screen.get('states') or {}).keys())
            missing = REQUIRED_STATES - states
            if missing:
                fail(f'{vid}/{screen.get("label")}: faltan estados {sorted(missing)}')
        hits = scan_visible({
            'tablet': profile.get('tablet'),
            'pc': profile.get('pc'),
            'screens': profile.get('screens'),
            'flows': profile.get('flows'),
            'microcopy': profile.get('microcopy'),
            'acceptance': profile.get('acceptance')
        })
        if hits:
            fail(f'{vid}: términos técnicos visibles detectados: {sorted(set(hits))}')
    trace = load(root / 'shared/verticals/ux/vertical-ux-operation.trace-matrix.v0.json')
    if len(trace.get('rows', [])) < 400:
        fail('Trace matrix UX demasiado chica')
    print(f'OK vertical UX operations: {len(profiles)} verticals, {total_screens} screens, {total_flows} flows, {len(trace.get("rows", []))} trace rows validated')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
