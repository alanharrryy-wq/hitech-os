from __future__ import annotations

import datetime as _dt
import time
from typing import Any
from urllib.parse import urlparse

API_VERSION = "PRISMA_LIFECYCLE_FAST_HEALTH_V2"
_LOADED_AT = time.time()

def lifecycle_fast_health_payload(path: str = '/api/lifecycle/health', public: bool = False) -> dict[str, Any]:
    parsed = urlparse(path or '/api/lifecycle/health')
    return {
        'ok': True,
        'status': 'LIFECYCLE_READY',
        'apiVersion': API_VERSION,
        'mode': 'fast_health',
        'readOnly': True,
        'public': bool(public),
        'bounded': True,
        'heavyWorkSkipped': True,
        'generatedAt': _dt.datetime.now(_dt.timezone.utc).isoformat(),
        'uptimeMs': int((time.time() - _LOADED_AT) * 1000),
        'path': parsed.path,
        'checks': [
            {'name': 'handler', 'status': 'PASS'},
            {'name': 'no_db_scan', 'status': 'PASS'},
            {'name': 'no_subprocess', 'status': 'PASS'},
            {'name': 'no_network', 'status': 'PASS'},
            {'name': 'no_dry_run', 'status': 'PASS'},
            {'name': 'mutation_allowed', 'status': 'PUBLIC_READ_ONLY' if public else 'LOCAL_READ_ONLY'},
        ],
        'message': 'Lifecycle health is fast and bounded; heavy lifecycle work remains on explicit action routes.',
    }
