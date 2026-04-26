#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TERMINAL_ROOT = Path(__file__).resolve().parents[2]
HITECH_ROOT = TERMINAL_ROOT.parents[1]
SHARE_ROOT = Path("F:/terminal_de_venta_chatgpt_share")
STAGING_ROOT = Path("F:/terminal_de_venta_chatgpt_share.__sync_tmp")
LOCK_PATH = Path("F:/terminal_de_venta_chatgpt_share.__sync_lock")
EVIDENCE_ROOT = HITECH_ROOT / "tools" / "_local" / "evidence"
TASK_NAME = "TerminalDeVentaChatGPTShareSync"
TASK_INTERVAL_MINUTES = 1
STATUS_VERSION = 2
MAX_FILE_BYTES = 1_000_000
HIDDEN_LAUNCHER = TERMINAL_ROOT / "tooling" / "scripts" / "sync_chatgpt_share_hidden.vbs"
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

INCLUDE_DIRS = (
    (TERMINAL_ROOT / "docs", Path("repo/docs")),
    (TERMINAL_ROOT / "prisma", Path("repo/prisma")),
    (TERMINAL_ROOT / "shared" / "twin-kernel", Path("repo/shared/twin-kernel")),
    (TERMINAL_ROOT / "tooling" / "scripts", Path("repo/tooling/scripts")),
    (TERMINAL_ROOT / "products" / "pc" / "app", Path("repo/products/pc/app")),
    (TERMINAL_ROOT / "products" / "tablet" / "app", Path("repo/products/tablet/app")),
)

INCLUDE_FILES = (
    (TERMINAL_ROOT / "README.md", Path("repo/README.md")),
    (TERMINAL_ROOT / "REPO_STRUCTURE_GOVERNANCE.md", Path("repo/REPO_STRUCTURE_GOVERNANCE.md")),
    (TERMINAL_ROOT / "STRUCTURAL_CLEANUP_REPORT.md", Path("repo/STRUCTURAL_CLEANUP_REPORT.md")),
    (TERMINAL_ROOT / "terminal_de_venta.cmd", Path("repo/terminal_de_venta.cmd")),
    (
        EVIDENCE_ROOT / "terminal-de-venta-prisma-canonical-validation.json",
        Path("evidence/terminal-de-venta-prisma-canonical-validation.json"),
    ),
    (
        EVIDENCE_ROOT / "terminal-de-venta-prisma-canonical-summary.txt",
        Path("evidence/terminal-de-venta-prisma-canonical-summary.txt"),
    ),
)

ROOT_GENERATED_FILES = {
    Path("README.md"),
    Path("SHARE_MANIFEST.json"),
    Path("SYNC_STATUS.json"),
    Path("LAST_SYNC.txt"),
}

EXCLUDED_DIR_NAMES = {
    ".cache",
    ".git",
    ".next",
    ".nuxt",
    ".output",
    ".parcel-cache",
    ".pnpm-store",
    ".swc",
    ".turbo",
    ".vercel",
    ".vite",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "temp",
    "tmp",
}

EXCLUDED_FILE_NAMES = {
    ".ds_store",
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "thumbs.db",
    "tsconfig.tsbuildinfo",
}

EXCLUDED_SUFFIXES = {
    ".7z",
    ".avi",
    ".db",
    ".db-journal",
    ".gif",
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".log",
    ".mov",
    ".mp3",
    ".mp4",
    ".pdf",
    ".png",
    ".rar",
    ".sqlite",
    ".sqlite3",
    ".tar",
    ".tgz",
    ".wav",
    ".webm",
    ".webp",
    ".zip",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def win(path: Path) -> str:
    return str(path.resolve())


def rel_text(path: Path) -> str:
    return str(path).replace("/", "\\")


def guard_path(path: Path, expected: Path) -> Path:
    resolved = path.resolve()
    if resolved != expected.resolve():
        raise RuntimeError(f"Refusing unexpected path: {resolved}")
    if resolved.drive.upper() != "F:":
        raise RuntimeError(f"Expected an F:\\ path, got: {resolved}")
    return resolved


def guard_share_root() -> Path:
    root = guard_path(SHARE_ROOT, Path("F:/terminal_de_venta_chatgpt_share"))
    if root.parent != Path("F:/").resolve():
        raise RuntimeError(f"Share root must stay directly under F:\\: {root}")
    return root


def reset_staging() -> None:
    staging = guard_path(STAGING_ROOT, Path("F:/terminal_de_venta_chatgpt_share.__sync_tmp"))
    if staging.exists():
        if not staging.is_dir():
            raise RuntimeError(f"Staging path is not a directory: {staging}")
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)


