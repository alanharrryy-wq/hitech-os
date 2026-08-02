from __future__ import annotations
from typing import Any
from .errors import ApplicationDisabledError

APPLICATION_STATUS = {
    "schema": "prisma.ui.bridge.application-status.v1",
    "applicationEnabled": False,
    "runtimeMutationAllowed": False,
    "productApplicationAllowed": False,
    "status": "APPLICATION_DISABLED_SOURCE_ONLY_V1",
    "requiredFutureGates": [
        "FRESH_EXACT_TARGET_AUTHORITY_MESH",
        "LAYER_MAP_PRESENT",
        "SCOPE_GUARD_PASS",
        "READ_ONLY_PLAN_AND_DIFF_REVIEWED",
        "EXPLICIT_APPLICATION_AUTHORIZATION",
        "VERIFIABLE_BACKUP",
        "POST_APPLICATION_EVIDENCE",
        "ROLLBACK_READY",
    ],
}

def apply_plan(*_: Any, **__: Any) -> None:
    raise ApplicationDisabledError("Application is intentionally disabled in PRISMA UI Bridge source-only v1")
