#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REQUIRED_FILES = {
    "products/pc/app/app/api/sync/tri-db/run/route.ts": ["runTriDbSyncNow", "NextResponse", "POST"],
    "products/pc/app/src/server/services/tri-db-command.service.ts": ["tri_db_bridge.py", "tri_db_status.py", "runTriDbSyncNow", "spawn"],
    "products/pc/app/components/sync/tri-db-sync-action.tsx": ["use client", "Sincronizar ahora", "/api/sync/tri-db/run"],
    "products/pc/app/components/sync/sync-release-workspace.tsx": ["TriDbSyncAction", "TriDbStatusCard"],
}

def resolve_terminal_root(target_root: Path) -> Path:
    root = target_root.expanduser().resolve()
    if (root / "terminal_de_venta.cmd").exists() and (root / "products").exists():
        return root
    nested = root / "apps" / "terminal-de-venta-system"
    if (nested / "terminal_de_venta.cmd").exists() and (nested / "products").exists():
        return nested.resolve()
    raise RuntimeError(f"No encontre terminal-de-venta-system desde: {root}")

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify PRISMA Tri-DB Sync Action v08")
    parser.add_argument("--target-root", default=r"F:\repos\hitech-os")
    args = parser.parse_args(argv)
    try:
        terminal_root = resolve_terminal_root(Path(args.target_root))
        bridge = terminal_root / "tools" / "prisma" / "tri_db_bridge.py"
        status = terminal_root / "tools" / "prisma" / "tri_db_status.py"
        if not bridge.exists():
            raise RuntimeError(f"Falta bridge v04 instalado: {bridge}")
        if not status.exists():
            raise RuntimeError(f"Falta status v06 instalado: {status}")
        for rel, tokens in REQUIRED_FILES.items():
            path = terminal_root / rel
            if not path.exists():
                raise RuntimeError(f"Falta archivo instalado: {path}")
            text = path.read_text(encoding="utf-8")
            for token in tokens:
                if token not in text:
                    raise RuntimeError(f"Falta token esperado en {rel}: {token}")
        print("VERIFY_TRI_DB_SYNC_ACTION_READY")
        print(f"OK terminal_root={terminal_root}")
        print(f"OK bridge={bridge}")
        print(f"OK status={status}")
        return 0
    except Exception as exc:
        print(f"VERIFY_TRI_DB_SYNC_ACTION_BLOCKED: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
