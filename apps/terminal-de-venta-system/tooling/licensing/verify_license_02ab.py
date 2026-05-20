from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "shared/licensing/license-types.ts",
    "shared/licensing/license-loader.ts",
    "shared/licensing/feature-resolver.ts",
    "shared/licensing/license-gate.ts",
    "shared/licensing/license-governor.ts",
    "products/tablet/app/app/api/license/status/route.ts",
    "products/tablet/app/app/api/license/features/route.ts",
    "products/tablet/app/app/settings/license/page.tsx",
    "products/pc/app/app/api/license/status/route.ts",
    "products/pc/app/app/api/license/features/route.ts",
    "products/pc/app/app/settings/license/page.tsx",
    "tooling/licensing/fixtures/tablet-solo.active.signed.license.json",
]

MARKERS = {
    "shared/licensing/feature-resolver.ts": ["resolveFeature", "Venta básica permitida", "Licencia inválida o alterada"],
    "shared/licensing/plan-catalog.ts": ["TABLET_SOLO", "TABLET_PRO", "TABLET_PC_MANAGED"],
    "shared/licensing/license-types.ts": ["LicenseAssignmentState", "operationalDecision", "lastDecisionAt"],
    "shared/licensing/license-governor.ts": ["getLicenseGovernorSnapshot", "refreshState", "canUseLocalPos"],
    "shared/licensing/license-refresh-state.ts": ["refresh_disabled", "operationalDecision"],
    "shared/licensing/license-refresh-client.ts": ["Refresh remoto no configurado", "La operación local continúa si la licencia local es válida"],
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

    license_path = ROOT / "tooling/licensing/fixtures/tablet-solo.active.signed.license.json"
    license_doc = json.loads(license_path.read_text(encoding="utf-8"))["payload"]
    assert license_doc["plan"] in {"TABLET_SOLO", "TABLET_PRO", "TABLET_PC_MANAGED", "DEVELOPMENT"}
    assert license_doc["state"] in {"active", "suspended", "revoked", "development"}
    assert "customerId" in license_doc and "businessId" in license_doc and "licenseId" in license_doc
    print("OK PRISMA_LICENSE_LOCAL_ENFORCEMENT_02AB structural verify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
