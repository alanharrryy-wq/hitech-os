from __future__ import annotations

import argparse
import filecmp
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

STATE_DIRNAME = ".ark_install"
STATE_FILE = "last_apply.json"
IGNORED_PAYLOAD_PARTS = {STATE_DIRNAME, "__pycache__", "reports", "reports_real"}
IGNORED_PAYLOAD_SUFFIXES = {".pyc", ".pyo"}


def should_include_in_payload(relative: Path) -> bool:
    return not any(
        part in IGNORED_PAYLOAD_PARTS for part in relative.parts
    ) and relative.suffix not in IGNORED_PAYLOAD_SUFFIXES


@dataclass
class Change:
    source: str
    target: str
    action: str


@dataclass
class InstallPlan:
    root: str
    payload: str
    backup_dir: str
    state_file: str
    log_file: str
    changes: list[Change]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Controlled installer for Ar-k governed integration")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--rollback", action="store_true")
    parser.add_argument("--root", required=True, help="Absolute project root")
    parser.add_argument("--payload", required=True, help="ZIP payload path rooted at the project tree or wrapped in a single top-level folder")
    parser.add_argument(
        "--log-dir",
        default=r"F:\descargasf",
        help="Directory for the single main integration log",
    )
    return parser.parse_args()


def resolve_root(value: str) -> Path:
    root = Path(value).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def resolve_payload(value: str) -> Path:
    payload = Path(value).expanduser().resolve()
    if not payload.exists():
        raise FileNotFoundError(f"Payload not found: {payload}")
    return payload


def build_log_file(log_dir: Path) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%y%m%d_%H%M")
    return log_dir / f"Ar-k_int_{stamp}.log"


def configure_logging(log_file: Path) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
    )


def extract_payload(payload_zip: Path) -> Path:
    workdir = Path(tempfile.mkdtemp(prefix="ark_payload_"))
    with zipfile.ZipFile(payload_zip, "r") as zip_file:
        zip_file.extractall(workdir)
    return workdir


def resolve_payload_root(extracted_root: Path) -> Path:
    entries = sorted(extracted_root.iterdir(), key=lambda item: item.name)
    directories = [entry for entry in entries if entry.is_dir()]
    files = [entry for entry in entries if entry.is_file()]
    if len(directories) == 1 and not files:
        return directories[0]
    return extracted_root


def compare_files(source: Path, target: Path) -> bool:
    return target.exists() and filecmp.cmp(source, target, shallow=False)


def plan_changes(root: Path, payload_zip: Path, log_dir: Path) -> tuple[InstallPlan, Path]:
    extracted = extract_payload(payload_zip)
    payload_root = resolve_payload_root(extracted)
    changes: list[Change] = []
    for source in sorted(path for path in payload_root.rglob("*") if path.is_file()):
        relative = source.relative_to(payload_root)
        if not should_include_in_payload(relative):
            continue
        target = root / relative
        if compare_files(source, target):
            action = "skip"
        elif target.exists():
            action = "replace"
        else:
            action = "create"
        changes.append(Change(source=str(source), target=str(target), action=action))
    state_dir = root / STATE_DIRNAME
    backup_dir = state_dir / "backups" / datetime.now().strftime("%y%m%d_%H%M%S")
    log_file = build_log_file(log_dir)
    state_file = state_dir / STATE_FILE
    plan = InstallPlan(
        root=str(root),
        payload=str(payload_zip),
        backup_dir=str(backup_dir),
        state_file=str(state_file),
        log_file=str(log_file),
        changes=changes,
    )
    return plan, extracted


