from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(r"F:\repos\hitech-os\apps\terminal-de-venta-system")
SHARE_ROOT = Path(r"F:\terminal_de_venta_chatgpt_share")
REPO_ROOT = SHARE_ROOT / "repo"
REPO_SHARE_ROOT = REPO_ROOT / "apps" / "terminal-de-venta-system"
STATUS_PATH = SHARE_ROOT / "SYNC_STATUS.json"
SHARE_MANIFEST_PATH = SHARE_ROOT / "SHARE_MANIFEST.json"
LAST_SYNC_PATH = SHARE_ROOT / "LAST_SYNC.txt"
TOP_README_PATH = SHARE_ROOT / "README.md"
REPO_README_PATH = REPO_ROOT / "README.md"

CRITICAL_FILES = [
    "README.md",
    "terminal_de_venta.cmd",
    "tooling/scripts/sync_chatgpt_share.py",
    "tools/verify_chatgpt_share_sync_coverage.py",
    "docs/architecture/PRISMA_ARQUITECTURA_FINAL_PC_TABLET.md",
    "docs/mobile/PRISMA_APP_MOBILE_03_PRODUCT_ROOT_REBASE.md",
    "shared/contracts/sync-event-contract.v1.json",
    "shared/contracts/security-audit-permissions.v1.json",
    "tools/verify_sync_contract_gate_01.mjs",
    "tools/verify_security_audit_permissions_01.mjs",
    "products/mobile/app/README.md",
    "products/mobile/app/docs/PWA_READINESS.md",
    "products/mobile/app/docs/PLAY_STORE_READINESS.md",
    "products/mobile/app/docs/TWA_ANDROID_READINESS.md",
    "products/mobile/app/tools/verify_prisma_mobile_pwa_readiness.mjs",
    "products/mobile/app/tools/verify_prisma_mobile_playstore_readiness.mjs",
    "products/tablet/app/tools/verify_tablet_standalone_core_closeout_02.mjs",
    "products/tablet/app/tools/verify_tablet_touch_pos_ui_03.mjs",
    "products/pc/app/tools/verify_sync_ingest_persistence_01.mjs",
    "products/pc/app/tools/verify_pc_backoffice_core_01.mjs",
    "products/pc/app/tools/verify_pc_kpi_dashboard_02.mjs",
    "products/tablet/app/app/api/pos/sales/complete/route.ts",
    "products/pc/app/app/api/backoffice/sync/ingest/route.ts",
    "products/pc/app/src/lib/backoffice/sync-ingest-store.ts",
]

LEGACY_REPO_DIRS = [
    "docs",
    "packages",
    "prisma",
    "products",
    "shared",
    "tools",
    "tooling",
]

LEGACY_REPO_FILES = [
    "REPO_STRUCTURE_GOVERNANCE.md",
    "STRUCTURAL_CLEANUP_REPORT.md",
    "terminal_de_venta.cmd",
]


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> int:
    missing = []
    for rel in CRITICAL_FILES:
        if not (REPO_SHARE_ROOT / rel).exists():
            missing.append(rel)

    stale_legacy = []
    for rel in LEGACY_REPO_DIRS:
        target = REPO_ROOT / rel
        if target.exists():
            stale_legacy.append(str(target))
    for rel in LEGACY_REPO_FILES:
        target = REPO_ROOT / rel
        if target.exists():
            stale_legacy.append(str(target))

    missing_control = []
    for path in [STATUS_PATH, SHARE_MANIFEST_PATH, LAST_SYNC_PATH, TOP_README_PATH, REPO_README_PATH]:
        if not path.exists():
            missing_control.append(str(path))

    status = load_json(STATUS_PATH)
    manifest = load_json(SHARE_MANIFEST_PATH)

    manifest_root = manifest.get("canonical_zip_root")
    status_root = status.get("canonical_zip_root")
    root_ok = manifest_root == "repo/apps/terminal-de-venta-system" and status_root == "repo/apps/terminal-de-venta-system"

    if missing or stale_legacy or missing_control or not root_ok:
        print("FAIL verify_chatgpt_share_sync_coverage")
        for rel in missing:
            print("missing:", rel)
        for rel in stale_legacy:
            print("stale_legacy:", rel)
        for rel in missing_control:
            print("missing_control:", rel)
        if not root_ok:
            print("bad_canonical_root: status=", status_root, "manifest=", manifest_root)
        return 1

    print("OK verify_chatgpt_share_sync_coverage")
    print(f"share_root={SHARE_ROOT}")
    print("canonical_zip_root=repo/apps/terminal-de-venta-system")
    print(f"critical_files={len(CRITICAL_FILES)}")
    print(f"source_file_count={status.get('source_file_count')}")
    print(f"mirrored_file_count={status.get('mirrored_file_count')}")
    print(f"docs_count={manifest.get('docs_count')}")
    print(f"mobile_docs_count={manifest.get('mobile_docs_count')}")
    print(f"last_successful_sync_at={status.get('last_successful_sync_at')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
