#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / 'shared' / 'contracts' / 'verticals' / 'data-model.contract.json'
SCHEMA = ROOT / 'shared' / 'contracts' / 'verticals' / 'vertical-data-extension.schema.json'
CORE = ROOT / 'shared' / 'verticals' / 'data-models' / 'core-data-model.v0.json'
EXT_DIR = ROOT / 'shared' / 'verticals' / 'data-models' / 'extensions'
OWNERSHIP = ROOT / 'shared' / 'verticals' / 'data-models' / 'entity-ownership.v0.json'
MIGRATIONS = ROOT / 'shared' / 'verticals' / 'data-models' / 'migration-boundaries.v0.json'
EXPECTED = {'convenience','restaurant','pharmacy','beauty','hardware','apparel','repair','field_route','grocery_scale','food_truck'}
REQUIRED_EXTENSION_FIELDS = {'extensionId','entityName','extensionType','ownerSurface','storagePolicy','tabletAccess','pcAuthority','syncPolicy','auditImpact','offlineImpact','coreRelations','requiredEvents','fixtures','acceptanceCriteria'}
FORBIDDEN_CORE_HINTS = {'tableNumber','appointmentTime','prescriptionId','repairOrderId','routeStopId','scaleWeight','kitchenStation','colorSizeGrid','sizeColorMatrix'}

def load(path: Path):
    if not path.exists():
        raise SystemExit(f'missing {path}')
    return json.loads(path.read_text(encoding='utf-8'))

def main() -> int:
    contract = load(CONTRACT)
    load(SCHEMA)
    core = load(CORE)
    load(OWNERSHIP)
    load(MIGRATIONS)
    core_forbidden = set(core.get('forbiddenUniversalFields', []))
    if not FORBIDDEN_CORE_HINTS.intersection(core_forbidden):
        raise SystemExit('core forbidden fields look incomplete')
    if len(contract.get('coreEntities', [])) < 10:
        raise SystemExit('core entity contract too small')
    files = sorted(EXT_DIR.glob('*.data-extension.json'))
    found = {p.name.replace('.data-extension.json','') for p in files}
    missing = EXPECTED - found
    extra = found - EXPECTED
    if missing:
        raise SystemExit('missing vertical data extensions: ' + ', '.join(sorted(missing)))
    if extra:
        raise SystemExit('unexpected vertical data extensions: ' + ', '.join(sorted(extra)))
    total_extensions = 0
    for path in files:
        data = load(path)
        vertical = data.get('verticalId')
        if vertical not in EXPECTED:
            raise SystemExit(f'invalid verticalId in {path}: {vertical}')
        exts = data.get('extensions') or []
        if not exts:
            raise SystemExit(f'no extensions in {path}')
        for ext in exts:
            missing_fields = REQUIRED_EXTENSION_FIELDS - set(ext)
            if missing_fields:
                raise SystemExit(f'{path} extension missing fields: {sorted(missing_fields)}')
            if '.' not in ext['extensionId']:
                raise SystemExit(f'extensionId lacks namespace: {ext["extensionId"]}')
            if not ext['requiredEvents']:
                raise SystemExit(f'extension lacks events: {ext["extensionId"]}')
            if not ext['fixtures']:
                raise SystemExit(f'extension lacks fixtures: {ext["extensionId"]}')
            forbidden = set(ext.get('forbiddenCoreFields', []))
            if not forbidden:
                raise SystemExit(f'extension lacks forbiddenCoreFields: {ext["extensionId"]}')
            total_extensions += 1
    if total_extensions < 30:
        raise SystemExit('too few vertical extensions')
    print(f'OK vertical data models: {len(files)} verticals, {total_extensions} extensions validated')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
