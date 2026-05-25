from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_FILES = [
    "products/pc/app/app/layout.tsx",
    "products/pc/app/app/prisma-atmospheric-background.css",
    "products/pc/app/app/components/PrismaAtmosphericBackground.tsx",
    "products/pc/app/app/dashboard/page.tsx",
    "products/pc/app/app/dashboard/hoy-premium.module.css",
    "products/pc/app/public/backgrounds/prisma/01_prisma_base_graphite_cloudglass.png",
    "products/pc/app/public/backgrounds/prisma/02_prisma_fractures_light_overlay_alpha.png",
    "products/pc/app/public/backgrounds/prisma/03_prisma_mist_dust_overlay_alpha.png",
]

EXPECTATIONS = {
    "products/pc/app/app/layout.tsx": [
        'import "./prisma-atmospheric-background.css";',
        'import { PrismaAtmosphericBackground } from "./components/PrismaAtmosphericBackground";',
        "<PrismaAtmosphericBackground />",
        'className="prisma-app-content"',
    ],
    "products/pc/app/app/prisma-atmospheric-background.css": [
        ".prisma-atmosphere",
        ".prisma-bg-base",
        ".prisma-bg-fractures",
        ".prisma-bg-mist",
        ".prisma-bg-scrim",
        "pointer-events: none",
        "prefers-reduced-motion: reduce",
        "/backgrounds/prisma/01_prisma_base_graphite_cloudglass.png",
        "/backgrounds/prisma/02_prisma_fractures_light_overlay_alpha.png",
        "/backgrounds/prisma/03_prisma_mist_dust_overlay_alpha.png",
    ],
    "products/pc/app/app/components/PrismaAtmosphericBackground.tsx": [
        "use client",
        "PrismaAtmosphericBackground",
        "prisma-bg-layer prisma-bg-base",
        "prisma-bg-layer prisma-bg-fractures",
        "prisma-bg-layer prisma-bg-mist",
        "prisma-bg-layer prisma-bg-scrim",
        "prefers-reduced-motion: reduce",
    ],
    "products/pc/app/app/dashboard/page.tsx": [
        'data-prisma-visual="cloudglass-layer-pack-01"',
        'data-prisma-background="fractured-graphite-cloudglass"',
    ],
    "products/pc/app/app/dashboard/hoy-premium.module.css": [
        "--hoy-glass",
        ".heroShell::after",
        "backdrop-filter: blur(24px)",
        "prefers-reduced-transparency: reduce",
        "fractured",
    ],
}

MIN_ASSET_BYTES = {
    "products/pc/app/public/backgrounds/prisma/01_prisma_base_graphite_cloudglass.png": 1_000_000,
    "products/pc/app/public/backgrounds/prisma/02_prisma_fractures_light_overlay_alpha.png": 500_000,
    "products/pc/app/public/backgrounds/prisma/03_prisma_mist_dust_overlay_alpha.png": 500_000,
}


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    failures: list[str] = []
    checks: list[dict[str, object]] = []

    for rel in REQUIRED_FILES:
        path = root / rel
        exists = path.exists()
        checks.append({"file": rel, "exists": exists, "size": path.stat().st_size if exists else 0})
        if not exists:
            failures.append(f"Missing required file: {rel}")

    for rel, min_size in MIN_ASSET_BYTES.items():
        path = root / rel
        if path.exists() and path.stat().st_size < min_size:
            failures.append(f"Asset too small, likely not copied correctly: {rel} ({path.stat().st_size} bytes)")

    for rel, needles in EXPECTATIONS.items():
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for needle in needles:
            if needle not in text:
                failures.append(f"Expected token not found in {rel}: {needle}")

    report = {
        "verifier": "verify_pc_cloudglass_dashboard_01",
        "root": str(root),
        "passed": not failures,
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