def print_plan(plan: InstallPlan) -> None:
    payload = {
        "root": plan.root,
        "payload": plan.payload,
        "backup_dir": plan.backup_dir,
        "state_file": plan.state_file,
        "log_file": plan.log_file,
        "changes": [asdict(change) for change in plan.changes],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


def create_backup(plan: InstallPlan) -> dict[str, list[str]]:
    backup_dir = Path(plan.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    replaced: list[str] = []
    created: list[str] = []
    skipped: list[str] = []
    cleanup_paths: list[str] = []
    root = Path(plan.root)
    if not (root / "reports").exists():
        cleanup_paths.append(str(root / "reports"))
    if not (root / "reports_real").exists():
        cleanup_paths.append(str(root / "reports_real"))
    for change in plan.changes:
        target = Path(change.target)
        if change.action == "replace":
            replaced.append(change.target)
            backup_target = backup_dir / target.relative_to(plan.root)
            backup_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup_target)
            logging.info("Backed up %s -> %s", target, backup_target)
        elif change.action == "create":
            created.append(change.target)
        else:
            skipped.append(change.target)
    state = {
        "root": plan.root,
        "backup_dir": plan.backup_dir,
        "payload": plan.payload,
        "replaced": replaced,
        "created": created,
        "skipped": skipped,
        "cleanup_paths": cleanup_paths,
    }
    state_path = Path(plan.state_file)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return state


def apply_changes(plan: InstallPlan) -> None:
    for change in plan.changes:
        if change.action == "skip":
            logging.info("Skipped unchanged file %s", change.target)
            continue
        source = Path(change.source)
        target = Path(change.target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        logging.info("Applied %s -> %s [%s]", source, target, change.action)


def verify_files(plan: InstallPlan) -> bool:
    ok = True
    for change in plan.changes:
        if change.action == "skip":
            continue
        if not Path(change.target).exists():
            logging.error("Missing file after install: %s", change.target)
            ok = False
    return ok


def run_validation_commands(root: Path) -> bool:
    commands = [
        [sys.executable, "-m", "compileall", str(root / "pya")],
        [sys.executable, "-m", "pya.tools.pya", "doctor", "--root", str(root)],
        [
            sys.executable,
            "-m",
            "pya.tools.pya",
            "run",
            "--root",
            str(root),
            "--target",
            str(root / "examples" / "sample_app"),
            "--out",
            str(root / "reports"),
        ],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root)
    all_ok = True
    for command in commands:
        logging.info("Running validation command: %s", " ".join(command))
        completed = subprocess.run(command, cwd=str(root), env=env, capture_output=True, text=True, check=False)
        logging.info("STDOUT:\n%s", completed.stdout)
        if completed.stderr:
            logging.info("STDERR:\n%s", completed.stderr)
        if completed.returncode != 0:
            logging.error("Validation command failed with code %s", completed.returncode)
            all_ok = False
            break
    return all_ok


def verify_installation(plan: InstallPlan) -> bool:
    root = Path(plan.root)
    required_files = [
        root / "README.md",
        root / "pya" / "system" / "root_manifest.py",
        root / "pya" / "kernel" / "pipeline.py",
        root / "pya" / "contracts" / "contract_registry.py",
        root / "pya" / "engines" / "scanner" / "manifest.json",
        root / "docs" / "parallel_development_guide.md",
    ]
    ok = verify_files(plan)
    for path in required_files:
        if not path.exists():
            logging.error("Required file missing: %s", path)
            ok = False
    if not ok:
        return False
    return run_validation_commands(root)


def load_state(root: Path) -> dict[str, object]:
    state_file = root / STATE_DIRNAME / STATE_FILE
    if not state_file.exists():
        raise FileNotFoundError(f"No rollback state found at {state_file}")
    return json.loads(state_file.read_text(encoding="utf-8"))


def rollback(root: Path) -> None:
    state = load_state(root)
    backup_dir = Path(state["backup_dir"])
    for target_str in state.get("created", []):
        target = Path(target_str)
        if target.exists():
            target.unlink()
            logging.info("Removed created file %s", target)
    for target_str in state.get("replaced", []):
        target = Path(target_str)
        backup_source = backup_dir / target.relative_to(root)
        if backup_source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_source, target)
            logging.info("Restored backup %s -> %s", backup_source, target)
    for cleanup_str in state.get("cleanup_paths", []):
        cleanup_path = Path(cleanup_str)
        if cleanup_path.exists():
            shutil.rmtree(cleanup_path, ignore_errors=True)
            logging.info("Removed cleanup path %s", cleanup_path)
    for pycache in root.rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)
        logging.info("Removed cache directory %s", pycache)
    logging.info("Rollback complete")


def main() -> int:
    args = parse_args()
    root = resolve_root(args.root)
    payload = resolve_payload(args.payload)
    log_dir = Path(args.log_dir).expanduser().resolve()
    plan, extracted = plan_changes(root, payload, log_dir)
    configure_logging(Path(plan.log_file))
    logging.info("Mode selected")
    logging.info("Resolved root=%s payload=%s", root, payload)
    print_plan(plan)

    try:
        if args.dry_run:
            logging.info("Dry-run complete")
            return 0
        if args.apply:
            create_backup(plan)
            try:
                apply_changes(plan)
                if not verify_installation(plan):
                    logging.error("Verification failed after apply; starting automatic rollback")
                    rollback(root)
                    return 2
                logging.info("Apply and verify complete")
                return 0
            except Exception:
                logging.exception("Apply failed; starting automatic rollback")
                rollback(root)
                return 1
        if args.verify:
            return 0 if verify_installation(plan) else 2
        if args.rollback:
            rollback(root)
            return 0
        return 1
    finally:
        shutil.rmtree(extracted, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