def remove_staging() -> None:
    staging = guard_path(STAGING_ROOT, Path("F:/terminal_de_venta_chatgpt_share.__sync_tmp"))
    if staging.exists():
        if not staging.is_dir():
            raise RuntimeError(f"Staging path is not a directory: {staging}")
        shutil.rmtree(staging)


def acquire_lock() -> int:
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        handle = os.open(str(LOCK_PATH), flags)
    except FileExistsError as exc:
        raise RuntimeError(f"Sync lock already exists: {LOCK_PATH}") from exc
    os.write(handle, f"{os.getpid()} {utc_now()}\n".encode("utf-8"))
    return handle


def release_lock(handle: int) -> None:
    os.close(handle)
    try:
        LOCK_PATH.unlink()
    except FileNotFoundError:
        pass


def skip_file(path: Path) -> str | None:
    name = path.name.lower()
    suffixes = [suffix.lower() for suffix in path.suffixes]
    if name in EXCLUDED_FILE_NAMES:
        return "excluded file name"
    if any(suffix in EXCLUDED_SUFFIXES for suffix in suffixes):
        return "excluded file suffix"
    if path.is_symlink():
        return "symlink"
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        return f"larger than {MAX_FILE_BYTES} bytes"
    return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_record(source: Path, destination: Path) -> dict[str, Any]:
    stat = source.stat()
    return {
        "source": win(source),
        "destination": rel_text(destination),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": sha256_file(source),
    }


def collect_file(source: Path, destination: Path, records: list[dict[str, Any]], skipped: list[dict], missing: list[str]) -> None:
    if not source.exists():
        missing.append(win(source))
        return
    reason = skip_file(source)
    if reason:
        skipped.append({"source": win(source), "reason": reason})
        return
    records.append(source_record(source, destination))


def build_source_snapshot() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    missing: list[str] = []

    for source, destination in INCLUDE_FILES:
        collect_file(source, destination, records, skipped, missing)

    for source, destination in INCLUDE_DIRS:
        if not source.exists():
            missing.append(win(source))
            continue
        for current, dirs, files in os.walk(source):
            current_path = Path(current)
            retained_dirs: list[str] = []
            for dirname in sorted(dirs):
                child = current_path / dirname
                if dirname.lower() in EXCLUDED_DIR_NAMES:
                    skipped.append({"source": win(child), "reason": "excluded directory"})
                elif child.is_symlink():
                    skipped.append({"source": win(child), "reason": "symlink directory"})
                else:
                    retained_dirs.append(dirname)
            dirs[:] = retained_dirs

            for filename in sorted(files):
                source_file = current_path / filename
                relative = source_file.relative_to(source)
                collect_file(source_file, destination / relative, records, skipped, missing)

    records.sort(key=lambda item: item["destination"].lower())
    digest = hashlib.sha256()
    total_bytes = 0
    for record in records:
        total_bytes += int(record["size"])
        digest.update(record["destination"].replace("\\", "/").encode("utf-8"))
        digest.update(b"\0")
        digest.update(record["sha256"].encode("ascii"))
        digest.update(b"\0")
        digest.update(str(record["size"]).encode("ascii"))
        digest.update(b"\0")

    return {
        "fingerprint": digest.hexdigest(),
        "files": records,
        "file_count": len(records),
        "byte_count": total_bytes,
        "skipped": skipped,
        "missing": missing,
        "skipped_count": len(skipped),
        "missing_count": len(missing),
    }


def run_subprocess(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        creationflags=CREATE_NO_WINDOW,
    )


