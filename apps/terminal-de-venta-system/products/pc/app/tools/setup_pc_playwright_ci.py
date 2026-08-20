#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

PLAYWRIGHT_VERSION = "1.60.0"
APP_REL = Path("apps/terminal-de-venta-system/products/pc/app")


def run(cmd: list[str], *, cwd: Path) -> None:
    print("[playwright-ci] $ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> int:
    repo = Path(os.environ.get("GITHUB_WORKSPACE") or Path.cwd()).resolve()
    runner_temp = Path(os.environ.get("RUNNER_TEMP") or repo / ".tmp").resolve()
    app = repo / APP_REL
    install_root = runner_temp / "pc-playwright-ci"
    module_root = install_root / "node_modules"
    test_module = module_root / "@playwright" / "test"
    cli = module_root / ".bin" / "playwright"

    if install_root.exists():
        shutil.rmtree(install_root)
    install_root.mkdir(parents=True)

    run(["npm", "init", "-y"], cwd=install_root)
    run(
        [
            "npm",
            "install",
            "--no-save",
            "--package-lock=false",
            f"@playwright/test@{PLAYWRIGHT_VERSION}",
        ],
        cwd=install_root,
    )
    if not test_module.is_dir() or not cli.is_file():
        raise SystemExit("isolated Playwright install did not materialize expected module/CLI")

    run([str(cli), "install", "--with-deps", "chromium"], cwd=install_root)

    link_parent = app / "node_modules" / "@playwright"
    link_parent.mkdir(parents=True, exist_ok=True)
    link = link_parent / "test"
    if link.exists() or link.is_symlink():
        if link.is_symlink() or link.is_file():
            link.unlink()
        else:
            shutil.rmtree(link)
    link.symlink_to(test_module, target_is_directory=True)

    explicit_module = test_module / "index.js"
    github_env = os.environ.get("GITHUB_ENV")
    if github_env:
        with open(github_env, "a", encoding="utf-8") as handle:
            handle.write(f"PRISMA_PLAYWRIGHT_TEST_MODULE={explicit_module}\n")

    run(
        [
            "node",
            "--input-type=module",
            "-e",
            "const m=await import('@playwright/test'); if(!m.chromium) process.exit(2); console.log('PLAYWRIGHT_MODULE_RESOLUTION_OK');",
        ],
        cwd=app,
    )

    report = {
        "verifier": "PC_PLAYWRIGHT_CI_SETUP_V1",
        "installRoot": str(install_root),
        "module": str(explicit_module),
        "linkedIntoPcApp": str(link),
        "version": PLAYWRIGHT_VERSION,
        "repoMutation": False,
        "packageManifestMutation": False,
        "lockfileMutation": False,
        "pass": True,
    }
    print(json.dumps(report, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
