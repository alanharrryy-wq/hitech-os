from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .support_finalizer import ALLOWED_ACTION, ALLOWED_STATUS, VERSION


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(atlas_output: str | Path) -> dict[str, Any]:
    root = Path(atlas_output).expanduser().resolve()
    path = root / "SUPPORT_FINALIZATION.json"
    if not path.exists():
        return {"status": "FAIL_SUPPORT_FINALIZATION_VERIFY", "missingFiles": [path.name]}
    value = _load(path)
    checks = {
        "schemaVersion": value.get("schemaVersion") == "code_atlas_support_finalizer.v2",
        "finalizerVersion": value.get("generator", {}).get("version") == VERSION,
        "statusAllowed": value.get("status") in ALLOWED_STATUS,
        "decisionAllowed": value.get("decision") in ALLOWED_ACTION,
        "repositoryReadOnly": value.get("readOnlyRepository") is True,
        "productionNotFalselyCertified": value.get("productionCertified") is False,
        "nonClaimsPresent": bool(value.get("doesNotProve")),
    }
    ok = all(checks.values())
    return {
        "status": "PASS_SUPPORT_FINALIZATION_VERIFY" if ok else "FAIL_SUPPORT_FINALIZATION_VERIFY",
        "checks": checks,
        "productionCertified": value.get("productionCertified"),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atlas-output", required=True)
    args = parser.parse_args(argv)
    result = verify(args.atlas_output)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
