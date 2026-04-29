from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(r"F:\repos\hitech-os\apps\terminal-de-venta-system")
SHARE_ROOT = Path(r"F:\terminal_de_venta_chatgpt_share")
REPO_SHARE_ROOT = SHARE_ROOT / "repo" / "apps" / "terminal-de-venta-system"
STATUS_PATH = SHARE_ROOT / "SYNC_STATUS.json"

CRITICAL_FILES = [
    "shared/contracts/sync-event-contract.v1.json",
    "shared/contracts/security-audit-permissions.v1.json",
    "tools/verify_sync_contract_gate_01.mjs",
    "tools/verify_security_audit_permissions_01.mjs",
    "products/tablet/app/tools/verify_tablet_standalone_core_closeout_02.mjs",
    "products/tablet/app/tools/verify_tablet_touch_pos_ui_03.mjs",
    "products/pc/app/tools/verify_sync_ingest_persistence_01.mjs",
    "products/pc/app/tools/verify_pc_backoffice_core_01.mjs",
    "products/pc/app/tools/verify_pc_kpi_dashboard_02.mjs",
    "products/tablet/app/app/api/pos/sales/complete/route.ts",
    "products/pc/app/app/api/backoffice/sync/ingest/route.ts",
    "products/pc/app/src/lib/backoffice/sync-ingest-store.ts",
]


def main() -> int:
    missing = []
    for rel in CRITICAL_FILES:
        if not (REPO_SHARE_ROOT / rel).exists():
            missing.append(rel)

    if missing:
        print("FAIL verify_chatgpt_share_sync_coverage")
        for rel in missing:
            print("missing:", rel)
        return 1

    status = {}
    if STATUS_PATH.exists():
        try:
            status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        except Exception:
            status = {}

    print("OK verify_chatgpt_share_sync_coverage")
    print(f"share_root={SHARE_ROOT}")
    print(f"critical_files={len(CRITICAL_FILES)}")
    print(f"source_file_count={status.get('source_file_count')}")
    print(f"mirrored_file_count={status.get('mirrored_file_count')}")
    print(f"last_successful_sync_at={status.get('last_successful_sync_at')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
