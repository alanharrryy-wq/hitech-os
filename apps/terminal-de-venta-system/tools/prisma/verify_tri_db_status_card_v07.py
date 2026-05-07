#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FILES = [
    "products/pc/app/app/sync/page.tsx",
    "products/pc/app/components/sync/sync-release-workspace.tsx",
    "products/pc/app/components/sync/tri-db-status-card.tsx",
    "products/pc/app/src/server/services/tri-db-status.service.ts",
    "products/pc/app/src/modules/sync/tri-db-status.types.ts",
]

REQUIRED_TEXT = {
    "products/pc/app/app/sync/page.tsx": ["getTriDbStatusCard", "triDbStatus"],
    "products/pc/app/components/sync/sync-release-workspace.tsx": ["TriDbStatusCard", "triDbStatus"],
    "products/pc/app/components/sync/tri-db-status-card.tsx": ["Tablet → PC canonical → Mobile", "bridgeOutboxAcknowledged", "SurfacePanel"],
    "products/pc/app/src/server/services/tri-db-status.service.ts": ["status.latest.json", "PRISMA_TRI_DB_STATUS_JSON", "getTriDbStatusCard"],
    "products/pc/app/src/modules/sync/tri-db-status.types.ts": ["TriDbStatusCardModel", "TriDbSurfaceMetrics"],
}

def resolve_terminal_root(target_root: Path) -> Path:
    root = target_root.expanduser().resolve()
    if (root / "terminal_de_venta.cmd").exists() and (root / "products").exists():
        return root
    nested = root / "apps" / "terminal-de-venta-system"
    if (nested / "terminal_de_venta.cmd").exists() and (nested / "products").exists():
        return nested.resolve()
    raise RuntimeError(f"No encontre terminal-de-venta-system desde: {root}")

def verify_sources(terminal_root: Path) -> list[str]:
    notes: list[str] = []
    for rel in REQUIRED_FILES:
        path = terminal_root / rel
        if not path.exists():
            raise RuntimeError(f"Falta archivo instalado: {path}")
        text = path.read_text(encoding="utf-8")
        for token in REQUIRED_TEXT.get(rel, []):
            if token not in text:
                raise RuntimeError(f"Falta token esperado en {rel}: {token}")
        notes.append(f"OK {rel}")
    return notes

def verify_status_json(terminal_root: Path) -> list[str]:
    latest = terminal_root / "shared" / "tri-db" / "status.latest.json"
    if not latest.exists():
        return [f"WARN status.latest.json no existe todavia: {latest}"]
    data = json.loads(latest.read_text(encoding="utf-8"))
    required = ["status", "latest_bridge_status", "bridge_tables_projected", "bridge_rows_inserted_or_updated", "bridge_outbox_acknowledged", "tablet", "pc", "parity"]
    missing = [key for key in required if key not in data]
    if missing:
        raise RuntimeError(f"status.latest.json incompleto. Faltan: {', '.join(missing)}")
    return [f"status.latest.json OK: status={data.get('status')} bridge={data.get('latest_bridge_status')}"]

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify PRISMA Tri-DB Status Card v07")
    parser.add_argument("--target-root", default=r"F:\repos\hitech-os")
    args = parser.parse_args(argv)
    try:
        terminal_root = resolve_terminal_root(Path(args.target_root))
        notes = []
        notes.extend(verify_sources(terminal_root))
        notes.extend(verify_status_json(terminal_root))
        print("VERIFY_TRI_DB_STATUS_CARD_READY")
        for note in notes:
            print(note)
        return 0
    except Exception as exc:
        print(f"VERIFY_TRI_DB_STATUS_CARD_BLOCKED: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