def task_query() -> dict[str, Any]:
    result = run_subprocess(
        ["schtasks", "/Query", "/TN", TASK_NAME, "/FO", "LIST"],
    )
    return {
        "task_name": TASK_NAME,
        "installed": result.returncode == 0,
        "interval_minutes": TASK_INTERVAL_MINUTES,
        "query_returncode": result.returncode,
    }


def scheduled_task_action() -> str:
    wscript = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32" / "wscript.exe"
    return f'"{wscript}" //B "{HIDDEN_LAUNCHER.resolve()}"'


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def find_junk() -> dict[str, Any]:
    root = guard_share_root()
    if not root.exists():
        return {"directories": [], "files": [], "reparse_points": []}

    junk_dirs: list[str] = []
    junk_files: list[str] = []
    reparse_points: list[str] = []
    for path in root.rglob("*"):
        try:
            is_reparse = bool(path.stat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
        except AttributeError:
            is_reparse = path.is_symlink()
        except OSError:
            continue
        if is_reparse or path.is_symlink():
            reparse_points.append(win(path))
        if path.is_dir() and path.name.lower() in EXCLUDED_DIR_NAMES:
            junk_dirs.append(win(path))
        if path.is_file():
            name = path.name.lower()
            suffixes = [suffix.lower() for suffix in path.suffixes]
            if name in EXCLUDED_FILE_NAMES or any(suffix in EXCLUDED_SUFFIXES for suffix in suffixes):
                junk_files.append(win(path))
    return {
        "directories": sorted(junk_dirs),
        "files": sorted(junk_files),
        "reparse_points": sorted(reparse_points),
    }


def mirrored_state(snapshot: dict[str, Any]) -> dict[str, Any]:
    root = guard_share_root()
    missing: list[str] = []
    mismatched: list[str] = []
    matched = 0
    for record in snapshot["files"]:
        destination = root / record["destination"]
        if not destination.exists():
            missing.append(rel_text(Path(record["destination"])))
            continue
        if destination.stat().st_size != record["size"] or sha256_file(destination) != record["sha256"]:
            mismatched.append(rel_text(Path(record["destination"])))
            continue
        matched += 1
    return {
        "matched_file_count": matched,
        "missing": missing,
        "mismatched": mismatched,
    }


def share_file_count() -> int:
    root = guard_share_root()
    if not root.exists():
        return 0
    return sum(1 for path in root.rglob("*") if path.is_file())


def status_from_snapshot(
    snapshot: dict[str, Any],
    *,
    after_sync: bool,
    sync_error: str | None = None,
    task_installed_override: bool | None = None,
) -> dict[str, Any]:
    now = utc_now()
    previous = read_json(SHARE_ROOT / "SYNC_STATUS.json") or {}
    previous_fingerprint = previous.get("last_synced_source_fingerprint")
    previous_sync_at = previous.get("last_successful_sync_at")
    mirrored = mirrored_state(snapshot) if SHARE_ROOT.exists() else {"matched_file_count": 0, "missing": [], "mismatched": []}
    junk = find_junk()

    stale_reasons: list[str] = []
    if sync_error:
        stale_reasons.append(sync_error)
    if snapshot["missing"]:
        stale_reasons.append("required source files are missing")
    if not after_sync:
        if not previous:
            stale_reasons.append("SYNC_STATUS.json is missing")
        elif previous_fingerprint != snapshot["fingerprint"]:
            stale_reasons.append("source fingerprint changed after last successful sync")
    if mirrored["missing"]:
        stale_reasons.append("mirrored files are missing")
    if mirrored["mismatched"]:
        stale_reasons.append("mirrored files differ from current source")
    if junk["directories"] or junk["files"] or junk["reparse_points"]:
        stale_reasons.append("forbidden junk or reparse points exist in share folder")

    fresh = not stale_reasons
    last_synced_fingerprint = snapshot["fingerprint"] if after_sync and not sync_error else previous_fingerprint
    last_successful_sync_at = now if after_sync and not sync_error else previous_sync_at
    task_installed = task_installed_override if task_installed_override is not None else task_query()["installed"]

    return {
        "status_version": STATUS_VERSION,
        "source_root": win(TERMINAL_ROOT),
        "share_root": win(SHARE_ROOT),
        "last_checked_at": now,
        "last_successful_sync_at": last_successful_sync_at,
        "sync_result": "PASS" if fresh else ("FAIL" if sync_error else "STALE"),
        "fresh": fresh,
        "stale_reasons": stale_reasons,
        "source_fingerprint": snapshot["fingerprint"],
        "last_synced_source_fingerprint": last_synced_fingerprint,
        "source_file_count": snapshot["file_count"],
        "source_byte_count": snapshot["byte_count"],
        "share_file_count": share_file_count(),
        "mirrored_file_count": mirrored["matched_file_count"],
        "missing_source_count": snapshot["missing_count"],
        "skipped_count": snapshot["skipped_count"],
        "junk_directories_found": len(junk["directories"]),
        "junk_files_found": len(junk["files"]),
        "reparse_points_found": len(junk["reparse_points"]),
        "auto_refresh": {
            "strategy": "Windows Scheduled Task",
            "task_name": TASK_NAME,
            "interval_minutes": TASK_INTERVAL_MINUTES,
            "installed": task_installed,
            "command": scheduled_task_action(),
            "hidden_launcher": win(HIDDEN_LAUNCHER),
        },
        "normal_user_flow": "Open F:\\, right-click F:\\terminal_de_venta_chatgpt_share, compress to ZIP, upload.",
    }


def readme_lines(auto_refresh_installed: bool) -> list[str]:
    auto_line = "Auto-refresh: Windows task refreshes this folder when source changes are detected."
    if not auto_refresh_installed:
        auto_line = "Auto-refresh: not installed; use the maintenance command only if LAST_SYNC says stale."
    return [
        "# Terminal de Venta ChatGPT Share",
        "Dedicated physical ChatGPT share surface for external review.",
        "Normal flow: open F:\\, right-click this folder, compress to ZIP, upload.",
        auto_line,
        "Freshness status lives in SYNC_STATUS.json and LAST_SYNC.txt.",
        "Includes Prisma, PC, Tablet, twin-kernel, docs, tooling, and evidence.",
        "Excludes node_modules, .next, builds, caches, logs, DBs, zips, env files, and heavy media.",
        "Source of truth remains F:\\repos\\hitech-os\\apps\\terminal-de-venta-system.",
        "Maintenance fallback: python F:\\repos\\hitech-os\\apps\\terminal-de-venta-system\\tooling\\scripts\\sync_chatgpt_share.py --sync",
    ]


def write_last_sync(status: dict[str, Any], destination: Path) -> None:
    freshness = "FRESH" if status["fresh"] else "STALE"
    reasons = "; ".join(status["stale_reasons"]) if status["stale_reasons"] else "none"
    lines = [
        "Terminal de Venta ChatGPT Share Sync Status",
        f"Freshness: {freshness}",
        f"Last successful sync UTC: {status.get('last_successful_sync_at') or 'never'}",
        f"Last checked UTC: {status['last_checked_at']}",
        f"Source root: {status['source_root']}",
        f"Files mirrored: {status['mirrored_file_count']} of {status['source_file_count']}",
        f"Auto-refresh task: {status['auto_refresh']['task_name']} installed={status['auto_refresh']['installed']}",
        f"Stale reasons: {reasons}",
        "Normal flow: open F:\\, right-click F:\\terminal_de_venta_chatgpt_share, compress to ZIP, upload.",
    ]
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_manifest(snapshot: dict[str, Any], status: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": status["last_checked_at"],
        "source_root": win(TERMINAL_ROOT),
        "share_root": win(SHARE_ROOT),
        "source_fingerprint": snapshot["fingerprint"],
        "normal_user_flow": status["normal_user_flow"],
        "included_dirs": [{"source": win(source), "destination": rel_text(destination)} for source, destination in INCLUDE_DIRS],
        "included_files": [{"source": win(source), "destination": rel_text(destination)} for source, destination in INCLUDE_FILES],
        "excluded_dir_names": sorted(EXCLUDED_DIR_NAMES),
        "excluded_file_names": sorted(EXCLUDED_FILE_NAMES),
        "excluded_suffixes": sorted(EXCLUDED_SUFFIXES),
        "max_file_bytes": MAX_FILE_BYTES,
        "files_copied": snapshot["file_count"] + len(ROOT_GENERATED_FILES),
        "bytes_copied": snapshot["byte_count"],
        "source_file_count": snapshot["file_count"],
        "skipped_count": snapshot["skipped_count"],
        "missing_count": snapshot["missing_count"],
        "missing": snapshot["missing"],
        "skipped": snapshot["skipped"],
        "freshness": {
            "fresh": status["fresh"],
            "sync_result": status["sync_result"],
            "stale_reasons": status["stale_reasons"],
            "last_successful_sync_at": status["last_successful_sync_at"],
        },
    }


def stage_content(snapshot: dict[str, Any], status: dict[str, Any]) -> set[Path]:
    reset_staging()
    staged_files: set[Path] = set()

    for record in snapshot["files"]:
        source = Path(record["source"])
        relative = Path(record["destination"])
        target = STAGING_ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        staged_files.add(relative)

    readme = STAGING_ROOT / "README.md"
    readme.write_text("\n".join(readme_lines(status["auto_refresh"]["installed"])) + "\n", encoding="utf-8")
    staged_files.add(Path("README.md"))

    manifest = build_manifest(snapshot, status)
    write_json(STAGING_ROOT / "SHARE_MANIFEST.json", manifest)
    staged_files.add(Path("SHARE_MANIFEST.json"))

    write_json(STAGING_ROOT / "SYNC_STATUS.json", status)
    staged_files.add(Path("SYNC_STATUS.json"))

    write_last_sync(status, STAGING_ROOT / "LAST_SYNC.txt")
    staged_files.add(Path("LAST_SYNC.txt"))

    return staged_files


def publish_staged(staged_files: set[Path]) -> None:
    root = guard_share_root()
    root.mkdir(parents=True, exist_ok=True)

    for relative in sorted(staged_files, key=lambda item: str(item).lower()):
        source = STAGING_ROOT / relative
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.replace(source, destination)

    expected = {rel_text(path).lower() for path in staged_files}
    for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        relative = path.relative_to(root)
        if path.is_file() and rel_text(relative).lower() not in expected:
            path.unlink()
        elif path.is_dir():
            try:
                next(path.iterdir())
            except StopIteration:
                path.rmdir()

    remove_staging()


def sync(*, background: bool = False) -> dict[str, Any]:
    handle = acquire_lock()
    try:
        snapshot = build_source_snapshot()
        task_override = True if background else None
        status = status_from_snapshot(snapshot, after_sync=True, task_installed_override=task_override)
        staged_files = stage_content(snapshot, status)
        publish_staged(staged_files)
        final_status = status_from_snapshot(snapshot, after_sync=True, task_installed_override=task_override)
        write_json(SHARE_ROOT / "SHARE_MANIFEST.json", build_manifest(snapshot, final_status))
        write_json(SHARE_ROOT / "SYNC_STATUS.json", final_status)
        write_last_sync(final_status, SHARE_ROOT / "LAST_SYNC.txt")
        return final_status
    except Exception as exc:
        try:
            snapshot = build_source_snapshot()
            failed_status = status_from_snapshot(
                snapshot,
                after_sync=False,
                sync_error=str(exc),
                task_installed_override=True if background else None,
            )
            SHARE_ROOT.mkdir(parents=True, exist_ok=True)
            write_json(SHARE_ROOT / "SYNC_STATUS.json", failed_status)
            write_last_sync(failed_status, SHARE_ROOT / "LAST_SYNC.txt")
        except Exception:
            pass
        raise
    finally:
        try:
            remove_staging()
        except Exception:
            pass
        release_lock(handle)


def update_status(*, background: bool = False) -> dict[str, Any]:
    snapshot = build_source_snapshot()
    status = status_from_snapshot(snapshot, after_sync=False, task_installed_override=True if background else None)
    SHARE_ROOT.mkdir(parents=True, exist_ok=True)
    write_json(SHARE_ROOT / "SYNC_STATUS.json", status)
    write_last_sync(status, SHARE_ROOT / "LAST_SYNC.txt")
    return status


def refresh_if_stale(*, background: bool = False) -> dict[str, Any]:
    snapshot = build_source_snapshot()
    status = status_from_snapshot(snapshot, after_sync=False, task_installed_override=True if background else None)
    if status["fresh"]:
        return status
    return sync(background=background)


def install_scheduled_task() -> dict[str, Any]:
    if not HIDDEN_LAUNCHER.exists():
        raise RuntimeError(f"Hidden launcher not found: {HIDDEN_LAUNCHER}")
    action = scheduled_task_action()
    result = run_subprocess(
        [
            "schtasks",
            "/Create",
            "/TN",
            TASK_NAME,
            "/SC",
            "MINUTE",
            "/MO",
            str(TASK_INTERVAL_MINUTES),
            "/TR",
            action,
            "/F",
        ],
    )
    settings_result = run_subprocess(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                "$settings = New-ScheduledTaskSettingsSet "
                "-AllowStartIfOnBatteries "
                "-DontStopIfGoingOnBatteries "
                "-StartWhenAvailable "
                "-MultipleInstances IgnoreNew; "
                f"Set-ScheduledTask -TaskName '{TASK_NAME}' -Settings $settings | Out-Null"
            ),
        ],
    )
    return {
        "task_name": TASK_NAME,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "installed": result.returncode == 0,
        "power_settings_applied": settings_result.returncode == 0,
        "settings_stdout": settings_result.stdout.strip(),
        "settings_stderr": settings_result.stderr.strip(),
        "command": action,
        "hidden_launcher": win(HIDDEN_LAUNCHER),
    }


