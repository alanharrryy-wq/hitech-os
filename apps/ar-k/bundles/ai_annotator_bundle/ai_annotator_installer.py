from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from core.bundle_constants import (
    DEFAULT_INSTALL_REL,
    DEFAULT_LOG_DIR,
    DEFAULT_STATE_REL,
    LOG_FILENAME_PATTERN,
    ROLLBACK_STATE_FILE,
    TOP_LEVEL_DIR,
)
from core.example_builder import generate_outputs
from core.log_utils import default_log_path, timestamp_token
from core.manifest_utils import sha256_path
from core.write_limits import assert_example_output_dir, assert_only_annotation_artifacts, explain_write_limit
import payload_manifest
from tools.validate_ai_annotator_bundle import validate_bundle_dir

DEFAULT_INSTALL_REL = DEFAULT_INSTALL_REL
DEFAULT_STATE_REL = DEFAULT_STATE_REL
LOG_FILENAME_PATTERN = LOG_FILENAME_PATTERN


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--rollback", action="store_true")
    parser.add_argument("--root", required=True)
    parser.add_argument("--log-dir", required=False, default=DEFAULT_LOG_DIR)
    parser.add_argument("--install-rel", required=False, default=DEFAULT_INSTALL_REL)
    return parser


class InstallerRuntime:
    def __init__(self, root: Path, log_dir: Path, install_rel: str) -> None:
        self.root = root.resolve()
        self.log_dir = log_dir
        self.install_root = (self.root / install_rel).resolve()
        self.state_root = (self.root / DEFAULT_STATE_REL).resolve()
        self.rollback_file = (self.root / ROLLBACK_STATE_FILE).resolve()
        self.timestamp = timestamp_token()
        self.backup_root = self.state_root / "backups" / self.timestamp
        self.log_path = default_log_path(log_dir)

    def summary(self) -> dict[str, str]:
        return {
            "root": str(self.root),
            "install_root": str(self.install_root),
            "state_root": str(self.state_root),
            "rollback_file": str(self.rollback_file),
            "backup_root": str(self.backup_root),
            "log_path": str(self.log_path),
        }


def _write_log(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def _bundle_source_dir() -> Path:
    return THIS_DIR


def _bundle_file_rows(source_dir: Path) -> list[dict[str, object]]:
    rows = []
    for rel, expected in payload_manifest.PAYLOAD_MANIFEST.items():
        path = source_dir / rel
        if not path.exists():
            raise FileNotFoundError(f"Manifest file missing in source bundle: {rel}")
        rows.append(
            {
                "relative_path": rel,
                "sha256": sha256_path(path),
                "expected_sha256": expected["sha256"],
                "size": path.stat().st_size,
            }
        )
    return rows


def do_dry_run(runtime: InstallerRuntime) -> dict[str, object]:
    source_dir = _bundle_source_dir()
    validate_bundle_dir(source_dir)
    rows = _bundle_file_rows(source_dir)
    return {
        "mode": "dry-run",
        "runtime": runtime.summary(),
        "file_count": len(rows),
        "write_limits": explain_write_limit(),
        "actions": [
            f"would validate source bundle at {source_dir}",
            f"would install bundle into {runtime.install_root}",
            f"would persist rollback state at {runtime.rollback_file}",
            f"would keep backups under {runtime.backup_root}",
        ],
    }


def do_apply(runtime: InstallerRuntime) -> dict[str, object]:
    source_dir = _bundle_source_dir()
    validate_bundle_dir(source_dir)
    runtime.state_root.mkdir(parents=True, exist_ok=True)
    backup_made = False
    previous_install = runtime.install_root.exists()
    if previous_install:
        runtime.backup_root.parent.mkdir(parents=True, exist_ok=True)
        _copy_tree(runtime.install_root, runtime.backup_root)
        backup_made = True
    runtime.install_root.parent.mkdir(parents=True, exist_ok=True)
    _copy_tree(source_dir, runtime.install_root)
    payload_rows = _bundle_file_rows(runtime.install_root)
    state = {
        "applied_at": datetime.now().isoformat(),
        "install_root": str(runtime.install_root),
        "state_root": str(runtime.state_root),
        "backup_root": str(runtime.backup_root) if backup_made else None,
        "source_dir": str(source_dir),
        "manifest_size": len(payload_rows),
        "files": payload_rows,
    }
    runtime.rollback_file.parent.mkdir(parents=True, exist_ok=True)
    runtime.rollback_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return {
        "mode": "apply",
        "runtime": runtime.summary(),
        "backup_created": backup_made,
        "installed_files": len(payload_rows),
    }


def do_verify(runtime: InstallerRuntime) -> dict[str, object]:
    validate_bundle_dir(_bundle_source_dir())
    if not runtime.install_root.exists():
        raise RuntimeError(f"Install root does not exist: {runtime.install_root}")
    missing: list[str] = []
    mismatched: list[str] = []
    for rel, expected in payload_manifest.PAYLOAD_MANIFEST.items():
        if rel == "payload_manifest.py":
            continue
        path = runtime.install_root / rel
        if not path.exists():
            missing.append(rel)
            continue
        actual = sha256_path(path)
        if actual != expected["sha256"]:
            mismatched.append(rel)
    if missing or mismatched:
        raise RuntimeError(
            f"Installed bundle drift detected. missing={missing!r} hash_mismatches={mismatched!r}"
        )
    example_dir = runtime.state_root / "verification_outputs" / runtime.timestamp
    assert_example_output_dir(example_dir, runtime.root)
    summary = generate_outputs(example_dir, limit=18)
    assert_only_annotation_artifacts(example_dir.glob('*.json'))
    return {
        "mode": "verify",
        "runtime": runtime.summary(),
        "missing_files": missing,
        "hash_mismatches": mismatched,
        "example_output_dir": str(example_dir),
        "example_summary": summary,
    }


def do_rollback(runtime: InstallerRuntime) -> dict[str, object]:
    if not runtime.rollback_file.exists():
        raise RuntimeError(f"Rollback state file not found: {runtime.rollback_file}")
    state = json.loads(runtime.rollback_file.read_text(encoding="utf-8"))
    install_root = Path(state["install_root"])
    backup_root = Path(state["backup_root"]) if state.get("backup_root") else None
    if install_root.exists():
        shutil.rmtree(install_root)
    if backup_root and backup_root.exists():
        install_root.parent.mkdir(parents=True, exist_ok=True)
        _copy_tree(backup_root, install_root)
    return {
        "mode": "rollback",
        "runtime": runtime.summary(),
        "restored_backup": bool(backup_root and backup_root.exists()),
    }


def main(argv: list[str] | None = None) -> int:
    ns = build_parser().parse_args(argv)
    runtime = InstallerRuntime(Path(ns.root), Path(ns.log_dir), ns.install_rel)
    lines = [f"bundle={TOP_LEVEL_DIR}", f"runtime={json.dumps(runtime.summary(), sort_keys=True)}"]
    if ns.dry_run:
        result = do_dry_run(runtime)
    elif ns.apply:
        result = do_apply(runtime)
    elif ns.verify:
        result = do_verify(runtime)
    else:
        result = do_rollback(runtime)
    lines.append(json.dumps(result, indent=2, sort_keys=True))
    _write_log(runtime.log_path, lines)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
