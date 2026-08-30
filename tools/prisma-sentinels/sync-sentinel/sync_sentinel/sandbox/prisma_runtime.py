from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from .database import sqlite_url

APP_REL = Path("apps/terminal-de-venta-system")


def _run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 600) -> dict[str, object]:
    cp = subprocess.run(
        cmd, cwd=str(cwd), env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=timeout, check=False,
    )
    text = ((cp.stdout or "") + "\n" + (cp.stderr or ""))[-6000:]
    return {"ok": cp.returncode == 0, "returncode": cp.returncode, "tail": text}


def install_workspace(worktree: Path) -> dict[str, object]:
    return _run(
        ["pnpm", "install", "--frozen-lockfile", "--ignore-scripts"],
        cwd=worktree, timeout=900,
    )


def _pc_sentinel_schema(worktree: Path) -> Path:
    terminal = worktree / APP_REL
    source = terminal / "prisma/schema.prisma"
    pc_app = terminal / "products/pc/app"
    target = pc_app / ".sync-sentinel/prisma/schema.prisma"
    target.parent.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8")
    pattern = re.compile(r'generator\s+client\s*\{(?P<body>.*?)\}', re.DOTALL)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("BLOCKED_CANONICAL_PRISMA_GENERATOR_NOT_FOUND")
    body = match.group("body")
    body = re.sub(r'\n\s*output\s*=\s*"[^"]*"', "", body)
    replacement = 'generator client {' + body.rstrip() + '\n  output   = "../../.generated/prisma-client"\n}'
    target.write_text(text[:match.start()] + replacement + text[match.end():], encoding="utf-8", newline="\n")
    return target


def prepare_isolated_databases(worktree: Path, data_root: Path) -> dict[str, object]:
    terminal = worktree / APP_REL
    pc_app = terminal / "products/pc/app"
    tablet_app = terminal / "products/tablet/app"
    pc_db = data_root / "pc/canonical.db"
    tablet_db = data_root / "tablet/tablet-pos.db"
    pc_url = sqlite_url(pc_db, data_root, "pc")
    tablet_url = sqlite_url(tablet_db, data_root, "tablet")
    common = dict(os.environ)
    common["PRISMA_GENERATE_SKIP_AUTOINSTALL"] = "true"

    env_pc = dict(common)
    env_pc["DATABASE_URL"] = pc_url
    migrations = _run(
        ["python", str(terminal / "tooling/scripts/migrate_prisma_canonical.py")],
        cwd=terminal, env=env_pc, timeout=300,
    )
    if not migrations["ok"]:
        return {"ok": False, "pcDb": pc_db, "tabletDb": tablet_db, "steps": {"pcMigrations": migrations}}

    sentinel_schema = _pc_sentinel_schema(worktree)
    pc_generate = _run(
        ["pnpm", "exec", "prisma", "generate", "--schema", str(sentinel_schema)],
        cwd=pc_app, env=env_pc, timeout=300,
    )
    if not pc_generate["ok"]:
        return {"ok": False, "pcDb": pc_db, "tabletDb": tablet_db, "steps": {"pcMigrations": migrations, "pcGenerate": pc_generate}}

    env_tab = dict(common)
    env_tab.update({
        "DATABASE_URL": tablet_url,
        "TABLET_DATABASE_URL": tablet_url,
        "TABLET_DATABASE_PATH": str(tablet_db.resolve()),
    })
    tablet_schema = tablet_app / "prisma/schema.prisma"
    tablet_generate = _run(
        ["pnpm", "exec", "prisma", "generate", "--schema", str(tablet_schema)],
        cwd=tablet_app, env=env_tab, timeout=300,
    )
    if not tablet_generate["ok"]:
        return {"ok": False, "pcDb": pc_db, "tabletDb": tablet_db, "steps": {"pcMigrations": migrations, "pcGenerate": pc_generate, "tabletGenerate": tablet_generate}}
    tablet_push = _run(
        ["pnpm", "exec", "prisma", "db", "push", "--schema", str(tablet_schema), "--skip-generate"],
        cwd=tablet_app, env=env_tab, timeout=300,
    )
    steps = {
        "pcMigrations": migrations,
        "pcGenerate": pc_generate,
        "tabletGenerate": tablet_generate,
        "tabletDbPush": tablet_push,
    }
    return {
        "ok": all(bool(v.get("ok")) for v in steps.values()),
        "pcDb": pc_db,
        "tabletDb": tablet_db,
        "pcUrl": pc_url,
        "tabletUrl": tablet_url,
        "sentinelPcSchema": sentinel_schema,
        "steps": steps,
    }
