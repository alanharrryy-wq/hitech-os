from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any

from ..shared.status_payloads import utc_now_iso

def capture_failure(output_dir: str | Path, exc: BaseException, context: dict[str, Any] | None = None) -> Path:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = {
        "captured_at": utc_now_iso(),
        "error_type": type(exc).__name__,
        "message": str(exc),
        "context": context or {},
        "traceback": traceback.format_exception(type(exc), exc, exc.__traceback__),
    }
    target = root / f"failure_snapshot_{type(exc).__name__}.json"
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target
