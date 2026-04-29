from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(r"F:\repos\hitech-os\apps\terminal-de-venta-system")
SHARE_ROOT = Path(r"F:\terminal_de_venta_chatgpt_share")
REPO_SHARE_ROOT = SHARE_ROOT / "repo" / "apps" / "terminal-de-venta-system"
STATUS_PATH = SHARE_ROOT / "SYNC_STATUS.json"
LAST_SYNC_PATH = SHARE_ROOT / "LAST_SYNC.txt"
HIDDEN_LAUNCHER = PROJECT_ROOT / "tooling" / "scripts" / "sync_chatgpt_share_hidden.vbs"

EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    ".turbo",
    ".cache",
    ".parcel-cache",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "env",
    ".pnpm-store",
}

EXCLUDED_SUFFIXES = {
    ".db",
    ".sqlite",
    ".sqlite3",
    ".zip",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".mp4",
    ".mov",
    ".avi",
    ".mp3",
    ".wav",
    ".pdf",
    ".pptx",
    ".docx",
    ".xlsx",
    ".log",
}

INCLUDED_SUFFIXES = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".json",
    ".md",
    ".txt",
    ".cmd",
    ".ps1",
    ".py",
    ".prisma",
    ".css",
    ".scss",
    ".html",
    ".yml",
    ".yaml",
    ".toml",
    ".lock",
}

IMPORTANT_NAMES = {
    "package.json",
    "pnpm-lock.yaml",
    "pnpm-workspace.yaml",
    "tsconfig.json",
    "next.config.js",
    "next.config.mjs",
    "eslint.config.js",
    "middleware.ts",
    "tailwind.config.ts",
    "postcss.config.js",
    "README",
    "README.md",
    "LICENSE",
}

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


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def as_posix(path: Path) -> str:
    return path.as_posix()


def should_skip_dir(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)


def is_useful_file(path: Path) -> bool:
    if should_skip_dir(path.relative_to(PROJECT_ROOT).parent):
        return False

    name = path.name
    suffix = path.suffix.lower()

    if name.startswith(".env") and name != ".env.example":
        return False

    if suffix in EXCLUDED_SUFFIXES:
        return False

    try:
        if path.stat().st_size > 2 * 1024 * 1024:
            return False
    except OSError:
        return False

    if suffix in INCLUDED_SUFFIXES:
        return True

    if name in IMPORTANT_NAMES:
        return True

    if name.endswith(".env.example"):
        return True

    return False


def collect_source_files() -> list[Path]:
    files: list[Path] = []
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(PROJECT_ROOT)
        except ValueError:
            continue
        if should_skip_dir(rel.parent):
            continue
        if is_useful_file(path):
            files.append(path)
    return sorted(files, key=lambda p: as_posix(p.relative_to(PROJECT_ROOT)).lower())


def mirror() -> dict:
    if not PROJECT_ROOT.exists():
        raise SystemExit(f"Project root not found: {PROJECT_ROOT}")

    SHARE_ROOT.mkdir(parents=True, exist_ok=True)
    REPO_SHARE_ROOT.mkdir(parents=True, exist_ok=True)

    source_files = collect_source_files()
    wanted_rel = {p.relative_to(PROJECT_ROOT) for p in source_files}

    copied = 0
    updated = 0

    for src in source_files:
        rel = src.relative_to(PROJECT_ROOT)
        dst = REPO_SHARE_ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        should_copy = True
        if dst.exists():
            try:
                s1 = src.stat()
                s2 = dst.stat()
                should_copy = s1.st_size != s2.st_size or int(s1.st_mtime) != int(s2.st_mtime)
            except OSError:
                should_copy = True

        if should_copy:
            shutil.copy2(src, dst)
            updated += 1
        copied += 1

    removed = 0
    if REPO_SHARE_ROOT.exists():
        for dst in sorted(REPO_SHARE_ROOT.rglob("*"), reverse=True):
            if dst.is_file():
                rel = dst.relative_to(REPO_SHARE_ROOT)
                if rel not in wanted_rel:
                    dst.unlink()
                    removed += 1
            elif dst.is_dir():
                try:
                    next(dst.iterdir())
                except StopIteration:
                    dst.rmdir()

    missing_critical = []
    for rel_text in CRITICAL_FILES:
        if not (REPO_SHARE_ROOT / Path(rel_text)).exists():
            missing_critical.append(rel_text)

    status = {
        "fresh": len(missing_critical) == 0,
        "mode": "future_proof_project_wide_useful_file_mirror",
        "project_root": str(PROJECT_ROOT),
        "share_root": str(SHARE_ROOT),
        "repo_share_root": str(REPO_SHARE_ROOT),
        "last_successful_sync_at": now_iso() if not missing_critical else None,
        "source_file_count": len(source_files),
        "mirrored_file_count": copied,
        "updated_file_count": updated,
        "removed_stale_file_count": removed,
        "critical_files": len(CRITICAL_FILES),
        "missing_critical_files": missing_critical,
        "auto_refresh_installed": check_task_installed(),
    }

    STATUS_PATH.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")
    LAST_SYNC_PATH.write_text(
        f"{now_iso()}\nsource_file_count={len(source_files)}\nmirrored_file_count={copied}\nmissing_critical={len(missing_critical)}\n",
        encoding="utf-8",
    )

    return status


