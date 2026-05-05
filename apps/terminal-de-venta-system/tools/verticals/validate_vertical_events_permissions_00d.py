#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

VERTICALS = ['convenience','restaurant','pharmacy','beauty','hardware','apparel','repair','field_route','grocery_scale','food_truck']
TOPIC_RE = re.compile(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$')
PERM_RE = TOPIC_RE

REQUIRED = [
    'shared/contracts/verticals/events/event-envelope.schema.json',
    'shared/contracts/verticals/events/vertical-event-policy.schema.json',
    'shared/contracts/verticals/permissions/permission-policy.schema.json',
    'shared/verticals/events/common-event-catalog.v0.json',
    'shared/verticals/permissions/common-permission-catalog.v0.json',
    'shared/verticals/audit/vertical-audit-rules.v0.json',
    'shared/verticals/sync/vertical-sync-policy.v0.json',
]

FORBIDDEN_VISIBLE = {'payload', 'endpoint', 'outbox', 'ack', 'retry worker', 'conflict resolver'}

def load(path: Path):
    with path.open('r', encoding='utf-8') as fh:
        return json.load(fh)

def fail(msg: str) -> None:
    print('ERROR:', msg)
    sys.exit(1)

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    for rel in REQUIRED:
        if not (root / rel).exists():
            fail(f'falta archivo requerido: {rel}')

    event_total = 0
    perm_total = 0
    sensitive_total = 0
    for vid in VERTICALS:
        ep = root / 'shared' / 'verticals' / 'events' / 'policies' / f'{vid}.event-policy.json'
        pp = root / 'shared' / 'verticals' / 'permissions' / 'policies' / f'{vid}.permission-policy.json'
        if not ep.exists():
            fail(f'falta event policy para {vid}')
        if not pp.exists():
            fail(f'falta permission policy para {vid}')
        edata = load(ep)
        pdata = load(pp)
        if edata.get('verticalId') != vid:
            fail(f'verticalId invalido en {ep}')
        if pdata.get('verticalId') != vid:
            fail(f'verticalId invalido en {pp}')
        events = edata.get('events') or []
        if len(events) < 10:
            fail(f'muy pocos eventos para {vid}')
        for event in events:
            topic = event.get('topic')
            if not topic or not TOPIC_RE.match(topic):
                fail(f'topic invalido {topic!r} en {vid}')
            if not event.get('source'):
                fail(f'evento sin source {topic} en {vid}')
            if event.get('sensitivity') not in {'low','medium','high'}:
                fail(f'sensitivity invalida en {topic}')
            copy = str(event.get('visibleMicrocopy','')).lower()
            for term in FORBIDDEN_VISIBLE:
                if term in copy:
                    fail(f'microcopy tecnica prohibida en {topic}: {term}')
        perms = pdata.get('permissions') or []
        if len(perms) < 10:
            fail(f'muy pocos permisos para {vid}')
        for perm in perms:
            if not PERM_RE.match(perm):
                fail(f'permiso invalido {perm!r} en {vid}')
        role_matrix = pdata.get('roleMatrix') or {}
        for role in ['cashier','supervisor','manager','owner','backoffice_admin']:
            if role not in role_matrix:
                fail(f'falta rol {role} en {vid}')
        sensitive = pdata.get('sensitivePermissions') or []
        if not sensitive:
            fail(f'falta sensitivePermissions en {vid}')
        if pdata.get('tabletPolicy', {}).get('canGrantPermissions') is not False:
            fail(f'Tablet no debe otorgar permisos en {vid}')
        event_total += len(events)
        perm_total += len(perms)
        sensitive_total += len(sensitive)

    print(f'OK vertical events permissions: {len(VERTICALS)} verticals, {event_total} events, {perm_total} permissions, {sensitive_total} sensitive permissions validated')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
