#!/usr/bin/env python3
"""Static gate for PRISMA Identity Dictionary."""
from __future__ import annotations
import json
from identity_dictionary_core import IDENTITY, load_model, validate_model


def main() -> int:
    problems, warnings = validate_model(check_compiled=True)
    model = load_model() if not any(item.startswith("missing required") for item in problems) else None
    payload = {
        "status": "PASS" if not problems else "FAIL",
        "authority": IDENTITY.as_posix(),
        "selectedProfileId": model["activation"]["selectedProfileId"] if model else None,
        "profileCount": len(model["profiles"]) if model else 0,
        "adapterCount": len(model["adapters"]) if model else 0,
        "bindingReadySurfaces": [s for s,b in model["bindings"].items() if b["readiness"] == "CERTIFIED_BINDING_SOURCE"] if model else [],
        "blockedSurfaces": [s for s,b in model["bindings"].items() if b["readiness"] == "BLOCKED_BY_MISSING_VISUAL_CONTROL_BINDINGS"] if model else [],
        "runtimeProjectionAllowed": False,
        "warnings": warnings,
        "problems": problems,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not problems else 1

if __name__ == "__main__":
    raise SystemExit(main())
