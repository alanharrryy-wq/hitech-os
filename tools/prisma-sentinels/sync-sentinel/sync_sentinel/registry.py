from __future__ import annotations

from pathlib import Path

SENTINEL_REL = Path("tools/prisma-sentinels/sync-sentinel")
APP_REL = Path("apps/terminal-de-venta-system")

CANONICAL_AUTHORITY_PATHS = [
    Path("PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_AGENT_GATE.md"),
    Path("PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json"),
    Path("PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_DO_NOT_REBUILD_MAP.json"),
    Path("PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_REGISTRATION_INDEX.json"),
    Path("PRISMA Factory Ledger/PRISMA_EVIDENCE_INDEX.json"),
    APP_REL / "docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md",
    APP_REL / "docs/sync/PC_TABLET_SYNC_CURRENT_AUTHORITY.md",
    APP_REL / "products/mobile/app/docs/prisma-app/PRISMA_MOBILE_INTERFACE_CANON.md",
    APP_REL / "products/mobile/app/docs/prisma-app/PRISMA_MOBILE_INTERFACE_CANON.contract.json",
]

SYNC_SOURCE_PATHS = [
    APP_REL / "products/tablet/app/src/server/sync/dispatcher.ts",
    APP_REL / "products/tablet/app/src/server/sync/pc-origin.ts",
    APP_REL / "products/tablet/app/src/server/sync/catalog-pull.ts",
    APP_REL / "products/tablet/app/src/server/pos-outbox/index.ts",
    APP_REL / "products/tablet/app/src/server/pos-reports/index.ts",
    APP_REL / "products/pc/app/src/server/services/sync-ingest.service.ts",
    APP_REL / "products/pc/app/src/server/services/sync-projectors.service.ts",
    APP_REL / "products/pc/app/src/server/services/catalog-delta-export.service.ts",
    APP_REL / "products/pc/app/src/server/services/pc-command-center.service.ts",
    APP_REL / "products/mobile/app/src/lib/prisma-app/mobile-data-plane/state-loader.ts",
    APP_REL / "products/mobile/app/src/lib/prisma-app/mobile-data-plane/endpoints.ts",
    APP_REL / "products/mobile/app/src/lib/prisma-app/mobile-security/context.ts",
    APP_REL / "products/mobile/app/src/lib/prisma-app/mobile-security/route-guard.ts",
    APP_REL / "products/mobile/app/src/lib/prisma-app/mobile-security/projection-route.ts",
    APP_REL / "products/mobile/app/src/lib/prisma-app/mobile-security/projection-envelope.ts",
    APP_REL / "products/mobile/app/app/api/mobile/v1/read-models/sync-source-health/route.ts",
    APP_REL / "shared/twin-kernel/src/sync/catalog-delta.ts",
    APP_REL / "shared/contracts/pc-tablet-catalog-delta.v1.json",
]

STATIC_PROBES = [
    {
        "id": "pc_to_tablet_catalog_delta_closure",
        "cwd": APP_REL,
        "cmd": ["node", "tools/verify_pc_to_tablet_catalog_delta_closure_01.mjs"],
        "pass_token": "PC_TO_TABLET_CATALOG_DELTA_CLOSURE passed",
    },
    {
        "id": "tablet_sync_dispatcher_contract",
        "cwd": APP_REL / "products/tablet/app",
        "cmd": ["node", "tools/verify_tablet_sync_dispatcher_01.mjs"],
        "pass_token": "PRISMA_TABLET_SYNC_DISPATCHER_01 passed",
    },
    {
        "id": "pc_sync_ingest_persistence_contract",
        "cwd": APP_REL / "products/pc/app",
        "cmd": ["node", "tools/verify_sync_ingest_persistence_01.mjs"],
        "pass_token": "PRISMA_SYNC_INGEST_PERSISTENCE_01 passed",
    },
    {
        "id": "mobile_secure_projection_gateway_contract",
        "cwd": APP_REL / "products/mobile/app",
        "cmd": ["node", "tools/verify_prisma_mobile_secure_projection_gateway_42.mjs"],
        "pass_token": "PRISMA Mobile Secure Projection Gateway 42: PASS",
    },
]

KNOWN_LIVE_DB_CANDIDATES = [
    APP_REL / "products/tablet/app/data/tablet-pos.db",
    APP_REL / "products/tablet/data/tablet-pos.db",
    APP_REL / "products/pc/app/data/canonical.db",
    Path("tools/_local/data/terminal-de-venta-system/canonical.db"),
]

FORBIDDEN_MUTATION_PREFIXES = [
    APP_REL / "products/tablet/app/app",
    APP_REL / "products/tablet/app/components",
    APP_REL / "products/pc/app/app",
    APP_REL / "products/pc/app/components",
    APP_REL / "products/mobile",
    APP_REL / "shared-ui",
]