def uninstall_scheduled_task() -> dict[str, Any]:
    result = run_subprocess(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
    )
    return {
        "task_name": TASK_NAME,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "deleted": result.returncode == 0,
    }


def summary(status: dict[str, Any]) -> dict[str, Any]:
    return {
        "share_root": status["share_root"],
        "sync_result": status["sync_result"],
        "fresh": status["fresh"],
        "stale_reasons": status["stale_reasons"],
        "last_successful_sync_at": status["last_successful_sync_at"],
        "source_file_count": status["source_file_count"],
        "mirrored_file_count": status["mirrored_file_count"],
        "share_file_count": status["share_file_count"],
        "junk_directories_found": status["junk_directories_found"],
        "junk_files_found": status["junk_files_found"],
        "reparse_points_found": status["reparse_points_found"],
        "auto_refresh_installed": status["auto_refresh"]["installed"],
    }


def print_payload(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    for key, value in payload.items():
        print(f"{key}: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refresh and verify the physical ChatGPT share surface at F:\\terminal_de_venta_chatgpt_share."
    )
    parser.add_argument("--sync", action="store_true", help="Refresh the physical share folder now.")
    parser.add_argument("--status", action="store_true", help="Update freshness markers without refreshing source files.")
    parser.add_argument("--refresh-if-stale", action="store_true", help="Refresh only when the source fingerprint changed.")
    parser.add_argument("--install-scheduled-task", action="store_true", help="Install the Windows auto-refresh scheduled task.")
    parser.add_argument("--uninstall-scheduled-task", action="store_true", help="Remove the Windows auto-refresh scheduled task.")
    parser.add_argument("--task-status", action="store_true", help="Report Windows scheduled task status.")
    parser.add_argument("--background", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--quiet", action="store_true", help="Suppress normal output.")
    args = parser.parse_args()

    try:
        if args.install_scheduled_task:
            payload = install_scheduled_task()
        elif args.uninstall_scheduled_task:
            payload = uninstall_scheduled_task()
        elif args.task_status:
            payload = task_query()
        elif args.status:
            payload = summary(update_status(background=args.background))
        elif args.refresh_if_stale:
            payload = summary(refresh_if_stale(background=args.background))
        else:
            payload = summary(sync(background=args.background))
    except Exception as exc:
        payload = {"sync_result": "FAIL", "error": str(exc), "share_root": win(SHARE_ROOT)}
        if not args.quiet:
            print_payload(payload, args.json)
        return 1

    if not args.quiet:
        print_payload(payload, args.json)
    return 0 if payload.get("sync_result", "PASS") != "FAIL" and payload.get("returncode", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
