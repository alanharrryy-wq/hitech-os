from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "shared/licensing/license-types.ts",
    "shared/licensing/license-loader.ts",
    "shared/licensing/feature-resolver.ts",
    "shared/licensing/license-gate.ts",
    "products/tablet/app/app/api/license/status/route.ts",
    "products/tablet/app/app/api/license/features/route.ts",
    "products/tablet/app/app/settings/license/page.tsx",
    "products/pc/app/app/api/license/status/route.ts",
    "products/pc/app/app/api/license/features/route.ts",
    "products/pc/app/app/settings/license/page.tsx",
    "local-runtime/license/license.dev.json",
]

MARKERS = {
    "shared/licensing/feature-resolver.ts": ["resolveFeature", "Venta básica permitida"],
    "shared/licensing/plan-catalog.ts": ["TABLET_SOLO", "TABLET_PRO", "TABLET_PC_REQUIRED"],
    "shared/licensing/license-loader.ts": ["loadLocalLicense", "validateLicenseDocument"],
}


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        print("MISSING FILES")
        for item in missing:
            print(f" - {item}")
        return 2

    for rel, needles in MARKERS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                print(f"MISSING MARKER {needle!r} in {rel}")
                return 3

    license_path = ROOT / "local-runtime/license/license.dev.json"
    license_doc = json.loads(license_path.read_text(encoding="utf-8"))
    assert license_doc["plan"] in {"TABLET_SOLO", "TABLET_PRO", "TABLET_PC_REQUIRED", "DEVELOPMENT"}
    assert license_doc["state"] in {"active", "suspended", "revoked", "development"}
    print("OK PRISMA_LICENSE_LOCAL_ENFORCEMENT_02AB structural verify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
