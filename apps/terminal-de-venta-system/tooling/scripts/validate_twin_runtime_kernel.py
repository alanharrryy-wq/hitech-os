from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_FILES = [
    "shared/twin-kernel/src/types/capability.ts",
    "shared/twin-kernel/src/validation/twin-capability-validator.ts",
    "shared/twin-kernel/src/runtime/twin-capability-registry.ts",
    "shared/twin-kernel/src/data/twin-capability-manifest.ts",
    "shared/twin-kernel/src/data/twin-parity-matrix.ts",
    "shared/twin-kernel/src/sync/twin-capability-events.ts",
    "shared/twin-kernel/src/index.ts",
    "products/pc/app/src/composition/twin-capabilities.ts",
    "products/tablet/app/src/composition/twin-capabilities.ts",
    "docs/prisma/ui/shared/contracts/twin-capability-contract.md",
    "docs/prisma/ui/qa/twin-runtime-smoke.md",
    "docs/prisma/ui/implementation/twin-runtime-integration.md",
]

REQUIRED_CAPABILITY_IDS = [
    "catalog-master",
    "stock-signal",
    "inventory-count",
    "purchase-order",
    "receiving-flow",
    "replenishment-signal",
    "sales-ticket",
    "checkout-payment",
    "shift-cash",
    "return-flow",
    "sync-health",
    "audit-trail",
    "dashboard-kpis",
    "customer-context",
]

def default_report_dir() -> Path:
    win = Path(r"F:\descargasf")
    if win.exists() or sys.platform.startswith("win"):
        win.mkdir(parents=True, exist_ok=True)
        return win
    fallback = Path.cwd()
    return fallback

def validate(root: Path) -> tuple[int, dict]:
    errors: list[str] = []
    warnings: list[str] = []
    files: list[dict] = []

    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.exists():
            errors.append(f"missing:{rel}")
            continue
        files.append({"path": rel, "bytes": path.stat().st_size})

    manifest_path = root / "shared/twin-kernel/src/data/twin-capability-manifest.ts"
    if manifest_path.exists():
        text = manifest_path.read_text(encoding="utf-8")
        found_ids = sorted(set(re.findall(r'"id"\s*:\s*"([a-z0-9-]+)"', text)))
        missing_ids = [capability_id for capability_id in REQUIRED_CAPABILITY_IDS if capability_id not in found_ids]
        if missing_ids:
            errors.append("missing_capability_ids:" + ",".join(missing_ids))
        if len(found_ids) < 14:
            errors.append(f"too_few_capabilities:{len(found_ids)}")
        if text.count('"surface": "pc"') < 14 or text.count('"surface": "tablet"') < 14:
            errors.append("surface_bindings_incomplete")
        if text.count('"required": true') < 12:
            warnings.append("low_required_event_count")
    else:
        errors.append("manifest_not_readable")

    for rel in [
        "products/pc/app/src/composition/twin-capabilities.ts",
        "products/tablet/app/src/composition/twin-capabilities.ts",
    ]:
        path = root / rel
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if "createTwinCapabilityRegistry" not in text:
                errors.append(f"missing_registry_usage:{rel}")

    report = {
        "ok": not errors,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "root": str(root),
        "required_files": len(REQUIRED_FILES),
        "files": files,
        "errors": errors,
        "warnings": warnings,
    }
    return (0 if not errors else 2), report

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PRISMA twin runtime kernel installation.")
    parser.add_argument("root", help="Path to terminal-de-venta-system root")
    parser.add_argument("--report-dir", default=None, help="Optional report output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    code, report = validate(root)
    out_dir = Path(args.report_dir).resolve() if args.report_dir else default_report_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "prisma_twin_runtime_kernel_validation.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"report={report_path}")
    return code

if __name__ == "__main__":
    raise SystemExit(main())
