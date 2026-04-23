from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
from datetime import datetime
from pathlib import Path
from typing import Any

THIS_FILE = Path(__file__).resolve()
BUNDLE_ROOT = THIS_FILE.parent
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

from payload_manifest import (
    DEFAULT_INSTALL_REL,
    DEFAULT_LOG_DIR,
    LOG_FILE_PREFIX,
    ROLLBACK_STATE_REL,
    STATE_REL,
    STATUS_READY,
    TOP_LEVEL_DIR,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Self-contained installer for ark_registry_builder_bundle.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--rollback", action="store_true")
    parser.add_argument("--root", required=True, help="Explicit Ar-k root. Required to avoid implicit cwd installs.")
    parser.add_argument("--log-dir", default=DEFAULT_LOG_DIR)
    parser.add_argument("--install-rel", default=DEFAULT_INSTALL_REL)
    return parser


def now_stamp() -> tuple[str, str]:
    now = datetime.now()
    return now.strftime("%y%m%d_%H%M"), now.isoformat(timespec="seconds")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def make_log_path(log_dir: Path) -> Path:
    stamp, _ = now_stamp()
    return ensure_dir(log_dir) / f"{LOG_FILE_PREFIX}{stamp}.log"


def write_log(log_path: Path, lines: list[str]) -> None:
    ensure_dir(log_path.parent)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def installed_tree(root: Path, install_rel: str) -> Path:
    return root / install_rel


def state_root(root: Path) -> Path:
    return root / STATE_REL


def rollback_state_path(root: Path) -> Path:
    return root / ROLLBACK_STATE_REL


def copy_bundle(source_root: Path, target_root: Path) -> None:
    if target_root.exists():
        shutil.rmtree(target_root)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
    shutil.copytree(source_root, target_root, ignore=ignore)


def backup_existing_install(target_root: Path, root: Path) -> Path | None:
    if not target_root.exists():
        return None
    stamp, _ = now_stamp()
    backup_root = ensure_dir(state_root(root) / "backups" / stamp)
    backup_target = backup_root / target_root.name
    shutil.copytree(target_root, backup_target)
    return backup_target


def write_last_apply(root: Path, target_root: Path, backup_path: Path | None) -> Path:
    state_file = rollback_state_path(root)
    ensure_dir(state_file.parent)
    payload = {
        "installed_at": datetime.now().isoformat(timespec="seconds"),
        "bundle_root_name": TOP_LEVEL_DIR,
        "install_root": str(target_root),
        "backup_path": str(backup_path) if backup_path else None,
        "status": STATUS_READY,
    }
    state_file.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return state_file


def verify_install(root: Path, install_rel: str, log_lines: list[str]) -> dict[str, Any]:
    target_root = installed_tree(root, install_rel)
    if not target_root.exists():
        return {"ok": False, "reason": "install_root_missing", "install_root": str(target_root)}
    validate_cmd = [
        sys.executable,
        str(target_root / "tools" / "validate_registry_builder_bundle.py"),
        "--bundle-root",
        str(target_root),
    ]
    validate_text = subprocess.check_output(validate_cmd, text=True)
    validate_result = json.loads(validate_text)
    examples_dir = state_root(root) / "verify_examples"
    generate_cmd = [
        sys.executable,
        str(target_root / "tools" / "generate_example_outputs.py"),
        "--output-dir",
        str(examples_dir),
        "--limit",
        "4",
    ]
    generate_text = subprocess.check_output(generate_cmd, text=True)
    log_lines.append("VALIDATE=" + validate_text.strip())
    log_lines.append("GENERATE=" + generate_text.strip())
    return {"ok": bool(validate_result.get("ok")), "validation": validate_result, "examples_dir": str(examples_dir)}


def rollback(root: Path, install_rel: str) -> dict[str, Any]:
    state_file = rollback_state_path(root)
    if not state_file.exists():
        return {"ok": False, "reason": "missing_last_apply"}
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    backup_path = payload.get("backup_path")
    target_root = installed_tree(root, install_rel)
    if not backup_path:
        if target_root.exists():
            shutil.rmtree(target_root)
        return {"ok": True, "restored": None, "removed_install_root": True}
    backup_root = Path(backup_path)
    if not backup_root.exists():
        return {"ok": False, "reason": "backup_missing", "backup_path": backup_path}
    if target_root.exists():
        shutil.rmtree(target_root)
    shutil.copytree(backup_root, target_root)
    return {"ok": True, "restored": str(target_root)}


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    root = Path(args.root).resolve()
    install_rel = args.install_rel.replace("\\", "/")
    log_path = make_log_path(Path(args.log_dir))
    target_root = installed_tree(root, install_rel)
    mode_name = "dry-run" if args.dry_run else "apply" if args.apply else "verify" if args.verify else "rollback"
    lines = [
        f"STATUS={STATUS_READY}",
        f"MODE={mode_name}",
        f"ROOT={root}",
        f"INSTALL_ROOT={target_root}",
        f"STATE_ROOT={state_root(root)}",
        f"ROLLBACK_STATE={rollback_state_path(root)}",
        f"SOURCE_ROOT={BUNDLE_ROOT}",
    ]
    if args.dry_run:
        backup_preview = state_root(root) / "backups" / now_stamp()[0]
        lines.append(f"DRY_RUN_BACKUP_PREVIEW={backup_preview}")
        lines.append("RESULT=DRY_RUN_OK")
        write_log(log_path, lines)
        print(json.dumps({"ok": True, "mode": "dry-run", "install_root": str(target_root), "log": str(log_path)}, indent=2))
        return 0
    if args.apply:
        ensure_dir(state_root(root))
        backup_path = backup_existing_install(target_root, root)
        copy_bundle(BUNDLE_ROOT, target_root)
        state_file = write_last_apply(root, target_root, backup_path)
        lines.append(f"BACKUP_PATH={backup_path}")
        lines.append(f"LAST_APPLY={state_file}")
        verify_result = verify_install(root, install_rel, lines)
        lines.append("VERIFY_RESULT=" + json.dumps(verify_result, sort_keys=True))
        if not verify_result.get("ok"):
            rollback_result = rollback(root, install_rel)
            lines.append("AUTO_ROLLBACK=" + json.dumps(rollback_result, sort_keys=True))
            write_log(log_path, lines)
            print(json.dumps({"ok": False, "mode": "apply", "verify": verify_result, "rollback": rollback_result, "log": str(log_path)}, indent=2))
            return 1
        lines.append("RESULT=APPLY_OK")
        write_log(log_path, lines)
        print(json.dumps({"ok": True, "mode": "apply", "install_root": str(target_root), "log": str(log_path), "verify": verify_result}, indent=2))
        return 0
    if args.verify:
        result = verify_install(root, install_rel, lines)
        lines.append("RESULT=" + ("VERIFY_OK" if result.get("ok") else "VERIFY_FAIL"))
        write_log(log_path, lines)
        print(json.dumps({"mode": "verify", "log": str(log_path), **result}, indent=2))
        return 0 if result.get("ok") else 1
    rollback_result = rollback(root, install_rel)
    lines.append("ROLLBACK_RESULT=" + json.dumps(rollback_result, sort_keys=True))
    lines.append("RESULT=" + ("ROLLBACK_OK" if rollback_result.get("ok") else "ROLLBACK_FAIL"))
    write_log(log_path, lines)
    print(json.dumps({"mode": "rollback", "log": str(log_path), **rollback_result}, indent=2))
    return 0 if rollback_result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
