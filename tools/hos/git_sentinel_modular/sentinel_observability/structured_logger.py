from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..shared.status_payloads import utc_now_iso

def log_event(log_target: str | Path, event: str, **fields: Any) -> dict[str, Any]:
    path = Path(log_target)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"event": event, "timestamp": utc_now_iso(), **fields}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
    return payload