def check_task_installed() -> bool:
    result = subprocess.run(
        ["schtasks.exe", "/Query", "/TN", "TerminalDeVentaChatGPTShareSync"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode == 0


def write_hidden_launcher() -> None:
    HIDDEN_LAUNCHER.parent.mkdir(parents=True, exist_ok=True)
    HIDDEN_LAUNCHER.write_text(
        'Set shell = CreateObject("WScript.Shell")\n'
        f'shell.Run """{sys.executable}"" ""{PROJECT_ROOT / "tooling" / "scripts" / "sync_chatgpt_share.py"}"" --sync", 0, False\n',
        encoding="utf-8",
    )


def install_scheduled_task() -> dict:
    write_hidden_launcher()

    command = [
        "schtasks.exe",
        "/Create",
        "/TN",
        "TerminalDeVentaChatGPTShareSync",
        "/SC",
        "MINUTE",
        "/MO",
        "5",
        "/TR",
        f'"{Path(os.environ.get("WINDIR", r"C:\\Windows")) / "System32" / "wscript.exe"}" //B "{HIDDEN_LAUNCHER}"',
        "/F",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    return {
        "task_name": "TerminalDeVentaChatGPTShareSync",
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "hidden_launcher": str(HIDDEN_LAUNCHER),
        "command": " ".join(command),
    }


def verify() -> dict:
    status = {}
    if STATUS_PATH.exists():
        try:
            status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
        except Exception:
            status = {}

    missing = []
    for rel_text in CRITICAL_FILES:
        if not (REPO_SHARE_ROOT / Path(rel_text)).exists():
            missing.append(rel_text)

    result = {
        "ok": len(missing) == 0,
        "share_root": str(SHARE_ROOT),
        "repo_share_root": str(REPO_SHARE_ROOT),
        "critical_files": len(CRITICAL_FILES),
        "missing": missing,
        "source_file_count": status.get("source_file_count"),
        "mirrored_file_count": status.get("mirrored_file_count"),
        "last_successful_sync_at": status.get("last_successful_sync_at"),
    }

    if not result["ok"]:
        raise SystemExit("verify failed: missing critical files: " + ", ".join(missing))

    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--install-scheduled-task", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    if args.install_scheduled_task:
        result = install_scheduled_task()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if result["returncode"] != 0:
            return result["returncode"]

    if args.sync:
        status = mirror()
        print("share_root:", SHARE_ROOT)
        print("sync_result:", "PASS" if status["fresh"] else "FAIL")
        print("fresh:", status["fresh"])
        print("source_file_count:", status["source_file_count"])
        print("mirrored_file_count:", status["mirrored_file_count"])
        print("updated_file_count:", status["updated_file_count"])
        print("removed_stale_file_count:", status["removed_stale_file_count"])
        print("missing_critical_files:", status["missing_critical_files"])

    if args.verify:
        result = verify()
        print("OK verify_chatgpt_share_sync_coverage")
        print("share_root=" + result["share_root"])
        print("critical_files=" + str(result["critical_files"]))
        print("source_file_count=" + str(result["source_file_count"]))
        print("mirrored_file_count=" + str(result["mirrored_file_count"]))
        print("last_successful_sync_at=" + str(result["last_successful_sync_at"]))

    if args.status:
        if STATUS_PATH.exists():
            print(STATUS_PATH.read_text(encoding="utf-8"))
        else:
            print("No SYNC_STATUS.json found:", STATUS_PATH)
            return 1

    if not (args.sync or args.verify or args.install_scheduled_task or args.status):
        parser.print_help()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
